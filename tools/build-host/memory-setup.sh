#!/bin/bash
# Keep the desktop responsive under heavy builds (run once with sudo).
#
#  1. zram: zstd, sized to RAM (~2-3x compression, so ~60+ GB effective)
#  2. 16 GB btrfs swapfile as a lower-priority fallback behind zram
#  3. VM tuning for zram-first swapping (Fedora / ChromeOS recommendations)
#  4. systemd-oomd also watches machine.slice (mock/nspawn builds) and kills
#     there first, at lower pressure than the desktop
#
# Undo: sudo ./memory-setup.sh --undo
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }

if [ "${1:-}" = "--undo" ]; then
    swapoff /var/swap/swapfile 2>/dev/null || :
    sed -i '\|/var/swap/swapfile|d' /etc/fstab
    rm -rf /var/swap
    rm -f /etc/systemd/zram-generator.conf /etc/sysctl.d/99-zram-desktop.conf \
          /etc/systemd/system/machine.slice.d/50-oomd.conf
    systemctl daemon-reload; sysctl --system >/dev/null
    echo "undone; reboot to get the default zram back"; exit 0
fi

# 1. zram
cat > /etc/systemd/zram-generator.conf <<'EOF'
# Local override (memory-setup.sh): zstd compresses ~3x on build/desktop data
[zram0]
zram-size = ram
compression-algorithm = zstd
swap-priority = 100
EOF

# 2. swapfile (btrfs needs a NOCOW file; mkswapfile handles it)
if [ ! -f /var/swap/swapfile ]; then
    btrfs subvolume create /var/swap
    btrfs filesystem mkswapfile --size 16g /var/swap/swapfile
fi
grep -q '/var/swap/swapfile' /etc/fstab ||
    echo '/var/swap/swapfile none swap defaults,pri=10 0 0' >> /etc/fstab

# 3. sysctl
cat > /etc/sysctl.d/99-zram-desktop.conf <<'EOF'
# zram is far cheaper than eviction: swap early, one page at a time
vm.swappiness = 180
vm.page-cluster = 0
vm.watermark_boost_factor = 0
# keep more free memory so allocations don't stall in direct reclaim
vm.watermark_scale_factor = 125
EOF

# 4. oomd for builds
mkdir -p /etc/systemd/system/machine.slice.d
cat > /etc/systemd/system/machine.slice.d/50-oomd.conf <<'EOF'
# mock/nspawn builds: killed by systemd-oomd before the desktop suffers
[Slice]
ManagedOOMMemoryPressure=kill
ManagedOOMMemoryPressureLimit=40%
ManagedOOMMemoryPressureDurationSec=10s
ManagedOOMSwap=kill
EOF

systemctl daemon-reload
sysctl --system >/dev/null
systemctl restart systemd-oomd
swapoff /dev/zram0 2>/dev/null || :
systemctl restart systemd-zram-setup@zram0.service
swapon -a
echo "== result"
zramctl; swapon --show; sysctl vm.swappiness vm.page-cluster
oomctl | grep -A1 'machine.slice' || echo "(machine.slice appears in oomctl once a build runs)"

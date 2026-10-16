#!/usr/bin/env python3
"""Once a second: who uses the GPU, the NPU and the unified memory.

Per process (DRM fdinfo, own processes only): GPU memory (drm-total-gtt +
drm-total-system) and the share of render/compute engine time since the last
sample. System wide: MemAvailable, the kernel's GPUActive/GPUReclaim, NPU busy
percentage and memory, CPU load. Read only, needs no root.

Usage: python3 ai-load-monitor.py [seconds] [--csv out.csv]
"""
import glob
import os
import sys
import time

NPU = "/sys/class/accel/accel0/device"
ENGINES = ("rcs", "ccs")


def meminfo():
    out = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":", 1)
        out[k] = int(v.split()[0])
    return out


def kib(v):
    n, unit = v.split()[0], v.split()[1] if len(v.split()) > 1 else ""
    return int(n) * {"KiB": 1, "MiB": 1024, "GiB": 1048576}.get(unit, 1 / 1024)


def drm_clients():
    """pid -> (name, gpu memory KiB, {engine: (busy cycles, total cycles)})"""
    seen, out = set(), {}
    for fd in glob.glob("/proc/[0-9]*/fdinfo/*"):
        try:
            text = open(fd).read()
        except OSError:
            continue
        if "drm-client-id" not in text:
            continue
        pid = int(fd.split("/")[2])
        fields = dict(l.split(":", 1) for l in text.splitlines() if ":" in l)
        cid = (fields.get("drm-pdev", "").strip(), fields["drm-client-id"].strip())
        if cid in seen:
            continue
        seen.add(cid)
        name, mem, eng = out.get(pid, (open(f"/proc/{pid}/comm").read().strip(), 0, {}))
        for region in ("gtt", "system"):
            v = fields.get(f"drm-total-{region}")
            if v:
                mem += kib(v.strip())
        for e in ENGINES:
            b, t = fields.get(f"drm-cycles-{e}"), fields.get(f"drm-total-cycles-{e}")
            if b and t:
                pb, pt = eng.get(e, (0, 0))
                eng[e] = (pb + int(b), max(pt, int(t)))
        out[pid] = (name, mem, eng)
    return out


def npu():
    try:
        return int(open(f"{NPU}/npu_busy_time_us").read()), int(open(f"{NPU}/npu_memory_utilization").read())
    except OSError:
        return 0, 0


def cpu():
    v = list(map(int, open("/proc/stat").readline().split()[1:]))
    return sum(v), v[3] + v[4]


def main():
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 60
    csv = open(sys.argv[sys.argv.index("--csv") + 1], "w") if "--csv" in sys.argv else None
    if csv:
        csv.write("t,mem_avail_gb,gpu_active_gb,gpu_reclaim_gb,npu_busy_pct,npu_mem_mb,cpu_pct,top_gpu\n")
    prev, pnpu, pcpu, pt = drm_clients(), npu(), cpu(), time.monotonic()
    for i in range(seconds):
        time.sleep(1)
        cur, cnpu, ccpu, ct = drm_clients(), npu(), cpu(), time.monotonic()
        m = meminfo()
        rows = []
        for pid, (name, mem, eng) in cur.items():
            busy = 0.0
            for e, (b, t) in eng.items():
                pb, ptot = prev.get(pid, ("", 0, {}))[2].get(e, (b, t))
                if t > ptot:
                    busy = max(busy, 100.0 * (b - pb) / (t - ptot))
            rows.append((busy, mem, name))
        rows.sort(reverse=True)
        npu_pct = 100.0 * (cnpu[0] - pnpu[0]) / ((ct - pt) * 1e6)
        cpu_pct = 100.0 * (1 - (ccpu[1] - pcpu[1]) / max(ccpu[0] - pcpu[0], 1))
        top = "  ".join(f"{n}:{b:.0f}%/{mem / 1048576:.1f}G" for b, mem, n in rows[:4] if b >= 1 or mem > 262144)
        line = (f"{i + 1:4d}s  RAM avail {m['MemAvailable'] / 1048576:5.1f}G  GPU mem {m.get('GPUActive', 0) / 1048576:5.1f}G"
                f" (+{m.get('GPUReclaim', 0) / 1048576:.1f}G pool)  NPU {npu_pct:3.0f}% {cnpu[1] / 1e6:5.0f}MB  CPU {cpu_pct:3.0f}%  | {top}")
        print(line, flush=True)
        if csv:
            csv.write(f"{i + 1},{m['MemAvailable'] / 1048576:.2f},{m.get('GPUActive', 0) / 1048576:.2f},"
                      f"{m.get('GPUReclaim', 0) / 1048576:.2f},{npu_pct:.1f},{cnpu[1] / 1e6:.0f},{cpu_pct:.1f},\"{top}\"\n")
        prev, pnpu, pcpu, pt = cur, cnpu, ccpu, ct


if __name__ == "__main__":
    main()

# Copilot key as an app launcher (KDE)

The Copilot key sends `KEY_LEFTMETA + KEY_LEFTSHIFT + KEY_F23` (libinput).
Fedora's xkeyboard-config 2.48 gives `<FK23>` the type `PC_SHIFT_SUPER_LEVEL2`
(`[ XF86TouchpadOff/F23, XF86Assistant ]`), so Shift+Super+F23 becomes
`XF86Assistant`. Qt 6.11 has no key for it (`Key_unknown`), so KDE can neither
record nor match it ("Meta+Shift" only in System Settings).

Fix: input-remapper turns F23 into F19 (plain, single-level, unused) before
xkb, and KDE binds Meta+Shift+F19.

```bash
mkdir -p "$HOME/.config/input-remapper-2/presets/AT Translated Set 2 keyboard"
cp config.json ~/.config/input-remapper-2/
cp copilot.json "$HOME/.config/input-remapper-2/presets/AT Translated Set 2 keyboard/"
sudo systemctl enable --now input-remapper
input-remapper-control --command autoload
```
Then System Settings, Keyboard, Shortcuts, pick the app and press the Copilot key
(records Meta+Shift+F19).

Don't use the xkb option `fkeys:basic_13-24` instead: it also turns F20
(MicMute) and F21/F22 (touchpad) into plain F-keys.

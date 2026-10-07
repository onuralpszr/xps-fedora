# xps-ptl-tools

## xps-ptl-autobrightness

Ambient-light auto-brightness for KDE Plasma. PowerDevil has no ambient light support, so this user service reads the light sensor from iio-sensor-proxy and sets the internal display through KDE's `org.kde.ScreenBrightness`.

- Follows a log-lux curve with smoothing, hysteresis and short fades.
- Learns your preference: adjust brightness yourself and after 10 s it keeps that offset as the light changes (saved across logins).
- Pauses during KDE idle dimming.

Enable per user (not enabled automatically):

    systemctl --user enable --now xps-ptl-autobrightness

Control: the **Auto Brightness** Plasma widget (switch, live lux/brightness, learned preference + reset, optional OSD), or

    systemctl --user disable --now xps-ptl-autobrightness   # off for good
    xps-ptl-autobrightness --debug                          # run in a terminal

D-Bus: `org.xpsptl.AutoBrightness` (see the script header). Config: `/etc/xps-ptl/autobrightness.conf`, `~/.config/xps-ptl/autobrightness.conf`.

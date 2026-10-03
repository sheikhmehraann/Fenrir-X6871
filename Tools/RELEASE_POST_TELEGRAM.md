Fenrir for Infinix GT 20 Pro (X6871)

Initial release for Android 14 and Android 15.

Key Features:
- Passes Strong Play Integrity on custom kernels and recoveries without extra modules
- Spoofs bootloader state as locked to Android userspace
- Fastboot getvar unlocked returns "no"
- Stock VBMeta remains enabled without verification failures
- Volume Down boots directly into Fastboot mode, bypassing factory test screens
- Unlocks full fastboot and OEM command set
- 10-minute USB fastboot session timeout

Supported Firmware Builds:
- Android 15: X6871-15.1.2.165SP05(OP001PF001AZ) and X6871-15.1.2.180SP05(OP001PF001AZ)
- Android 14: X6871-H962CF-U-OP-250217V2673
- Ported and GSI ROMs are supported

Installation:
1. Boot to OrangeFox Recovery or TWRP
2. Flash the Fenrir recovery zip for your Android version
3. Format Data (mandatory on first install due to key derivation changes)
4. Reboot system

Credits:
- R0rt1z2 (upstream Fenrir framework)
- ramabondanp
- mehraann19

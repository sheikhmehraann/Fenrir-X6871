# 🐺 Fenrir v1.0.0 — Infinix GT 20 Pro (X6871)

> [!CAUTION]
> **THIS IS ONLY FOR THE INFINIX GT 20 PRO (`X6871`) POWERED BY MEDIATEK DIMENSITY 8200 ULTIMATE.**  
> Flashing bootloader binaries from another device will brick your phone. Proceed with caution and verify your build version.

---

### ⚠️ Firmware Compatibility Notes
- **Android 15 (`XOS 15`)**: Tested & verified on `X6871-15.1.2.165SP05(OP001PF001AZ)` and `X6871-15.1.2.180SP05(OP001PF001AZ)`.
- **Android 14 (`XOS 14`)**: Strictly compatible with `X6871-H962CF-U-OP-250217V2673`. Do not attempt to cross-flash across different A14 builds.

---

### ✨ Features & Improvements
- 🟢 **Strong / Green Play Integrity**: Grants Green verified boot state without needing Play Integrity Fix (PIF) modules or Magisk hide workarounds.
- 🔒 **Stealth Locked Bootloader**: Spoofs device status as **Locked** to Fastboot & Android system properties while remaining fully unlocked.
- 🔓 **Full Fastboot Command Unlocks**: Unlocks all 165 Fastboot & OEM streaming commands without restrictions.
- ⚡ **VBMeta Enabled**: VBMeta integrity handled in-memory; retains full Play Integrity status.
- 🔘 **Hardware Fastboot Trigger**: Holding **Volume Down** on boot redirects directly into Fastboot (Bootloader) mode.
- 🦊 **OrangeFox Recovery Support**: Includes pre-tuned `vendor_boot.img` for Android 15 with AVB flags removed for custom/ported ROM support.

---

### 🛠️ Installation Instructions

> [!WARNING]
> A factory reset / Format Data in recovery is **REQUIRED** after initial flashing because the device state is spoofed as locked to the OS.

#### Option A: Flash via Custom Recovery (TWRP / OrangeFox)
1. Reboot to OrangeFox / TWRP Recovery.
2. Flash the attached `Android-15-Fenrir-Patch-recovery-ab.zip` (for A15) or `Android-14-Fenrir-Patch-recovery-ab.zip` (for A14).
3. Go to Wipe -> **Format Data** (Type `yes`).
4. Reboot System.

#### Option B: Manual Fastboot Flashing

**For Android 15 (`A15`)**:
```bash
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img
fastboot flash vbmeta_a vbmeta-stock.img
fastboot flash vbmeta_b vbmeta-stock.img
fastboot flash vendor_boot_a vendor_boot-orangefox.img
fastboot flash vendor_boot_b vendor_boot-orangefox.img
fastboot reboot
```

**For Android 14 (`A14`)**:
```bash
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img
fastboot reboot
```

---

### 🤝 Credits & Acknowledgments
- **Fenrir Framework**: [@R0rt1z2](https://github.com/R0rt1z2)
- **Research & Development**: [@ramabondanp](https://github.com/ramabondanp) & [@mehraann19](https://github.com/sheikhmehraann)

# 🐺 Fenrir v1.0.0 — Infinix GT 20 Pro (X6871)

> [!CAUTION]
> **COMPATIBILITY WARNING**: This release is engineered strictly for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate**. Do NOT flash binaries from other devices or cross-flash mismatched firmware builds.

---

### 📱 Supported Firmware Builds
- **Android 15 (XOS 15)**: `X6871-15.1.2.165SP05(OP001PF001AZ)` & `X6871-15.1.2.180SP05(OP001PF001AZ)`
- **Android 14 (XOS 14)**: `X6871-H962CF-U-OP-250217V2673` (Strict base version match required)

---

### ✨ Features & Capabilities
- 🟢 **Play Integrity / Green State**: Grants Green verified boot state without needing Play Integrity Fix (PIF) modules or Magisk hide routines.
- 🔒 **Stealth Locked Bootloader**: Spoofs device status as **Locked** to system apps & Fastboot while remaining fully unlocked.
- 🔓 **Unlocked All Fastboot Commands**: Completely unlocks all 165 Fastboot & OEM streaming commands without restrictions.
- ⚡ **Enforcing Verity Mode**: Retains `veritymode=enforcing` while permitting custom boot & recovery image execution.
- 🔘 **Hardware Fastboot Trigger**: Holding **Volume Down** on startup boots directly into Fastboot (Bootloader) mode.
- 🦊 **OrangeFox Recovery Support**: Pre-tuned recovery image (`patched-vendor_boot.img`) with AVB flags removed for seamless port ROM booting.

---

### 🛠️ Installation Instructions

> [!WARNING]
> **FORMAT DATA REQUIRED**: A factory reset / Format Data in recovery is mandatory after initial flashing due to locked state spoofing.

#### Method 1: Recovery Flashable ZIP (Recommended)
1. Reboot your device into OrangeFox / TWRP Recovery.
2. Flash `Android-15-Fenrir-Patch-recovery-ab.zip` (for A15) or `Android-14-Fenrir-Patch-recovery-ab.zip` (for A14).
3. Go to **Wipe** -> **Format Data** (type `yes`).
4. Reboot to System.

#### Method 2: Fastboot Mode Flashing

**Android 15 (`A15`)**:
```bash
fastboot flash lk_a A15/lk-patched.img
fastboot flash lk_b A15/lk-patched.img
fastboot flash vbmeta_a A15/vbmeta-stock.img
fastboot flash vbmeta_b A15/vbmeta-stock.img
fastboot flash vendor_boot_a A15/vendor_boot-orangefox.img
fastboot flash vendor_boot_b A15/vendor_boot-orangefox.img
fastboot reboot
```

**Android 14 (`A14`)**:
```bash
fastboot flash lk_a A14/lk-patched.img
fastboot flash lk_b A14/lk-patched.img
fastboot reboot
```

---

### 🤝 Credits & Acknowledgments
- **Fenrir Framework**: Created by [@R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [@ramabondanp](https://github.com/ramabondanp) & [@mehraann19](https://github.com/sheikhmehraann)

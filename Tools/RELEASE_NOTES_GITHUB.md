# 🐺 Fenrir v1.0.0 — Infinix GT 20 Pro (X6871)

> [!CAUTION]
> **COMPATIBILITY WARNING**: This release is engineered strictly for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate**. Do NOT flash binaries from other devices or cross-flash mismatched firmware builds.

---

### 📱 Supported Firmware Builds
- **Android 15 (XOS 15)**: `X6871-15.1.2.165SP05(OP001PF001AZ)` & `X6871-15.1.2.180SP05(OP001PF001AZ)`
- **Android 14 (XOS 14)**: `X6871-H962CF-U-OP-250217V2673` (Strict base version match required)

---

### 🛠️ Installation Instructions

> [!WARNING]
> **FORMAT DATA REQUIRED**: A factory reset / Format Data in recovery is **REQUIRED** after initial flashing because the device state is spoofed as locked to the OS.

#### Method 1: Flash via Custom Recovery (OrangeFox / TWRP)
1. Reboot your device into OrangeFox or TWRP Recovery.
2. Flash `Android-15-Fenrir-Patch-recovery-ab.zip` (for A15) or `Android-14-Fenrir-Patch-recovery-ab.zip` (for A14).
3. Navigate to **Wipe** -> **Format Data** (type `yes`).
4. Reboot to System.

#### Method 2: Manual Fastboot Flashing

**For Android 15 (`A15`)**:
```bash
fastboot flash lk_a A15/lk-patched.img
fastboot flash lk_b A15/lk-patched.img
fastboot flash vbmeta_a A15/vbmeta-stock.img
fastboot flash vbmeta_b A15/vbmeta-stock.img
fastboot flash vendor_boot_a A15/vendor_boot-orangefox.img
fastboot flash vendor_boot_b A15/vendor_boot-orangefox.img
fastboot reboot
```

**For Android 14 (`A14`)**:
```bash
fastboot flash lk_a A14/lk-patched.img
fastboot flash lk_b A14/lk-patched.img
fastboot reboot
```

---

### 🤝 Credits & Acknowledgments
- **Fenrir Framework**: Created by [@R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [@ramabondanp](https://github.com/ramabondanp) & [@mehraann19](https://github.com/sheikhmehraann)

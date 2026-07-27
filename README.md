# Fenrir Bootloader Suite — Infinix GT 20 Pro (`X6871`)

![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro-blue.svg)
![Chipset](https://img.shields.io/badge/SoC-Dimensity%208200%2F8300-orange.svg)
![Android Support](https://img.shields.io/badge/Android-14%20%7C%2015-green.svg)
![Status](https://img.shields.io/badge/Status-Verified%20%26%20Tested-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Production-ready, forensically verified bootloader patch suite and recovery setup for the **Infinix GT 20 Pro (`X6871`)** running **Android 14 (XOS 14)** and **Android 15 (XOS 15)**.

---

## 🌟 Key Features

- 🟢 **Full Green Boot State**: Suppresses the yellow/orange bootloader warning screen on logo boot.
- 🛡️ **Play Integrity / Device Certification**: Passes hardware/bootloader integrity checks by reporting `verifiedbootstate=green` to Android.
- 🔒 **Spoofed Lock State (`LKS_LOCK`)**: Reports `unlocked = no` (`LKS_LOCK = 4`) to Fastboot queries & bootloader UI.
- 🔓 **Unlocked Fastboot/OEM Commands**: Completely overrides `sec_get_vfy_policy` so all 157 fastboot & OEM streaming commands are permitted.
- ⚡ **Verity Enforcing Mode**: Preserves `veritymode=enforcing` while permitting custom/modified kernel images via AVB error flag hooks.
- 🦊 **OrangeFox Recovery Integration**: Includes pre-tuned `vendor_boot.img` with `FBE v2` decryption support and modified `fstab` (AVB mount flags stripped).

---

## 📂 Repository Directory Layout

```
REPO-X6871-Fenrir/
├── A14/                                # Android 14 Support Package
│   ├── lk-patched.img                 # Fenrir Patched A14 LK Bootloader
│   ├── lk-stock-backup.img            # Stock Android 14 LK Backup
│   ├── flash_a14.bat                  # 1-Click Windows Flashing Script
│   └── flash_a14.sh                   # Linux / macOS Flashing Script
├── A15/                                # Android 15 Support Package
│   ├── lk-patched.img                 # Fenrir Patched A15 LK Bootloader
│   ├── lk-stock-backup.img            # Stock Android 15 LK Backup
│   ├── vbmeta-stock.img               # Stock A15 VBMETA
│   ├── vendor_boot-orangefox.img      # Patched OrangeFox R12 Recovery
│   ├── flash_a15.bat                  # 1-Click Windows Flashing Script
│   └── flash_a15.sh                   # Linux / macOS Flashing Script
├── Tools/                              # Developer & Verification Tools
│   ├── build_a14.py                   # A14 Python Build Engine
│   ├── build_a15.py                   # A15 Python Build Engine
│   └── verify.py                      # Ultra-Deep Forensic Verification Engine
├── .gitignore                          # Git Ignore File
├── LICENSE                             # MIT License
└── README.md                           # Master Documentation
```

---

## 🔒 Verified Binary Hashes

All images in this repository have been forensically verified with 0 collateral byte corruption outside patch sites:

| Partition / File | Target OS | File Size | SHA-256 Checksum |
|:---|:---:|:---:|:---|
| `A14/lk-patched.img` | Android 14 | `2,650,352` bytes | `0f6002929feb982abd9fdb1c93de99db0cf14110f8398ed7c841d18819cd2f34` |
| `A15/lk-patched.img` | Android 15 | `2,699,504` bytes | `fae5cf00170b19aef0841752bff6b4bff59eb72913a44217b159f2bae9d127bc` |
| `A15/vbmeta-stock.img` | Android 15 | `12,288` bytes | `cd3e6f4746da47c3a743f5509c826bd33c542d6456135137d36d52f3bbee34f0` |
| `A15/vendor_boot-orangefox.img` | Android 15 | `67,108,864` bytes | `1a5e2b2813842ddcc3f079ce6420df9412cd8ba397db0ed02dc91fad4196567a` |

---

## 🚀 Flashing Instructions

### Prerequisites
1. Install [Android Platform-Tools](https://developer.android.com/studio/releases/platform-tools) (`fastboot`).
2. Boot your phone into **Fastboot Mode** (Hold `Volume Down + Power`).

### Option A: Automatic Flashing (Windows / Linux)
- **Android 15**: Run `A15/flash_a15.bat` (Windows) or `bash A15/flash_a15.sh` (Linux/macOS).
- **Android 14**: Run `A14/flash_a14.bat` (Windows) or `bash A14/flash_a14.sh` (Linux/macOS).

### Option B: Manual Fastboot Commands

#### For Android 15 (A15):
```bash
# 1. Flash Fenrir Patched LK (Both Slots)
fastboot flash lk_a A15/lk-patched.img
fastboot flash lk_b A15/lk-patched.img

# 2. Flash Stock VBMETA (Both Slots)
fastboot flash vbmeta_a A15/vbmeta-stock.img
fastboot flash vbmeta_b A15/vbmeta-stock.img

# 3. Flash OrangeFox Recovery vendor_boot (Both Slots)
fastboot flash vendor_boot_a A15/vendor_boot-orangefox.img
fastboot flash vendor_boot_b A15/vendor_boot-orangefox.img

# 4. Reboot System
fastboot reboot
```

#### For Android 14 (A14):
```bash
# 1. Flash Fenrir Patched LK (Both Slots)
fastboot flash lk_a A14/lk-patched.img
fastboot flash lk_b A14/lk-patched.img

# 2. Reboot System
fastboot reboot
```

---

## 🛠️ Rebuilding / Verifying From Source

To verify binary integrity or rebuild the patched images from stock backups:

```bash
# Run forensic verification engine on A15
python Tools/verify.py

# Rebuild A15 patched image
python Tools/build_a15.py

# Rebuild A14 patched image
python Tools/build_a14.py
```

---

## ⚠️ Disclaimer

This software is provided for educational and device recovery purposes only. Modifying bootloader partitions carries inherent risks. Always ensure you have backups of your stock partitions before flashing.

---

## 🤝 Credits & Acknowledgments
- **Architect & Developer**: Jalapeno
- **Exploit Framework**: Fenrir / LKInjector
- **Recovery**: OrangeFox Recovery Team

# Fenrir Bootloader Suite — Infinix GT 20 Pro (X6871)

![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro-blue.svg)
![SoC](https://img.shields.io/badge/SoC-Dimensity%208200%20Ultimate-orange.svg)
![Android Support](https://img.shields.io/badge/Android-14%20%7C%2015-green.svg)
![Status](https://img.shields.io/badge/Status-Verified%20%26%20Tested-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Production-grade bootloader exploit suite and recovery setup for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate** across **Android 14** and **Android 15**.

---

## 🌟 Overview & Key Capabilities

This repository contains pre-patched bootloaders (`lk.img`), recovery builds, and verification scripts built using the **Fenrir** framework:

- 🟢 **Verified Boot State (`GREEN`)**: Forces `verifiedbootstate=green`, suppressing the boot logo warning screen and satisfying Play Integrity boot requirements.
- 🔒 **Spoofed Lock State (`LKS_LOCK`)**: Reports `unlocked = no` (`LKS_LOCK = 4`) to Fastboot queries and system properties while remaining fully unlocked.
- 🔓 **Unlocked Fastboot & OEM Commands**: Completely bypasses `sec_get_vfy_policy` signature checks, allowing all 157 Fastboot and OEM streaming commands.
- ⚡ **AVB & Verity Enforcing Mode**: Preserves `veritymode=enforcing` while permitting modified kernel loading via AVB error flag hooks.
- 🦊 **OrangeFox Recovery Integration**: Includes pre-tuned `vendor_boot.img` for Android 15 with File-Based Encryption (`FBE v2`) decryption support and modified `fstab`.

---

## 📁 Repository Structure

```
REPO-X6871-Fenrir/
├── A14/                                # Android 14 Support Package
│   ├── lk-patched.img                 # Fenrir Patched A14 Bootloader
│   ├── lk-stock-backup.img            # Stock Android 14 LK Backup
│   ├── flash_a14.bat                  # Windows 1-Click Flash Script
│   └── flash_a14.sh                   # Linux / macOS Flash Script
├── A15/                                # Android 15 Support Package
│   ├── lk-patched.img                 # Fenrir Patched A15 Bootloader
│   ├── lk-stock-backup.img            # Stock Android 15 LK Backup
│   ├── vbmeta-stock.img               # Stock A15 VBMETA
│   ├── vendor_boot-orangefox.img      # Patched OrangeFox R12 Recovery
│   ├── flash_a15.bat                  # Windows 1-Click Flash Script
│   └── flash_a15.sh                   # Linux / macOS Flash Script
├── Tools/                              # Build Engines & Verifiers
│   ├── build_a14.py                   # A14 Python Build Engine
│   ├── build_a15.py                   # A15 Python Build Engine
│   └── verify.py                      # Ultra-Deep Forensic Verification Engine
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔒 Verified Binary Hashes

| Partition / Image | Platform / Target | File Size | SHA-256 Checksum |
|:---|:---:|:---:|:---|
| `A14/lk-patched.img` | Android 14 (XOS 14) | `2,650,352` bytes | `0f6002929feb982abd9fdb1c93de99db0cf14110f8398ed7c841d18819cd2f34` |
| `A15/lk-patched.img` | Android 15 (XOS 15) | `2,699,504` bytes | `fae5cf00170b19aef0841752bff6b4bff59eb72913a44217b159f2bae9d127bc` |
| `A15/vbmeta-stock.img` | Android 15 | `12,288` bytes | `cd3e6f4746da47c3a743f5509c826bd33c542d6456135137d36d52f3bbee34f0` |
| `A15/vendor_boot-orangefox.img` | Android 15 | `67,108,864` bytes | `1a5e2b2813842ddcc3f079ce6420df9412cd8ba397db0ed02dc91fad4196567a` |

---

## 🚀 Installation Guide

### Option A: Automatic Flashing
- **Android 15**: Run `A15/flash_a15.bat` (Windows) or `bash A15/flash_a15.sh` (Linux/macOS).
- **Android 14**: Run `A14/flash_a14.bat` (Windows) or `bash A14/flash_a14.sh` (Linux/macOS).

### Option B: Manual Fastboot Commands

#### Android 15 (A15):
```bash
fastboot flash lk_a A15/lk-patched.img
fastboot flash lk_b A15/lk-patched.img
fastboot flash vbmeta_a A15/vbmeta-stock.img
fastboot flash vbmeta_b A15/vbmeta-stock.img
fastboot flash vendor_boot_a A15/vendor_boot-orangefox.img
fastboot flash vendor_boot_b A15/vendor_boot-orangefox.img
fastboot reboot
```

#### Android 14 (A14):
```bash
fastboot flash lk_a A14/lk-patched.img
fastboot flash lk_b A14/lk-patched.img
fastboot reboot
```

---

## 🤝 Credits & Acknowledgments

- **Fenrir Framework**: Created by [R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [Rama Bondan](https://github.com/ramabondanp) & [Mehraan](https://github.com/sheikhmehraann)
- **Recovery**: OrangeFox Recovery Team

---

## ⚠️ Disclaimer

This repository is provided for educational and device recovery purposes. Modifying low-level bootloader partitions carries risk. Always keep backups of original stock partitions before flashing.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

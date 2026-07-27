# Fenrir Bootloader Suite — Infinix GT 20 Pro (X6871)

![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro-blue.svg)
![SoC](https://img.shields.io/badge/SoC-Dimensity%208200%20Ultimate-orange.svg)
![Android Support](https://img.shields.io/badge/Android-14%20%7C%2015-green.svg)
![Status](https://img.shields.io/badge/Status-Verified%20%26%20Tested-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Professional, pre-patched bootloader suite and custom recovery setup for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate**.

---

## 📱 Supported Target Firmware Builds

- **Android 15**: `X6871-15.1.2.180SP05-OP001PF001AZ`
- **Android 14**: `X6871-H962CF-U-OP-250217V2673`

---

## 🚀 Benefits & Advantages

- 🟢 **Bypass Boot Warnings**: Completely suppresses the yellow/orange bootloader warning on startup.
- 🛡️ **Pass Play Integrity & Banking Apps**: Spoofs verified boot status to Green so banking apps and Play Integrity checks pass cleanly.
- 🔒 **Stealth Locked Appearance**: Device reports **Locked** to Android OS and Fastboot queries while remaining fully unlocked.
- 🔓 **Full Fastboot Control**: Unlocks all 157 Fastboot & OEM streaming commands for advanced partition flashing.
- ⚡ **Seamless Custom Kernel Support**: Preserves verity enforcing mode while granting permission to boot custom boot & recovery images.

---

## ✨ Features & Included Spoofs

- 🟢 **Green Boot State**: Removes boot logo warnings and forces Green state for Play Integrity certification.
- 🔒 **Spoofed Locked Status**: Device reports **Locked** to system apps & fastboot while staying fully unlocked.
- 🔓 **Unlocked All Fastboot Commands**: Unlocks all Fastboot & OEM streaming commands without restrictions.
- ⚡ **Verity Enforcing Mode**: Preserves Enforcing verity mode while allowing custom kernels and boot images.

---

## 🚀 Flashing Guide

### For Android 15 (A15):
```bash
fastboot flash lk_a A15/lk-patched.img
fastboot flash lk_b A15/lk-patched.img
fastboot flash vbmeta_a A15/vbmeta-stock.img
fastboot flash vbmeta_b A15/vbmeta-stock.img
fastboot flash vendor_boot_a A15/vendor_boot-orangefox.img
fastboot flash vendor_boot_b A15/vendor_boot-orangefox.img
fastboot reboot
```

### For Android 14 (A14):
```bash
fastboot flash lk_a A14/lk-patched.img
fastboot flash lk_b A14/lk-patched.img
fastboot reboot
```

---

## 🤝 Credits & Acknowledgments

- **Original Framework Owner**: [R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [Rama Bondan](https://github.com/ramabondanp) & [Mehraan](https://github.com/sheikhmehraann)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

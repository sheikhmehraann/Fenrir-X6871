# Fenrir Bootloader Suite — Infinix GT 20 Pro (X6871)

![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro-blue.svg)
![SoC](https://img.shields.io/badge/SoC-Dimensity%208200%20Ultimate-orange.svg)
![Android Support](https://img.shields.io/badge/Android-14%20%7C%2015-green.svg)
![Status](https://img.shields.io/badge/Status-Verified%20%26%20Tested-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Professional, pre-patched bootloader suite and custom recovery setup for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate**.

---

## 📱 Supported Target Firmware Builds

- `X6871-15.1.2.165SP05(OP001PF001AZ)`
- `X6871-15.1.2.180SP05(OP001PF001AZ)`
- `X6871-H962CF-U-OP-250217V2673`

---

## ⚠️ Firmware & Component Compatibility Notes

- **Android 14 (`A14`)**: Based on **XOS 14**. The `lk.img` is strict and works **ONLY** on its matching base version (`X6871-H962CF-U-OP-250217V2673`). Do not attempt to cross-flash across different A14 builds.
- **Android 15 (`A15`)**: Based on **XOS 15**. Tested & verified on build versions `X6871-15.1.2.165SP05(OP001PF001AZ)` and `X6871-15.1.2.180SP05(OP001PF001AZ)`.
- **Patched Recovery (`patched-vendor_boot.img`)**: Based on `OrangeFox-R12.0_20260508_15.1.2-Unofficial-X6871`, modified with AVB flags removed to boot seamlessly on Ported ROMs.

---

## 🚀 Benefits & Advantages

- 🟢 **Bypass Boot Warnings**: Completely suppresses the yellow/orange bootloader warning on startup.
- 🛡️ **Pass Play Integrity & Banking Apps**: Spoofs verified boot status to Green so banking apps and Play Integrity checks pass cleanly.
- 🔒 **Stealth Locked Appearance**: Device reports **Locked** to Android OS and Fastboot queries while remaining fully unlocked.
- 🔓 **Full Fastboot Control**: Unlocks all 165 Fastboot & OEM streaming commands for advanced partition flashing.
- ⚡ **Seamless Custom Kernel Support**: Preserves verity enforcing mode while granting permission to boot custom boot & recovery images.

---

## ✨ Features & Included Spoofs

- 🟢 **Green Boot State**: Removes boot logo warnings and forces Green state for Play Integrity certification.
- 🔒 **Spoofed Locked Status**: Device reports **Locked** to system apps & fastboot while staying fully unlocked.
- 🔓 **Unlocked All Fastboot Commands**: Unlocks all 165 Fastboot & OEM streaming commands without restrictions.
- ⚡ **Verity Enforcing Mode**: Preserves Enforcing verity mode while allowing custom kernels and boot images.

---

## 🚀 Flashing Guide (Recovery Method)

1. Reboot your device into OrangeFox or TWRP Recovery.
2. Download and Flash `Android-15-Fenrir-Patch-recovery-ab.zip` (for A15) or `Android-14-Fenrir-Patch-recovery-ab.zip` (for A14) from [Releases](https://github.com/sheikhmehraann/Fenrir-X6871/releases).
3. Navigate to **Wipe** -> **Format Data** (type `yes`).
4. Reboot to System.

---

## ❓ Frequently Asked Questions (FAQ)

1. **Can I change the kernel?**  
   Yes.

2. **Can I change recovery?**  
   At the moment, **NO** (until a Fenrir-supported custom recovery is built).

3. **Can I change ROMs?**  
   Yes, but you **MUST** reflash Fenrir (`lk-patched.img`) before rebooting to system.

4. **Port ROM VBMeta is disabled, what will happen?**  
   Fenrir handles VBMeta automatically and the device will boot normally.

5. **Why can't I disable VBMeta?**  
   Because disabling VBMeta prevents you from getting Strong Play Integrity certification.

6. **Why do I need to format data?**  
   Because your device bootloader state is spoofed as locked to the OS, requiring a clean user data partition.

7. **Why can't I dirty flash?**  
   Dirty flashing will fail, forcing you into recovery and requiring a format.

8. **Why is my Play Integrity not Strong after flashing?**  
   Common reasons:  
   - You may be using an old `boot.img` with outdated security patches.  
   - You may be running an older ROM build.  
   - Conflicting Play Integrity Fix (PIF) module spoofing.  
   - Your VBMeta is disabled.

9. **What happens if I change ROM and forget to reflash Fenrir?**  
   The device will bootloop.

10. **What should I do if I get a bootloop?**  
    If you follow instructions, you won't bootloop. However, if a bootloop occurs, visit an authorized Service Center (Carlcare) or use MTK flashing tools (such as AMT, UnlockTool, etc.) to unbrick your device.

11. **Port ROM sometimes reflashes stock recovery, what should I do?**  
    Reflash Fenrir (`lk-patched.img` & `vendor_boot`) before rebooting.

---

## 🤝 Credits & Acknowledgments

- **Original Framework Owner**: [R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [Rama Bondan](https://github.com/ramabondanp) & [Mehraan](https://github.com/sheikhmehraann)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

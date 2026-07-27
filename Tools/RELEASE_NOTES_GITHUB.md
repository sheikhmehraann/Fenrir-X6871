# 🐺 Fenrir v1.0.0 — Infinix GT 20 Pro (X6871)

> [!CAUTION]
> **COMPATIBILITY WARNING**: This release is engineered strictly for the **Infinix GT 20 Pro (`X6871`)** powered by **MediaTek Dimensity 8200 Ultimate**. Do NOT flash binaries from other devices or cross-flash mismatched firmware builds.

---

### 📱 Supported Firmware Builds
- **Android 15 (XOS 15)**: `X6871-15.1.2.165SP05(OP001PF001AZ)` & `X6871-15.1.2.180SP05(OP001PF001AZ)`
- **Android 14 (XOS 14)**: `X6871-H962CF-U-OP-250217V2673` (Strict base version match required)

---

### 🛠️ Flashing Guide (Recovery Method)

> [!WARNING]
> **FORMAT DATA REQUIRED**: A factory reset / Format Data in recovery is **REQUIRED** after initial flashing because the device state is spoofed as locked to the OS.

1. Reboot your device into OrangeFox or TWRP Recovery.
2. Download and Flash `Android-15-Fenrir-Patch-recovery-ab.zip` (for A15) or `Android-14-Fenrir-Patch-recovery-ab.zip` (for A14) attached below.
3. Navigate to **Wipe** -> **Format Data** (type `yes`).
4. Reboot to System.

---

### ❓ Frequently Asked Questions (FAQ)

1. **Can I install custom kernels?**  
   Yes. Custom kernels compile cleanly and boot without breaking verified boot state.

2. **Can I replace the custom recovery?**  
   At the moment, **NO** (until a Fenrir-supported custom recovery is built).

3. **Can I flash custom / ported ROMs?**  
   Yes, but you **MUST** reflash Fenrir before rebooting into system whenever switching ROMs.

4. **What happens if a ported ROM has VBMeta disabled?**  
   Fenrir dynamically manages VBMeta state in memory, allowing the ROM to boot normally without degrading attestation status.

5. **Why can't I manually disable VBMeta?**  
   Because disabling VBMeta destroys hardware attestation trees and prevents your device from achieving Strong Play Integrity certification.

6. **Why is a Format Data mandatory?**  
   Because device lock state emulation changes how Android's keymaster and vold daemons handle hardware-backed encryption keys.

7. **Can I dirty flash update zips?**  
   No. Dirty flashing across mismatched encryption parameters will fail and force a recovery boot loop.

8. **Why is Play Integrity failing or not reporting Strong?**  
   Common reasons:  
   - You may be using an old `boot.img` with outdated security patches.  
   - You may be running an older ROM build.  
   - Conflicting Play Integrity Fix (PIF) module spoofing.  
   - Your VBMeta is disabled.

9. **What happens if I forget to reflash Fenrir after updating a ROM?**  
   The device will enter a boot loop.

10. **How do I recover from a boot loop?**  
    If you follow instructions, you won't bootloop. However, if a bootloop occurs, visit an authorized Service Center (Carlcare) or use MTK flashing tools (such as AMT, UnlockTool, etc.) to unbrick your device.

11. **What should I do if a ported ROM reflashes stock recovery?**  
    Reflash Fenrir (bootloader and recovery package) before booting into system.

---

### 🤝 Credits & Acknowledgments
- **Original Framework Owner**: [@R0rt1z2](https://github.com/R0rt1z2/fenrir)
- **Research & Development**: [@ramabondanp](https://github.com/ramabondanp) & [@mehraann19](https://github.com/sheikhmehraann)

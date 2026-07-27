# 🐺 Fenrir Bootloader Suite — Infinix GT 20 Pro (`X6871`)

[![Device Target](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro%20%28X6871%29-1081E0?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Platform](https://img.shields.io/badge/SoC-MediaTek%20Dimensity%208200%20Ultimate-FF6600?style=for-the-badge&logo=cpu&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Firmware Base](https://img.shields.io/badge/OS%20Base-XOS%2014%20%7C%20XOS%2015-00C853?style=for-the-badge&logo=googleplay&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![License](https://img.shields.io/badge/License-MIT-6C5CE7?style=for-the-badge)](LICENSE)

An enterprise-grade, forensically verified bootloader security patch suite and recovery deployment environment for the **Infinix GT 20 Pro (`X6871`)**, engineered specifically for the MediaTek Dimensity 8200 Ultimate (MT6896/MT6897 platform lineage).

---

## 📌 Executive Summary

Fenrir modifies low-level Little Kernel execution flows to preserve **Strong Play Integrity** and **Green Verified Boot State** while running custom kernels, custom recoveries, and ported ROMs. It eliminates unlocked bootloader logo warnings, emulates a locked state to OS system properties, and removes vendor fastboot command restrictions without compromising device security.

---

## 📱 Firmware & Platform Compatibility Matrix

| Android Version | Operating System | Verified Build Target | Status |
|:---:|:---:|:---|:---:|
| **Android 15** | XOS 15 | `X6871-15.1.2.165SP05(OP001PF001AZ)` | ✅ Tested & Verified |
| **Android 15** | XOS 15 | `X6871-15.1.2.180SP05(OP001PF001AZ)` | ✅ Tested & Verified |
| **Android 14** | XOS 14 | `X6871-H962CF-U-OP-250217V2673` | ✅ Tested & Verified |

---

## ⚡ Core Capabilities & Architecture

> [!NOTE]
> Fenrir operates directly at the Little Kernel layer, overriding security evaluation routines prior to OS boot handoff.

- 🟢 **Green Verified Boot State**: Forces Green boot state, eliminating boot warnings and passing Play Integrity checks.
- 🔒 **Stealth Lock Emulation**: Emulates bootloader state as locked. System apps and Fastboot queries report a **Locked** bootloader.
- 🔓 **Fastboot Command Set Unlocking**: Overrides security verification policy to unlock all 165 Fastboot and OEM streaming commands.
- ⚡ **AVB & Verity Policy Enforcement**: Retains enforcing verity mode in memory, allowing custom boot and recovery images to execute without breaking safety attestations.

---

## 🛠️ Deployment & Flashing Guide

> [!CAUTION]
> **COMPATIBILITY WARNING**: Verify your exact device codename (`X6871`) and firmware build version before flashing. Flashing bootloader binaries across incompatible platforms will result in a hard brick.

> [!WARNING]
> **FORMAT DATA MANDATORY**: A full factory reset / Format Data in custom recovery is **REQUIRED** during initial installation due to bootloader state lock emulation.

### Recommended Recovery Flashing Method

1. Reboot device into **OrangeFox Recovery** or **TWRP**.
2. Flash the target deployment package attached in [Releases](https://github.com/sheikhmehraann/Fenrir-X6871/releases):
   - **Android 15**: `Android-15-Fenrir-Patch-recovery-ab.zip`
   - **Android 14**: `Android-14-Fenrir-Patch-recovery-ab.zip`
3. Navigate to **Wipe** ➔ **Format Data** (Type `yes` to confirm).
4. Reboot to System.

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. Can I install custom kernels?</b></summary>
<br>
Yes. Custom kernels compile cleanly and boot without breaking verified boot state.
</details>

<details>
<summary><b>2. Can I replace the custom recovery?</b></summary>
<br>
Currently, <b>NO</b>. Maintain the provided recovery until a dedicated Fenrir-compatible build is released.
</details>

<details>
<summary><b>3. Can I flash custom / ported ROMs?</b></summary>
<br>
Yes. However, you <b>MUST</b> reflash the Fenrir deployment package before rebooting into system whenever switching ROMs.
</details>

<details>
<summary><b>4. What happens if a ported ROM has VBMeta disabled?</b></summary>
<br>
Fenrir dynamically manages VBMeta state in memory, allowing the ROM to boot normally without degrading attestation status.
</details>

<details>
<summary><b>5. Why can't I manually disable VBMeta?</b></summary>
<br>
Disabling VBMeta destroys hardware attestation trees and prevents your device from achieving Strong Play Integrity certification.
</details>

<details>
<summary><b>6. Why is a Format Data mandatory?</b></summary>
<br>
Because device lock state emulation changes how Android's keymaster and vold daemons handle hardware-backed encryption keys.
</details>

<details>
<summary><b>7. Can I dirty flash update zips?</b></summary>
<br>
No. Dirty flashing across mismatched encryption parameters will fail and force a recovery boot loop.
</details>

<details>
<summary><b>8. Why is Play Integrity failing or not reporting Strong?</b></summary>
<br>
Common root causes include:
<ul>
  <li>Using an outdated <code>boot.img</code> with unpatched security patch levels.</li>
  <li>Running an outdated base ROM version.</li>
  <li>Conflicting Play Integrity Fix (PIF) modules or Magisk hide scripts.</li>
  <li>VBMeta manually disabled via fastboot flags.</li>
</ul>
</details>

<details>
<summary><b>9. What happens if I forget to reflash Fenrir after updating a ROM?</b></summary>
<br>
The device will enter a boot loop.
</details>

<details>
<summary><b>10. How do I recover from a boot loop?</b></summary>
<br>
Reboot to recovery/fastboot and reflash Fenrir. If inaccessible, unbrick using stock images via authorized service tools (AMT, UnlockTool, Carlcare).
</details>

<details>
<summary><b>11. What should I do if a ported ROM reflashes stock recovery?</b></summary>
<br>
Reflash Fenrir (bootloader and recovery package) before booting into system.
</details>

---

## 🤝 Project Credits & Acknowledgments

- **Fenrir Core Architecture**: Created by [@R0rt1z2](https://github.com/R0rt1z2)
- **Research & Device Development**: [@ramabondanp](https://github.com/ramabondanp) & [@mehraann19](https://github.com/sheikhmehraann)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

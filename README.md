# Fenrir Bootloader Suite - Infinix GT 20 Pro (X6871)

[![Device Target](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro%20(X6871)-1081E0?style=flat-square)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Platform](https://img.shields.io/badge/SoC-Dimensity%208200%20Ultimate%20(MT6896)-FF6600?style=flat-square)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Firmware Base](https://img.shields.io/badge/OS%20Base-XOS%2014%20%2F%20XOS%2015-00C853?style=flat-square)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Renkai Engine](https://img.shields.io/badge/Engine-Renkai%20v1.0-8A2BE2?style=flat-square)](https://github.com/sheikhmehraann/Renkai)
[![License](https://img.shields.io/badge/License-MIT-6C5CE7?style=flat-square)](LICENSE)

A bootloader patch set for the Infinix GT 20 Pro (X6871) on the MediaTek Dimensity 8200 Ultimate (MT6896) platform.

Fenrir patches Little Kernel (LK) binaries to bypass secure boot checks, spoof verified boot state to green, emulate a locked bootloader to userspace, and unrestrict fastboot operations. This lets you run custom kernels, custom recoveries, and GSI/ported ROMs while passing Play Integrity checks.

This repository is powered by and integrated with the [Renkai](https://github.com/sheikhmehraann/Renkai) unified bootloader engine.

---

## Supported Firmware Builds

| Android Version | OS Base | Target Build Number | Status |
|---|---|---|---|
| Android 15 | XOS 15 | `X6871-15.1.2.165SP05(OP001PF001AZ)` | Tested and Working |
| Android 15 | XOS 15 | `X6871-15.1.2.180SP05(OP001PF001AZ)` | Tested and Working |
| Android 14 | XOS 14 | `X6871-H962CF-U-OP-250217V2673` | Tested and Working |

Do not flash across mismatched firmware versions or across different device models. Bootloader binaries are platform and version specific.

---

## Technical Overview

Fenrir modifies routines in the `lk`, `bl2_ext`, and `aee` sub-partitions inside the MediaTek bootloader container before OS execution begins.

### 1. Verified Boot State Spoofing
- Injects a patch into the boot state setter (`STR WZR`) so `verified_boot_state` is always written as `0` (GREEN).
- Eliminates the 5-second yellow/orange unlocked bootloader warning on boot.
- Kernel cmdline receives `androidboot.verifiedbootstate=green`.

### 2. Lock State Emulation
- Patches lock state getters across `lk`, `bl2_ext`, and `aee` to return `LKS_LOCK` (`4`).
- TEE and Android userspace detect the device as locked.
- Fastboot query `fastboot getvar unlocked` returns `no`.

### 3. Verification Policy Override
- Patches `sec_get_vfy_policy()` across all sub-partitions to return `0` (`MOV W0, #0; RET`).
- Prevents image authentication errors from halting boot when running modified kernels or recovery images.
- Sets AVB verification error allowance flags.

### 4. Fastboot Security Bypass
- NOPs the security check branch in fastboot command handling.
- Keeps vendor and standard fastboot streaming commands operational on an emulated locked bootloader.

### 5. Hardware Boot Mode Controls
- Patches the boot mode key handler: holding Volume Down routes straight to Fastboot mode (`boot_mode = 0x63`), bypassing the stock Transsion factory test menu.
- Stock Volume Up behavior is preserved to enter Recovery mode.

### 6. Fastboot Idle Timeout Extension
- Stock MediaTek LK disconnects USB fastboot sessions after 60 seconds of inactivity.
- Patched timeout values extend the idle timeout to 10 minutes (600,000 ms), preventing sudden disconnects during large image flashes.

### 7. Custom Fastboot OEM Command
- Adds `fastboot oem bldr_spoof` to inspect or control bootloader spoofing state from host PC.

---

## Renkai Unified Engine Integration

The Infinix GT 20 Pro profiles (`x6871_a15` and `x6871_a14`) are integrated into [Renkai](https://github.com/sheikhmehraann/Renkai), a unified next-generation toolkit combining Fenrir and Kaeru.

### Key Renkai Architecture Features
- **Multi-Partition GFH Container Pipeline**: Rebuilds GFH headers, section tables, and partition alignments using `liblk` v3.2.0.
- **Dual-Mode Certificate Engine**: Automatically signs patched images using either public key hash blocks (`OVERRIDE` mode, used on X6871) or BitString wrapper envelopes (`WRAP` mode).
- **Automated Verification**: Structural validation of GFH magic (`0x58881688`), certificate ASN.1 DER chains, and disassembly opcode match verification.
- **Multi-Device Support**: Unified definitions across MediaTek Dimensity and Helio platforms (Infinix, Nothing, CMF, Xiaomi, POCO, Tecno, Lenovo, itel).

For multi-device builds and unified tooling, visit the [Renkai Repository](https://github.com/sheikhmehraann/Renkai).

---

## Flashing Instructions

A full Format Data in custom recovery is required on initial installation. Lock state emulation alters key derivation in hardware Keymaster/Gatekeeper. Existing userdata encrypted under an unlocked state cannot be decrypted once the bootloader reports locked. Back up your files before proceeding.

### Method 1: Fastboot (PC)

1. Boot the phone into Fastboot mode (power off, then hold Power + Volume Down).
2. Open a terminal in the folder containing your target Android version (`A14` or `A15`).
3. Flash the patched bootloader to both slots:
   ```bash
   fastboot flash lk_a lk-patched.img
   fastboot flash lk_b lk-patched.img
   ```
4. Optional: Flash the clean boot logo to remove warning artifacts:
   ```bash
   fastboot flash logo_a logo-patched.img
   fastboot flash logo_b logo-patched.img
   ```
5. Reboot to recovery:
   ```bash
   fastboot reboot recovery
   ```
6. In OrangeFox or TWRP, go to Wipe -> Format Data, type `yes`, and confirm.
7. Reboot to system.

### Method 2: Custom Recovery (ZIP Package)

1. Reboot into OrangeFox Recovery or TWRP.
2. Transfer and flash the target flashable zip from Releases:
   - For Android 15: `Android-15-Fenrir-Patch-recovery-ab.zip`
   - For Android 14: `Android-14-Fenrir-Patch-recovery-ab.zip`
3. Go to Wipe -> Format Data, type `yes`, and confirm.
4. Reboot to system.

---

## Frequently Asked Questions

**Can I run custom kernels with Fenrir?**  
Yes. Custom kernels boot normally without triggering yellow or red bootloader state warnings.

**Can I use any custom recovery?**  
Use an OrangeFox or TWRP build confirmed working on X6871. Avoid recoveries that force-disable VBMeta during installation.

**Can I flash custom or ported ROMs?**  
Yes. Whenever you flash a new ROM that overwrites the bootloader or boot partition, reflash the Fenrir LK package before the first system boot.

**What happens if a ROM disables VBMeta?**  
If VBMeta verification flags are stripped via fastboot disable flags, hardware key attestation breaks. Keep stock VBMeta enabled; Fenrir handles verification overrides in LK directly.

**Why does my phone bootloop if I skip Format Data?**  
Android disk encryption relies on hardware-backed keys provided by Keymaster. Because Fenrir changes the reported bootloader lock state from unlocked to locked, the keystore cannot derive the old encryption keys. Formatting userdata allows the device to initialize a fresh, clean keystore under the new locked context.

**Can I dirty flash incremental OS updates?**  
Only if the update does not replace the bootloader or change keymaster parameters. If updating firmware across major builds, a clean flash is strongly advised.

**Why is Play Integrity failing or not reporting strong?**  
Check the following:
- Ensure your `boot.img` security patch level matches your vendor SPL.
- Do not use conflicting Play Integrity Fix modules that set conflicting boot state props.
- Ensure VBMeta is not manually disabled in partitions.
- Ensure your ROM build passes basic attestation requirements.

**How do I unbrick if I flash the wrong version?**  
Use MTK client tools (or authorized service tools) to flash stock `lk` and `preloader` back via BROM or Download Agent mode. Always keep stock partition dumps backed up before flashing.

---

## Building from Source

### Option A: Renkai Unified Engine (Recommended)

Requires the [Renkai](https://github.com/sheikhmehraann/Renkai) repository cloned adjacent to this project.

```bash
# Build and verify all supported versions (A14 and A15)
py -3 Tools/build_renkai.py --version all

# Build only Android 15
py -3 Tools/build_renkai.py --version a15

# Build only Android 14
py -3 Tools/build_renkai.py --version a14
```

### Option B: Standalone Pipeline

```bash
# Clone the repository
git clone https://github.com/sheikhmehraann/Fenrir-X6871.git
cd Fenrir-X6871

# Build Android 15 patched LK
py -3 Tools/build_a15.py

# Build Android 14 patched LK
py -3 Tools/build_a14.py

# Verify patches and partition structures
py -3 Tools/verify.py
```

---

## Related Projects and Credits

- Upstream Fenrir architecture and concept: [R0rt1z2](https://github.com/R0rt1z2)
- Renkai unified multi-device engine: [Renkai](https://github.com/sheikhmehraann/Renkai)
- Infinix GT 20 Pro port, testing, and maintenance: [ramabondanp](https://github.com/ramabondanp) and [sheikhmehraann](https://github.com/sheikhmehraann)

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

# Renkai v1.0.0 - Infinix GT 20 Pro (X6871)

Initial public release of the Renkai bootloader patch suite for the Infinix GT 20 Pro (X6871) powered by MediaTek Dimensity 8200 Ultimate (MT6896).

This release provides patched Little Kernel (LK) images for both Android 14 and Android 15 firmware lines, allowing users to run custom kernels, recoveries, and ROMs with a spoofed green verified boot state and emulated locked bootloader.

---

## Supported Firmware Builds

- Android 15 (XOS 15): `X6871-15.1.2.165SP05(OP001PF001AZ)` and `X6871-15.1.2.180SP05(OP001PF001AZ)`
- Android 14 (XOS 14): `X6871-H962CF-U-OP-250217V2673`

Do not flash these binaries onto other device models or mismatched firmware revisions.

---

## Changes in this Release

- Green Boot State Spoof: Sets verified_boot_state to green in memory, eliminating unlocked bootloader screen warnings and setting `androidboot.verifiedbootstate=green`.
- Lock State Emulation: Spoofs bootloader lock state getter as locked (LKS_LOCK = 4) across lk, bl2_ext, and aee sub-partitions.
- Fastboot Unlocked Check: Returns "no" for `fastboot getvar unlocked`.
- Secure Boot Verification Override: Patches `sec_get_vfy_policy()` across all sub-partitions so custom boot and recovery images boot cleanly.
- Security Control Bypass: Overrides fastboot security restrictions so standard and vendor OEM commands remain accessible.
- Volume Down Shortcut: Pressing Volume Down routes directly into Fastboot mode (boot_mode = 0x63), bypassing factory testing menus.
- Fastboot Timeout: Extended idle USB timeout from 60 seconds to 10 minutes (600,000 ms).
- Custom OEM Command: Added `fastboot oem bldr_spoof` for runtime status queries.

---

## Flashing Instructions

Notice: A complete Format Data in custom recovery is required during initial setup. Because bootloader lock state is emulated as locked, hardware Keymaster encryption keys differ from unlocked state. Back up all internal storage before proceeding.

### Fastboot Method

1. Boot device into Fastboot mode.
2. Flash patched LK to both slots:
   ```bash
   fastboot flash lk_a lk-patched.img
   fastboot flash lk_b lk-patched.img
   ```
3. Optional: Flash patched logo to remove warning frames:
   ```bash
   fastboot flash logo_a logo-patched.img
   fastboot flash logo_b logo-patched.img
   ```
4. Reboot into recovery:
   ```bash
   fastboot reboot recovery
   ```
5. In recovery, select Wipe -> Format Data, type `yes`, and confirm.
6. Reboot to system.

### Custom Recovery Method

1. Boot into OrangeFox or TWRP.
2. Flash the zip file matching your firmware:
   - Android 15: `Android-15-Renkai-Patch-recovery-ab.zip`
   - Android 14: `Android-14-Renkai-Patch-recovery-ab.zip`
3. Format Data in recovery (type `yes`).
4. Reboot to system.

---

## Frequently Asked Questions

1. Can I run custom kernels?  
   Yes. Custom kernels boot without triggering yellow or red bootloader state warnings.

2. Can I replace the custom recovery?  
   Use any confirmed OrangeFox or TWRP recovery build for X6871.

3. Can I flash custom or ported ROMs?  
   Yes. Whenever you flash a ROM that replaces the bootloader, reflash the Renkai package before booting into system.

4. What happens if a ROM disables VBMeta?  
   Disabling VBMeta manually strips attestation flags. Leave stock VBMeta untouched; Renkai bypasses verification inside LK directly.

5. Why is Format Data mandatory?  
   Android disk encryption ties key derivation to bootloader lock state via Keymaster. When switching to emulated locked state, existing data cannot be decrypted. A clean format is necessary.

6. Can I dirty flash update zips?  
   No. Mismatched encryption state will cause a recovery bootloop. Clean flashing is advised.

7. Why is Play Integrity failing or not reporting strong?  
   Make sure your kernel security patch level matches your vendor SPL, VBMeta is intact, and you do not have conflicting modules overriding system props.

8. How do I recover from a bootloop?  
   Reboot into fastboot or recovery and reflash the correct Renkai package. If recovery is unreachable, restore stock lk using MTK flash tools.

---

## Renkai Integration

This release is verified against and integrated with the [Renkai](https://github.com/sheikhmehraann/Renkai) unified bootloader framework. Renkai provides multi-partition GFH container rebuilding, dual-mode certificate signing, and automated test verification for MediaTek devices across multiple platforms.

---

## Credits

- Renkai unified framework: [Renkai](https://github.com/sheikhmehraann/Renkai)
- Upstream Fenrir project: [R0rt1z2](https://github.com/R0rt1z2/fenrir)
- Infinix GT 20 Pro port and testing: [ramabondanp](https://github.com/ramabondanp) and [sheikhmehraann](https://github.com/sheikhmehraann)

# DSU, dm-verity, and VBMeta Flags on Android 14/15/16

## 1. Overview
On modern Android devices running Android 14, 15, and 16, dm-verity integrity checks operate in concert with Android Verified Boot (AVB 2.0) and userspace initialization policies. Booting modified system partitions, Generic System Images (GSIs), or Dynamic System Updates (DSU) without tripping verification errors requires precise alignment between LittleKernel command-line generation and VBMeta header flags.

---

## 2. The Android 14 Userspace Command-Line Trap

In older Android versions (Android 11-13), custom bootloader developers frequently modified LittleKernel to append `androidboot.veritymode=disabled` to the kernel command-line.

On Android 14+, this approach triggers a critical userspace failure:
1. LittleKernel passes `androidboot.veritymode=disabled` along with `androidboot.verifiedbootstate=green` and `androidboot.locked=1`.
2. The Linux kernel mounts the root filesystem and executes `/system/bin/init` (EL0).
3. Android `init` evaluates the security descriptor matrix:
   - If `verifiedbootstate == green` AND `device_state == locked`, userspace security policy mandates that `veritymode` MUST be `enforcing`.
   - When `init` encounters the conflicting pair (`green` + `veritymode=disabled`), it treats the execution environment as untrusted.
4. Android `init` issues an immediate reboot panic:
   - System reset register: `NONRST_REG2: 0x2C002000` (Init Panic / Security Abort).
   - Log output in pstore/ramoops: `Init fatal error: security state conflict`.

---

## 3. The Fenrir Dual-Mode Solution

To bypass dm-verity verification on custom or modified partitions without triggering the Android 14 userspace init crash, Fenrir utilizes a dual-mode mechanism:

### Component A: Kernel Command-Line
LittleKernel is configured to preserve `veritymode=enforcing`:
```
androidboot.veritymode=enforcing
androidboot.verifiedbootstate=green
androidboot.locked=1
androidboot.vbmeta.device_state=locked
```
This satisfies Android `init` security consistency requirements.

### Component B: VBMeta Flags (`flags = 2`)
The partition verification bypass is instead signaled through the AVB VBMeta image header:
- Header offset `0x78`: `uint32_t flags`
- Constant: `AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED = 2`

When LittleKernel's AVB subsystem parses a VBMeta image with `flags = 2`:
1. It validates the header and descriptors.
2. It detects the `HASHTREE_DISABLED` flag.
3. It skips construction of the dm-verity device-mapper hashtree table for filesystems (`system`, `vendor`, `product`).
4. It mounts filesystems as standard read-only linear device-mapper volumes rather than verified verity targets.
5. In the kernel command-line, `veritymode` remains reported as `enforcing`, but the underlying block devices operate without hash checking.

---

## 4. Generating & Flashing Disabled VBMeta

Fenrir includes a dedicated tool to generate or patch VBMeta images: `tools/make_disabled_vbmeta.py`.

### Option 1: Patching Stock VBMeta (Recommended)
This method preserves all OEM chain partition descriptors (`boot`, `dtbo`, `vendor_boot`) while flipping the hashtree disabled bit:
```bash
python tools/make_disabled_vbmeta.py -s /path/to/stock/vbmeta.img -o vbmeta_disabled.img
```

Flash the generated image to both slots:
```bash
fastboot flash vbmeta_a vbmeta_disabled.img
fastboot flash vbmeta_b vbmeta_disabled.img
```

### Option 2: Generating a Blank Disabled VBMeta
If testing an entirely custom GSI or AOSP build where chain partition descriptors are not needed:
```bash
python tools/make_disabled_vbmeta.py -o vbmeta_blank_disabled.img
```

---

## 5. Booting Generic System Images (GSI) & DSU

### GSI Flashing Procedure
1. Ensure `x6871-fenrir.bin` is flashed to `lk_a` and `lk_b`.
2. Ensure `vbmeta_disabled.img` (`flags = 2`) is flashed to `vbmeta_a` and `vbmeta_b`.
3. Reboot to fastbootd:
   ```bash
   fastboot reboot fastboot
   ```
4. Flash the GSI system image:
   ```bash
   fastboot flash system system.img
   ```
5. Format userdata (required on first GSI boot):
   ```bash
   fastboot -w
   fastboot reboot
   ```

### Dynamic System Update (DSU) Support
Because LittleKernel maintains `verifiedbootstate=green` and `device_state=locked`, Android's DSU Loader (in Settings -> Developer Options -> DSU Loader) functions without restriction:
1. Select and download a DSU image through the Android settings UI.
2. When prompted to restart into the guest OS, approve the reboot.
3. LittleKernel boots the DSU image with green verification state, bypassing stock signature rejection.

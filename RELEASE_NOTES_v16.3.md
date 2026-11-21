# Fenrir v16.3: Infinix GT 20 Pro (X6871) Public Release

## Target Device & Architecture
- **Device**: Infinix GT 20 Pro (Model: `X6871`, `X6871-OP`)
- **Platform**: MediaTek Dimensity 8200 Ultimate (`MT6895` / `MT6896`)
- **Firmware Target**: Android 16 (`X6871-OP-16.3`, build `BP2A.250605.031.A3`)
- **Architecture**: AArch64 (ARMv8.2-A / ARMv9-A)
- **Container Format**: MediaTek Image Container v2 (dual cert1/cert2 layout)

---

## CRITICAL HARDWARE & SAFETY WARNINGS

1. **Target Specificity**:
   This release is compiled and verified specifically for the **Infinix GT 20 Pro (`X6871`)** running on **MediaTek Dimensity 8200 Ultimate (`MT6895` / `MT6896`)**. Do **NOT** attempt to flash these binaries onto other devices (such as Infinix GT 10 Pro `X6739`, Note series, or other SoCs) without adjusting memory offsets and pattern definitions according to `docs/DEVICE_PORTING.md`. Flashing mismatched bootloader code will result in a Preloader authentication panic (`0x701F`) or early DRAM aborts.

2. **Bootloader Unlock Prerequisite**:
   Your device bootloader must be unlocked via standard fastboot prior to flashing:
   ```bash
   fastboot flashing unlock
   fastboot flashing unlock_critical
   ```

3. **Mandatory Userdata Format (Root of Trust Migration)**:
   If your device was previously running with an unpatched bootloader (where LittleKernel reported `ORANGE` / `unlocked` state to the TrustZone TEE), your current `/data` partition was encrypted using an encryption key derived from that untrusted state.
   Because Fenrir synchronizes the bootloader with the genuine OEM `GREEN` / `locked` Root of Trust, Android 16's Keymint and `vold` daemons will fail to decrypt existing keys derived under the old ORANGE context, triggering `init_user0_failed` (status 25) and booting into recovery.
   **You MUST perform a one-time userdata format upon first installation:**
   - In Recovery: Select `Format Data` (and wipe metadata).
   - In Fastboot: Run `fastboot erase metadata` and `fastboot -w`.
   All subsequent boots will generate and maintain hardware-backed File-Based Encryption (FBE) keys derived under the Green Root of Trust without requiring further wipes.

4. **Hardware Emergency Fastboot Shortcut (Unbrick Guarantee)**:
   Stage 1 contains a bare-metal PMIC hardware key poller executing before LittleKernel platform drivers initialize. If you encounter a bootloop caused by experimental kernel modules, GSI incompatibilities, or userspace crashes:
   - Power off the device (or force shutdown by holding Power + Volume Up for 10 seconds).
   - Hold **Volume Down**.
   - Power on while continuing to hold **Volume Down**.
   - The Stage 1 payload intercepts the boot check and immediately forces Fastboot mode (`99` / `0x63`).

---

## Flashing Guides

### Guide 1: Recovery Flashing Guide (Recommended)
1. **Reboot to Recovery**: Boot your device into TWRP, OrangeFox, or PitchBlack recovery.
2. **Flash Package**: Flash the `X6871-Fenrir-16.3-Flashable.zip` package.
3. **Wipe Metadata & Format Data**: Go to Wipe menu, wipe Metadata, select `Format Data`, and type `yes`.
4. **Reboot**: Select `Reboot System`.

### Guide 2: Fastboot Flashing Guide (Manual CLI)
1. **Reboot to Fastboot**:
   ```bash
   adb reboot bootloader
   ```
2. **Flash Patched LittleKernel (both slots)**:
   ```bash
   fastboot flash lk_a x6871-fenrir.bin
   fastboot flash lk_b x6871-fenrir.bin
   ```
3. **Flash Disabled VBMeta (both slots)**:
   ```bash
   fastboot flash vbmeta_a vbmeta_x6871_disabled_signed.img
   fastboot flash vbmeta_b vbmeta_x6871_disabled_signed.img
   ```
4. **Wipe Metadata & Format Data**:
   ```bash
   fastboot erase metadata
   fastboot -w
   ```
5. **Reboot Device**:
   ```bash
   fastboot reboot
   ```

---

## Architectural Mechanisms & Payload Stages

### 1. Preloader Container v2 Certificate Override (`0xA0`)
MediaTek's Preloader (`BL2_EXT`) verifies partition integrity using an ASN.1 DER parser. Fenrir replaces `cert2` with a synthesized ASN.1 structure beginning with Context-Specific Tag `[0]` (`0xA0`). The Preloader parser treats this tag as an encapsulated hash descriptor: it recalculates and verifies the partition SHA-256 hash across DRAM, but skips OEM digital signature verification, allowing modified LittleKernel partitions to boot without security panics (`0x701F`).

### 2. Stage 1 Bare-Metal Execution Pivot
- **Hook Site**: `0xFFFF000050F11750` (overwrites post-`boot_mode_check()` branch with `bl 0xFFFF000050F02800` / opcode `2C C4 FF 97`).
- **Payload Location**: `0xFFFF000050F02800` (728 bytes of verified AArch64 machine code).
- **Function**: Queries physical Volume Down key state (`detect_key(1)`). If held, writes `99` into `g_boot_mode` (`0xFFFF000050FE4968`) and the secondary buffer (`0xFFFF000050FD5510`), registers custom fastboot commands, and returns cleanly to main LittleKernel flow.

---

## Complete Catalog of 27 LittleKernel Patches

Fenrir applies 27 binary patches to LittleKernel partition data:

| # | Patch Identifier | Target Subroutine / Context | Technical Function & Description |
| :- | :--- | :--- | :--- |
| **01** | `spoof_sboot_state` | `sec_boot_check()` | Forces secure boot attribute to always return `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` (`w0 = 1`), preventing LittleKernel from imposing OEM production lockdown restrictions. |
| **02** | `bypass_security_control` | Fastboot command handler | Replaces conditional branch security checks with `nop` (`1F 20 03 D5`), permitting execution of all bootloader and fastboot routines without authorization tokens. |
| **03** | `spoof_lock_state` | `get_lock_state()` | Forces `get_lock_state()` to unconditionally return `LKS_LOCK` (`4`), causing LittleKernel subsystems to evaluate the device as factory-locked. |
| **04** | `force_avb_device_locked` | `avb_cmdline_append_options()` | Forces `androidboot.vbmeta.device_state=locked` into the assembled kernel command-line. |
| **05** | `force_avb_green_cmdline` | `append_boot_state_cmdline()` | Intercepts boot state string generation and forces `androidboot.verifiedbootstate=green` into the kernel command-line. |
| **06** | `force_get_avb_boot_state` | `get_avb_boot_state()` | Forces the internal AVB boot state query to unconditionally return `AVB_BOOT_STATE_GREEN` (`0`). |
| **07** | `force_sec_boot_state` | `sec_boot_state_get()` | Forces platform security query to return `SEC_BOOT_STATE_GREEN` (`0`). |
| **08** | `force_avb_load_slot_data` | `load_vfy_boot()` | Replaces error branch with an unconditional jump to the slot data loader, allowing execution to proceed with custom or unverified partitions. |
| **09** | `force_avb_skip_cert_vfy` | AVB cert verification loop | Unconditionally branches to `avb_ret = 0` (success), skipping public key certificate chain evaluation. |
| **10** | `force_avb_img_auth_0` | `load_vfy_boot()` | Forces `img_auth_required = 0` and sets `ALLOW_VERIFICATION_ERROR = 1`, permitting boots with modified images. |
| **11** | `force_img_auth_check_0` | `img_auth_check()` callback | Forces the image authentication callback to unconditionally return `0` (success). |
| **12** | `force_avb_verity_mode_ignore_corruption` | dm-verity policy handler | Sets dm-verity error handling to `ignore_corruption` while emitting `androidboot.veritymode=enforcing`, preventing Android 16 userspace init panic `0x2C002000` while supporting DSU and GSIs. |
| **13** | `dont_relock_seccfg` | `seccfg` security manager | Neutralizes the routine that clears or re-locks the `seccfg` security partition. |
| **14** | `disable_ap_watchdog` | `mtk_wdt_enable()` | Modifies watchdog enable routine to deactivate the Application Processor (AP) hardware watchdog timer, preventing reboot loops during boot. |
| **15** | `disable_ap_watchdog_doe` | `mtk_wdt_doe_setup()` | Deactivates the secondary hardware watchdog timer prior to kernel handoff. |
| **16** | `neutralize_orange_warning_screen` | Display warning handler | NOPs out the 5-second delay and framebuffer render for the OEM "Orange State" warning splash. |
| **17** | `neutralize_avb_warning_screen` | `show_warning_screen()` | NOPs out the AVB 5000ms delay and graphic alert displayed upon verification status changes. |
| **18** | `neutralize_orange_state_text_print` | LCM font renderer | Neutralizes the LittleKernel text rendering routine that draws "Orange State" strings to the screen. |
| **19** | `avb_allow_verification_error` | `avb_slot_verify()` flags | Modifies verification flags to include `AVB_SLOT_VERIFY_FLAGS_ALLOW_VERIFICATION_ERROR` (`0x01`). |
| **20** | `enable_kernel_uart_log` | Kernel command-line builder | Appends `mtk_printk_ctrl.disable_uart=0 earlycon printk.devkmsg=on` to enable low-level UART and early console logging. |
| **21** | `force_avb_public_key_trusted` | `validate_vbmeta_public_key()` | Forces validation to set `*out_key_is_trusted = 1` and return `AVB_IO_RESULT_OK` (`0`), accepting custom AVB signing keys. |
| **22** | `force_avb_cmdline_always` | `load_and_verify_boot()` | NOPs out the branch on `VERIFICATION_DISABLED`, ensuring complete AVB command-line arguments are always passed to the kernel. |
| **23** | `force_avb_tee_root_of_trust` | TEE SMC Call 2 (`0xBF000002`) | Overrides register `x2` to `0` (`GREEN`) and injects the 32-byte OEM stock public key digest (`6FDB7DD2...`) into the TEE registration buffer, enabling hardware-backed FBE key derivation in Keymint/vold. |
| **24** | `force_avb_cmdline_pubkey_digest` | Kernel command-line builder | Formats and emits the OEM factory public key digest in `androidboot.vbmeta.public_key_digest`, ensuring consistency with TrustZone. |
| **25** | `force_set_verified_boot_state_green` | `set_verified_boot_state()` | Unconditionally writes `0` (`BOOT_STATE_GREEN`) into global variable `g_verified_boot_state` at `0xFFFF000051006C18`. |
| **26** | `force_set_avb_boot_state_green` | `set_avb_boot_state()` | Unconditionally writes `0` (`AVB_BOOT_STATE_GREEN`) into secondary buffer at `0xFFFF000050FD5510`. |
| **27** | `force_get_lock_state_locked` | `get_lock_state()` path | Unconditionally branches to the locked return path (`LKS_LOCK = 4`) in AVB lock state evaluation. |

---

## Release Asset Hashes & Checksums

| Asset Name | File Size | SHA-256 Digest |
| :--- | :--- | :--- |
| `x6871-fenrir.bin` | 3,182,832 bytes | `FD712A72CC8AC1E7C387FD0F1EBDD735616C21D02F13A55826DE9D45B2B5A3E3` |
| `X6871-Fenrir-16.3-Flashable.zip` | 5,707,888 bytes | `A498FCD8151CE15EAA7B47C13C7A8873520FC0CFACBD879571C9E5E08DBF2E88` |
| `vbmeta_x6871_disabled_signed.img` | 10,304 bytes | `783841D1559610B4F2AEA5E1504FB4257863862A2232E4CE2C766C4FB84BC601` |

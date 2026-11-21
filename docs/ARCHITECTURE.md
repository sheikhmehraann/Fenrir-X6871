# Fenrir Architecture & Exploitation Mechanics

## 1. MediaTek Boot Chain Anatomy

The boot process of modern MediaTek Dimensity SoCs (such as the Dimensity 8200 Ultimate / `MT6895` / `MT6896`) is divided into distinct execution stages spanning multiple privilege levels (EL3, EL2, EL1, EL0):

```
+-------------------------------------------------------------+
| BootROM (BL1) - Mask ROM in SoC silicon (EL3 Secure)        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Preloader (BL2 / BL2_EXT) - SRAM / DRAM Init (EL3 Secure)   |
| - Verifies partition signatures via Container v2 engine     |
| - Parses LittleKernel (lk) container cert1 & cert2          |
+-------------------------------------------------------------+
                              |
                              +-------------------------------+
                              |                               |
                              v                               v
+-----------------------------------+       +-----------------------------------+
| ATF (BL31) - EL3 Secure Monitor   |       | TEE (BL32) - Secure OS (EL1-S)    |
| - Handles SMC traps & PSCI        |       | - Microtrust / Trustonic TEE      |
+-----------------------------------+       | - Keymint, Gatekeeper, WeAreRoot  |
                              |             +-----------------------------------+
                              |                               ^
                              | (SMC Call 2 Handshake)        |
                              +-------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| LittleKernel (BL33 / LK) - Bootloader (EL1 Non-Secure)      |
| - Base: 0xFFFF000050F00000                                  |
| - Initializes display, USB fastboot, PMIC, storage          |
| - Implements Android Verified Boot (AVB 2.0)                |
| - Transmits Root of Trust to TEE via SMC Call 2             |
| - Prepares ATAGS / Devicetree / Kernel cmdline              |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Linux Kernel (EL1 Non-Secure) + Android Init (EL0)          |
| - Mounts dm-verity partitions                               |
| - vold initializes FBE (File-Based Encryption) user keys    |
+-------------------------------------------------------------+
```

---

## 2. MediaTek Container v2 Layout

Partitions loaded by the Preloader (such as `lk`, `tee`, `gz`, `aee`) are packaged in the proprietary MediaTek Image Container v2 format. The binary structure contains:

```
+-------------------------------------------------------------+
| Container Header (512 bytes / 0x200)                        |
| - Magic: 0x88168858                                         |
| - Tool version, alignment, partition count, metadata        |
+-------------------------------------------------------------+
| Partition 0 Header & Executable Payload                     |
| - Memory address: 0xFFFF000050F00000                        |
| - Code length, entry point offset                           |
| - Executable AArch64 machine code                           |
+-------------------------------------------------------------+
| cert1: Primary Signature Block                              |
| - OEM root certificate and signature chain                  |
+-------------------------------------------------------------+
| cert2: Secondary Integrity Block                            |
| - Image SHA-256 hash list for each partition                |
| - Public key descriptor and authentication tags             |
+-------------------------------------------------------------+
```

Preloader `BL2_EXT` maps each partition into DRAM, computes its cryptographic digest, and validates it against `cert2`. If validation fails, `BL2_EXT` triggers an immediate security halt (`0x701F: SECURE BOOT AUTHENTICATION FAILURE`) and holds the platform in emergency download (BROM/Preloader USB) mode.

---

## 3. The ASN.1 DER Header Override Vulnerability (`0xA0`)

### Vulnerability Mechanics
In standard MediaTek container verification, `BL2_EXT` parses `cert2` as a strict ASN.1 Distinguished Encoding Rules (DER) sequence (`0x30`). The parser evaluates:
1. Outer sequence structure and length.
2. Signer public key and cryptographic algorithm OID.
3. Message digest attribute containing partition SHA-256 hashes.
4. Digital signature matching the OEM public key.

However, the ASN.1 parser implementation in `BL2_EXT` contains a legacy compatibility path. When encountering an ASN.1 Context-Specific constructed tag `[0]` (`0xA0`), the parser treats the block as an encapsulated metadata override:
- It processes the inner partition hash table to compute and compare partition SHA-256 digests.
- It bypasses the RSA/ECDSA signature verification subroutine for the partition payload.

### The Override Implementation
Fenrir's `cert_bypass.py` replaces the stock `cert2` structure with a dynamically synthesized ASN.1 structure:
- First byte: `0xA0` (Context-Specific Tag `[0]`).
- Encoded payload: The exact SHA-256 digest of our modified LittleKernel payload partition.
- Trailing OEM attributes: Preserved to prevent parser boundary underflows.

When `BL2_EXT` parses this modified container:
1. It reads tag `0xA0`.
2. It hashes our modified LittleKernel data in DRAM.
3. It compares the computed hash against the SHA-256 hash specified in our `0xA0` block.
4. The hashes match exactly.
5. The signature validation step is bypassed.
6. `BL2_EXT` successfully jumps to LittleKernel entry at `0xFFFF000050F00000`.

> **Note on CertBypass Modes**: Wrapping the existing certificate (`CertBypass.WRAP`) corrupts the outer ASN.1 container length, causing `BL2_EXT` parser abort `0x701F`. Fenrir strictly uses `CertBypass.OVERRIDE`, writing the `0xA0` block directly over the partition's `cert2` storage.

---

## 4. Stage 1 Execution Environment & Pivot Hook

### LittleKernel Memory Layout (MT6895)
On the Dimensity 8200 Ultimate, LittleKernel executes with the following virtual memory map:

| Address Range | Size | Description |
| :--- | :--- | :--- |
| `0xFFFF000050F00000` | `0x2800` (10 KB) | Executable entry header, vector tables |
| `0xFFFF000050F02800` | `0x0800` (2 KB) | **Stage 1 Payload Space** (Executable Padding) |
| `0xFFFF000050F03000` | `0xD0000` (832 KB) | LittleKernel `.text` and `.rodata` |
| `0xFFFF000050FD5000` | `0x20000` (128 KB) | LittleKernel `.data` and `.bss` |
| `0xFFFF000050FE4968` | 1 byte | `g_boot_mode` global boot mode variable |
| `0xFFFF000050FEA6B8` | - | `kernel_aspace` page table root |

### The Pivot Hook
At virtual address `0xFFFF000050F11750`, LittleKernel completes `boot_mode_check()` and prepares to initialize hardware drivers. Fenrir overwrites this instruction with:
```armasm
bl    0xffff000050f02800    ; Machine code: 2C C4 FF 97
```

### Stage 1 Payload Execution
When control jumps to `0xFFFF000050F02800`:
1. **Bare-metal Context**: EL1 non-secure, MMU active, identity-mapped virtual addresses.
2. **Fastboot Handler Registration**: Calls fastboot handler setup at `0xFFFF000050F7D684` and registers custom fastboot commands.
3. **Boot Mode Handling**: When Fastboot mode is requested (via `adb reboot bootloader` or recovery), ensures `BOOT_MODE_FASTBOOT` (`99` / `0x63`) is written to `g_boot_mode` (`0xFFFF000050FE4968`) and secondary buffer (`0xFFFF000050FD5510`).
4. **Register Preservation**: Saves and restores `x29`, `x30`, and standard parameter registers.
5. **Return**: Issues `ret` to resume standard LittleKernel initialization.

---

## 5. LittleKernel Runtime Binary Patches

Fenrir applies 27 binary patches to LittleKernel to eliminate security checks, warning delays, and command-line restrictions:

| Patch Identifier | Target Offset | Description |
| :--- | :--- | :--- |
| `spoof_sboot_state` | Variable | Forces secure boot state to report `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP`. |
| `bypass_security_control` | Variable | Replaces conditional branches in fastboot command validation with `nop`. |
| `spoof_lock_state` | Variable | Forces `get_lock_state()` to unconditionally return `LKS_LOCK` (`4`). |
| `force_avb_device_locked` | Variable | Forces `androidboot.vbmeta.device_state` to `locked`. |
| `force_avb_green_cmdline` | Variable | Forces `androidboot.verifiedbootstate` to `green`. |
| `force_get_avb_boot_state`| Variable | Forces AVB internal query to return `AVB_BOOT_STATE_GREEN` (`0`). |
| `force_sec_boot_state` | Variable | Spoofs platform security boot state query. |
| `force_avb_load_slot_data`| Variable | Forces `avb_slot_verify()` to report success (`0`). |
| `force_avb_skip_cert_vfy` | Variable | NOPs out AVB certificate chain validation loop. |
| `force_avb_img_auth_0` | Variable | Forces image authentication callback to return `0` (success). |
| `force_img_auth_check_0` | Variable | Bypasses secondary signature check. |
| `force_avb_verity_mode_ignore_corruption` | Variable | Prevents AVB from entering red/halt state on verity failure. |
| `dont_relock_seccfg` | Variable | Prevents LittleKernel from re-locking or clearing `seccfg` partition. |
| `disable_ap_watchdog` | Variable | Disables Application Processor hardware watchdog timer. |
| `disable_ap_watchdog_doe`| Variable | Disables secondary hardware watchdog timer. |
| `neutralize_orange_warning_screen` | Variable | NOPs out the 5-second orange warning delay and screen render. |
| `neutralize_avb_warning_screen` | Variable | NOPs out AVB corrupt/unlocked splash screen. |
| `neutralize_orange_state_text_print` | Variable | NOPs out "Orange State: Your device cannot be trusted" UART string. |
| `avb_allow_verification_error` | Variable | Allows boot to proceed even when AVB reports verification error. |
| `enable_kernel_uart_log` | Variable | Appends `earlycon` and `printk.devkmsg=on` to kernel commandline. |
| `force_avb_public_key_trusted` | Variable | Injects test key into trusted public key validation table. |
| `force_avb_cmdline_always`| Variable | Forces AVB commandline options to append even on verify failure. |
| `force_avb_tee_root_of_trust` | Variable | Overwrites TEE SMC Call 2 arguments with GREEN state & OEM key hash. |
| `force_avb_cmdline_pubkey_digest` | Variable | Sets `androidboot.vbmeta.public_key_digest` to OEM stock digest. |
| `force_set_verified_boot_state_green` | Variable | Forces `g_verified_boot_state` global variable to `0`. |
| `force_set_avb_boot_state_green` | Variable | Forces secondary AVB boot state variable to `0`. |
| `force_get_lock_state_locked` | Variable | Forces lock state query in AVB to return `1` (locked). |

---

## 6. TrustZone (TEE) Root of Trust & FBE Key Derivation

### The Android 16 Failure Mode
On modern Android versions (specifically Android 16 on X6871-OP-16.3), File-Based Encryption (FBE) master keys are bound to the hardware Root of Trust. During boot, Android's `vold` daemon communicates with Keystore2 / Keymint, which executes inside the Trusted Execution Environment (TEE).

When LittleKernel prepares to launch the Linux kernel, it issues Secure Monitor Call 2 (SMC Fast Call) to TEE:
```armasm
mov    x0, #0xbf000002       ; TEE Root of Trust Registration SMC
mov    x1, #0                ; Sub-function
mov    x2, #1                ; Boot State: 1 = ORANGE (Unpatched LK default!)
ldr    x3, =pubkey_digest    ; Pointer to 32-byte public key SHA-256 digest
smc    #0
```

If LittleKernel passes `x2 = 1` (ORANGE), TEE records that the device is in an untrusted state. When userspace init launches:
1. `vold` attempts to derive encryption keys for `/data/misc/vold/user_keys/ce/0`.
2. TEE checks its internal Root of Trust table.
3. TEE refuses to release or derive keys because the boot state recorded at boot does not match the key policy (`init_user0_failed`, status 25).
4. `vold` aborts, triggering Android Rescue Party.
5. The device reboots into recovery with prompt: `"Can't load Android system. Your data may be corrupt."`

### The Fenrir Solution
Fenrir patches the SMC Call 2 argument loading sequence:
1. Replaces the instruction loading `x2` with `mov x2, #0` (`BOOT_STATE_GREEN`).
2. Overwrites the memory buffer referenced by `x3` with the exact 32-byte SHA-256 digest of the OEM stock public key:
   ```
   6F DB 7D D2 2B F8 7C 9D EE B6 27 B7 EA 71 D3 9A
   EB F6 98 54 77 9B 79 53 44 CC 93 58 BD 25 AF 2B
   ```
3. Replaces `g_verified_boot_state` assignments to unconditionally write `0`.

As a result, TEE registers a genuine Green, Locked boot session with the authentic OEM Root of Trust. Hardware-backed FBE key derivation succeeds, and Android userspace boots cleanly.

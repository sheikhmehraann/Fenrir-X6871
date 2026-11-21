# Fenrir: MediaTek LittleKernel (LK) Exploitation & AVB Modification Framework

## Abstract
Fenrir is a low-level bootloader research framework and payload injection toolkit targeting MediaTek Dimensity platforms utilizing the MediaTek Container v2 format. The framework exploits an ASN.1 DER parser context handling vulnerability in the Preloader `BL2_EXT` certificate verification engine, redirecting execution into a custom multi-stage AArch64 payload before platform hardware initialization.

In addition to custom code execution, Fenrir provides an automated in-memory binary patching engine that intercepts LittleKernel runtime security enforcement, Android Verified Boot (AVB) state propagation, and TrustZone (TEE) Root of Trust synchronization. This enables booting modified or custom system images with `verifiedbootstate=green` and `device_state=locked` while preserving hardware-backed File-Based Encryption (FBE) under Android 14, 15, and 16.

---

## Target Architecture & Verified Devices

| Parameter | Specification |
| :--- | :--- |
| **Reference Device** | Infinix GT 20 Pro (`X6871`) |
| **SoC Platform** | MediaTek Dimensity 8200 Ultimate (`MT6895`) |
| **Instruction Set** | AArch64 (ARMv8.2-A / ARMv9-A) |
| **Operating Systems** | Android 16 |
| **Container Format** | MediaTek Image Container v2 (512-byte `ImageHeader`, dual `cert1`/`cert2`) |
| **Target Partition** | `lk` / `lk_a` / `lk_b` |
| **LittleKernel Base** | `0xFFFF000050F00000` |
| **Stage 1 Target** | `0xFFFF000050F02800` (LK file offset `0x2800`) |
| **Execution Hook (Pivot)** | `0xFFFF000050F11750` (`bl #0x2800`) |
| **Certificate Override** | ASN.1 Context-Specific Tag `[0]` (`0xA0`) DER block injection |

---

## Core Mechanisms

### 1. Preloader Container v2 Certificate Bypass
MediaTek Secure Boot validates partition integrity in the Preloader stage (`BL2_EXT`). The container format packs an executable payload followed by two certificate blobs:
- `cert1`: Primary signature block.
- `cert2`: Secondary certificate block containing partition image hashes and OEM public key descriptors.

The Preloader DER parser evaluates the first tag of `cert2`. When the parser encounters an ASN.1 Context-Specific constructed tag `[0]` (`0xA0`) formatted with custom partition digest descriptors, the signature validation branch is bypassed while recalculating valid image SHA-256 hashes. Fenrir's `cert_bypass.py` synthesizes this ASN.1 structure, enabling modified LittleKernel binaries to pass Preloader authentication without causing secure boot panics (`0x701f`).

### 2. Stage 1 Execution Pivot
Fenrir hooks LittleKernel immediately after the platform `boot_mode_check()` subroutine at virtual address `0xFFFF000050F11750`. The stock branch instruction is overwritten with a direct branch-with-link (`bl #0x2800`) to the Stage 1 payload situated in executable padding at `0xFFFF000050F02800`.

Stage 1 executes bare-metal in EL1 context before hardware drivers and platform subsystems are initialized:
- Queries PMIC hardware registers via `detect_key(FASTBOOT_KEY_INDEX)`.
- If the physical Volume Down key is held down during boot, forces `BOOT_MODE_FASTBOOT` (`99` / `0x63`).
- Initializes fastboot handler structures and registers custom command hooks.
- Restores overwritten registers and returns cleanly to LittleKernel main flow.

### 3. Android Verified Boot (AVB) & Green State Spoofing
Modern Android systems (Android 14+) require strict consistency across boot states:
- `androidboot.verifiedbootstate=green`
- `androidboot.locked=1`
- `androidboot.vbmeta.device_state=locked`

Simple kernel command-line spoofing is insufficient because userspace init and `vold` verify that dm-verity and TrustZone report matching states. Fenrir patches 27 distinct verification routines inside LittleKernel, ensuring:
- `avb_slot_verify()` reports `AVB_SLOT_VERIFY_RESULT_OK` regardless of hash mismatches.
- Certificate chain verification inside LittleKernel is skipped (`force_avb_skip_cert_vfy`).
- Image authentication callbacks unconditionally return success (`0`).
- Orange warning splash screens and delay timers are neutralized.

### 4. TrustZone (TEE) Root of Trust Synchronization
Under Android 14+, Keymint and `vold` derive hardware-backed master encryption keys (`user0`) by querying the Trusted Execution Environment (Microtrust / Trustonic TEE) via Secure Monitor Calls. LittleKernel passes the verified boot state and public key digest to TEE via SMC Call 2:
- Register `x0`: `0xBF000002` (Fast SMC Call 2)
- Register `x1`: Sub-function ID
- Register `x2`: Verified Boot State (`0` = GREEN, `1` = ORANGE, `2` = YELLOW)
- Register `x3`: Public key digest pointer

If an unpatched LittleKernel passes `x2 = 1` (ORANGE) to TEE while the kernel command-line claims `green`, or if an unknown public key digest is registered, TEE rejects FBE key derivation, resulting in recovery bootloops (`vold: Failed to prepare /data/misc/vold/user_keys: No such file or directory` status 25).

Fenrir implements:
- `force_avb_tee_root_of_trust`: Intercepts the SMC call parameters, forcing `x2 = 0` (GREEN) and substituting the OEM stock public key digest (`6FDB7DD2...`).
- `force_set_verified_boot_state_green`: Overwrites LittleKernel internal global state `g_verified_boot_state` to `0`.
- Result: Hardware-backed FBE encryption operates seamlessly across locked, unlocked, or custom bootloader states.

### 5. DSU & Custom Partition dm-verity Handling
Setting `veritymode=disabled` in the kernel command-line crashes Android userspace init (`NONRST_REG2: 0x2C002000`). To support Dynamic System Updates (DSU) and custom partition images (e.g., GSI):
- Fenrir keeps `veritymode=enforcing` in the kernel command-line.
- Fenrir utilizes an AVB VBMeta image configured with `flags = 2` (`AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED`).
- LittleKernel honors `flags = 2` and instructs the kernel to skip dm-verity hashtree validation without altering userspace security posture.

---

## Repository Structure

```
Fenrir/
├── bin/
│   └── x6871.bin                  # Reference stock LittleKernel image (lk.img)
├── docs/
│   ├── ARCHITECTURE.md            # Technical specifications of MTK boot chain & exploits
│   ├── DEVICE_PORTING.md          # Guide for reverse engineering & porting new SoCs
│   └── DSU_AND_VERITY.md          # dm-verity, disabled vbmeta, and DSU operational notes
├── injector/
│   ├── __init__.py                # Package initialization
│   ├── cert_bypass.py             # ASN.1 DER cert2 override engine (tag 0xA0)
│   ├── device.py                  # Device profile abstraction class
│   ├── devices.py                 # Device catalog & 27 LittleKernel binary patches
│   ├── inject.py                  # CLI entry point
│   ├── injector.py                # MediaTek container parser & injection manager
│   ├── patch_utils.py             # Hex pattern search & binary substitution engine
│   ├── stage.py                   # Stage & Patch definitions (AArch64 injection context)
│   └── utils.py                   # AArch64 branch-link (BL) encoder & padding
├── payload/
│   ├── Makefile                   # GNU Make rules for AArch64 bare-metal payloads
│   ├── README.md                  # Payload stage architecture notes
│   ├── build_payload.py           # Standalone payload generator (bytecode fallback)
│   ├── build/                     # Compiled payload artifacts
│   │   └── x6871/stage1/
│   │       └── payload.bin        # Verified 728-byte Stage 1 binary
│   ├── common/                    # Shared bare-metal headers & stubs
│   │   ├── arm64.h                # AArch64 register & system instruction macros
│   │   ├── common.c / common.h    # Hardware access stubs
│   │   ├── debug.c / debug.h      # LittleKernel dprintf / video_printf wrappers
│   │   ├── fastboot.c / .h        # Fastboot command table & hooks
│   │   ├── linker.x               # Linker script for stage relocations
│   │   ├── mmu.c / mmu.h          # AArch64 MMU page table walker & unprotect
│   │   ├── string.c / string.h    # Freestanding string primitives
│   │   └── types.h                # Integer & boolean type definitions
│   ├── devices/
│   │   └── x6871.h                # Hardware addresses & offsets for Infinix GT 20 Pro
│   └── stage1/
│       ├── stage1.S               # AArch64 assembly entry & register setup
│       └── stage1.c               # C entry point & hardware key detection
├── tools/
│   ├── make_disabled_vbmeta.py    # Generates flags=2 VBMeta images signed with testkey
│   └── verify_lk.py               # Automated image verification test suite
├── avbtool.py                     # AOSP Android Verified Boot signing utility
├── build.ps1                      # Windows PowerShell build & injection script
├── build.sh                       # Linux / WSL build & injection script
├── flash.ps1                      # Windows PowerShell fastboot flashing script
├── flash.sh                       # Linux / WSL fastboot flashing script
├── inject.ps1                     # Windows PowerShell injection CLI wrapper
├── inject.sh                      # Linux / WSL injection CLI wrapper
├── LICENSE                        # GNU General Public License v3.0
├── requirements.txt               # Python package dependencies
├── testkey_rsa2048.pem            # Standard 2048-bit RSA test key for AVB signing
└── x6871-fenrir.bin               # Prebuilt verified LittleKernel image for X6871
```

---

## Installation & Prerequisites

### Python Dependencies
Python 3.10 or newer is required. Install required packages:
```bash
pip install -r requirements.txt
```
Contents of `requirements.txt`:
- `liblk>=3.2`: MediaTek LittleKernel container serializer and parser.
- `pyasn1>=0.5.0`: ASN.1 DER encoder for certificate generation.
- `cryptography>=3.4.0`: Cryptographic primitives for AVB verification.

### Toolchain (Optional for Payload Recompilation)
The repository includes a pre-assembled, verified 728-byte Stage 1 payload (`payload/build/x6871/stage1/payload.bin`). If modifying the payload C or Assembly source code, an AArch64 bare-metal cross compiler is required:
- Ubuntu/Debian: `sudo apt-get install gcc-aarch64-linux-gnu` or `gcc-aarch64-none-elf`
- Arch Linux: `sudo pacman -S aarch64-none-elf-gcc`
- Windows: Pre-compiled payload is used automatically by `build_payload.py`.

---

## Build Instructions

### Linux / WSL

1. **Standard Build (Payload + Injection)**:
   ```bash
   ./build.sh x6871
   ```
   This compiles the payload (or executes `build_payload.py`), injects Stage 1 into `bin/x6871.bin`, applies all 27 LittleKernel runtime patches, re-signs the container with `0xA0` cert2 override, and outputs `x6871-fenrir.bin`.

2. **Targeting Custom Bootloader Image**:
   ```bash
   ./build.sh x6871 /path/to/extracted/stock_lk.img
   ```

3. **Manual CLI Injection**:
   ```bash
   ./inject.sh x6871 bin/x6871.bin -o x6871-fenrir.bin -p payload/build
   ```

### Windows (PowerShell)

1. **Standard Build**:
   ```powershell
   .\build.ps1 -Device x6871 -Bootloader bin\x6871.bin
   ```

2. **Manual CLI Injection**:
   ```powershell
   .\inject.ps1 x6871 bin\x6871.bin -o x6871-fenrir.bin -p payload\build
   ```

---

## Verification

Before flashing any image to hardware, validate the output using the automated verification engine:
```bash
python tools/verify_lk.py x6871-fenrir.bin x6871
```

The verification tool checks:
1. Container integrity and partition boundary definitions.
2. Cert2 begins with the `0xA0` ASN.1 DER override header.
3. Pivot hook at `0xFFFF000050F11750` branches to Stage 1 at `0xFFFF000050F02800` (`bl #0x2800`).
4. All 27 LittleKernel security patches are present in the partition data.

Expected output:
```
[*] Verifying LittleKernel image: x6871-fenrir.bin (3182832 bytes)
[+] VERIFIED: cert2 contains Fenrir 0xA0 ASN.1 override header (1137 bytes)
[+] VERIFIED: Stage 1 pivot hook at 0xFFFF000050F11750 -> BL 0xFFFF000050F02800
[+] Patches verified: 27/27 present.
[+] Image verification PASSED. Verified ready for hardware deployment.
```

---

## Flashing to Hardware

### Step 1: Boot Device to Fastboot
Power down the device, hold `Volume Down` and connect the USB cable, or issue:
```bash
adb reboot bootloader
```

### Step 2: Flash LittleKernel
Execute the flashing script (handles slot detection and flashing to active slot):
```bash
# Linux / WSL
./flash.sh x6871-fenrir.bin

# Windows PowerShell
.\flash.ps1 -Image x6871-fenrir.bin
```

Or execute fastboot commands manually:
```bash
fastboot flash lk_a x6871-fenrir.bin
fastboot flash lk_b x6871-fenrir.bin
```

### Step 3: Flash Disabled VBMeta (Required for Custom System / DSU / GSI)
If booting custom partitions or modifying system images, flash an AVB VBMeta image with `flags = 2`:
```bash
# Generate disabled vbmeta from stock
python tools/make_disabled_vbmeta.py -s /path/to/stock_vbmeta.img -o vbmeta_disabled.img

# Flash to both slots
fastboot flash vbmeta_a vbmeta_disabled.img
fastboot flash vbmeta_b vbmeta_disabled.img
```

### Step 4: First Boot / Data Format Requirement
If migrating from an existing installation where `/data` was encrypted under an unpatched (ORANGE/UNLOCKED) state, Android's Keymint and `vold` will detect the new GREEN/LOCKED Root of Trust and fail to decrypt old keys (`init_user0_failed`). A one-time format is required:
```bash
fastboot -w
fastboot reboot
```
Subsequent boots will generate new hardware-backed FBE keys synchronized with the Green Root of Trust.

---

## Hardware Emergency Fastboot Access

If the device encounters a bootloop during userspace testing or custom kernel development, Stage 1 provides unconditional hardware recovery access:
1. Power off device (or force reboot by holding Power + Volume Up for 10 seconds).
2. Hold **Volume Down**.
3. Stage 1 intercepts the boot mode check before platform initialization and forces Fastboot mode (`99`).
4. The device boots directly into Fastboot, bypassing kernel crashes and watchdog resets.

---

## Reference Hashes (Infinix GT 20 Pro X6871)

- **Stock `lk.img`**:
  - Size: `3,182,736` bytes
  - SHA-256: `E98E6988EB13BE5BC8CF0B5668BBE19888CE8CD347A221990AC6F88E75C419F7`
- **Fenrir Patched `x6871-fenrir.bin`**:
  - Size: `3,182,832` bytes
  - SHA-256: `FD712A72CC8AC1E7C387FD0F1EBDD735616C21D02F13A55826DE9D45B2B5A3E3`

---

## Documentation
- [Architecture & Exploit Mechanics](docs/ARCHITECTURE.md)
- [Device Porting Guide](docs/DEVICE_PORTING.md)
- [DSU & dm-verity Management](docs/DSU_AND_VERITY.md)

---

## License
Fenrir is released under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for complete terms.

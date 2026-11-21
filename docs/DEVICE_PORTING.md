# Device Porting Guide: Adding Support for New MediaTek SoCs

This guide describes the reverse-engineering methodology required to port Fenrir to other MediaTek SoCs (e.g., Dimensity 8050, 8100, 8200, 9000, 9200, 9300, Helio G99).

---

## 1. Extracting the Stock Bootloader

Acquire the stock `lk.img` (or `bootloader.img`) from an official stock ROM or OTA update. Verify the container structure using `liblk`:

```python
from liblk.image import LkImage

img = LkImage("lk.img")
for name, part in img.partitions.items():
    print(f"Partition: {name}")
    print(f"  Memory Address: 0x{part.header.memory_address:016X}")
    print(f"  Size:           {len(part.data)} bytes")
    print(f"  Cert1:          {len(part.cert1.data) if part.cert1 else 0} bytes")
    print(f"  Cert2:          {len(part.cert2.data) if part.cert2 else 0} bytes")
```

Expected output should confirm a container with partitions such as `lk`, `lk_main_dtb`, and dual certificates (`cert1`/`cert2`).

---

## 2. Disassembly & Static Analysis Setup

Load the raw partition data of `lk` (extracted via `img.partitions['lk'].data`) into Ghidra, IDA Pro, or Binary Ninja:
- **Architecture**: AArch64 (ARMv8-A or ARMv9-A little-endian).
- **Base Address**: Use `part.header.memory_address` (e.g., `0xFFFF000050F00000`).

---

## 3. Locating Critical Offsets & Symbols

### A. Stage 1 Payload Area
Locate an alignment padding region filled with zeros or NOPs near the start of the binary (typically between `0x2000` and `0x3000`).
- On `X6871`, file offset `0x2800` (`0xFFFF000050F02800`) provides 2 KB of executable space.
- Verify that this space is mapped with Read+Execute permissions in LittleKernel's initial MMU tables.

### B. Execution Pivot Hook Site
Search for string references to `"boot_mode_check"` or `"boot mode:"`:
1. Navigate to the function responsible for reading hardware straps and registers.
2. Locate the instruction immediately following the boot mode assignment (e.g., `str w0, [x19, #0x28]`).
3. Note the virtual address of this instruction. This becomes `PIVOT_ADDR`.
4. Overwriting this instruction with `bl STAGE1_BASE` redirects control into Stage 1 before platform drivers load.

### C. Hardware Key Detection (`detect_key`)
Search for cross-references to key code constants:
- Volume Down key index is typically `1` or `2`.
- In LittleKernel source, the prototype is: `bool mtk_detect_key(uint32_t key_index)`.
- Disassemble the caller and note the address of the function.

### D. Global Boot Mode Address (`g_boot_mode`)
Trace where `boot_mode_check()` writes the selected boot mode integer:
- `0` = Normal boot
- `1` = Recovery mode
- `2` or `99` (`0x63`) = Fastboot mode
- On `X6871`, this is located at `0xFFFF000050FE4968`.

### E. Fastboot Handler Routines
Search for string references:
- `"fastboot_init"` -> locates `FASTBOOT_INIT_ADDR`
- `"fastboot_register"` -> locates `FASTBOOT_REGISTER_ADDR`
- `"fastboot_okay"` / `"fastboot_fail"` -> locates response stubs
- `FASTBOOT_TARGET_BUF` -> global buffer where fastboot stores incoming download payloads.

---

## 4. Reverse Engineering the 27 LittleKernel Patches

Fenrir's patching engine uses byte-pattern matching with wildcard capabilities. Below are the key heuristics for identifying target subroutines:

### 1. `spoof_sboot_state`
- **String search**: `"sboot state:"` or `"sboot"`
- **Pattern**: Function loading security attributes and returning flags in `w0`.
- **Target**: Force function to return `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` (`w0 = 1`).

### 2. `spoof_lock_state`
- **String search**: `"get_lock_state"` or `"lock_state:"`
- **Target**: Force function to unconditionally return `LKS_LOCK` (`4`).

### 3. `force_avb_tee_root_of_trust` (Critical for FBE)
- **Heuristic**: Search for the immediate constant `0xBF000002` (or `0x82000002`), which is the Fast SMC Call ID for MediaTek TEE Root of Trust registration.
- **Disassembly review**:
  ```armasm
  mov    w2, w20         ; Boot state (1 = ORANGE)
  ldr    x3, [sp, #0x10] ; Public key digest buffer
  smc    #0
  ```
- **Replacement**: Overwrite the `w2` setup with `mov w2, #0` (`GREEN`), and copy the 32-byte OEM public key hash over the digest buffer.

### 4. `force_set_verified_boot_state_green`
- **String search**: `"verifiedbootstate"`
- **Heuristic**: Locate where `g_verified_boot_state` is set based on AVB slot verify results.
- **Replacement**: Force unconditional write of `0` (`GREEN`).

### 5. `disable_ap_watchdog`
- **Heuristic**: Search for MMIO writes to watchdog control registers (typically base `0x10007000` or `0x1C007000`).
- **Replacement**: Neutralize watchdog enable bits (`NOP` or early return).

---

## 5. Adding the Device Definition

### Step A: Create Header File
Create `payload/devices/<device_codename>.h`:
```c
#pragma once

#define DEVICE_NAME "MY_DEVICE"

#define STAGE1_BASE                  0xffff000050f02800
#define PIVOT_ADDR                   0xffff000050f11750
#define BOOT_MODE_ADDR               0xffff000050fe4968
#define BOOT_MODE_FASTBOOT           99

#define DETECT_KEY_ADDR              0xffff000050f6a120
#define FASTBOOT_KEY_INDEX           1

#define FASTBOOT_INIT_ADDR           0xffff000050f7d684
#define FASTBOOT_HANDLER_ADDR        0xffff000050f80ca0
#define FASTBOOT_TARGET_BUF          0xffff000050fd5510
```

### Step B: Register Device in `injector/devices.py`
Add the device entry with its unique binary patterns:
```python
Device(
    'my_device',
    'My Device Name',
    {
        'stage1': PayloadStage(
            'stage1',
            0xFFFF000050F02800,
            0xFFFF000050F11750,
            description='Stage 1 hardware key handler',
        ),
        'spoof_sboot_state': PatchStage(
            'spoof_sboot_state',
            pattern='<extracted_hex_pattern>',
            replacement='<replacement_hex>',
            match_mode=MatchMode.FIRST,
            partition='lk',
        ),
        # ... Add remaining patches ...
    },
    cert_bypass=CertBypass.OVERRIDE,
)
```

---

## 6. Testing & Validation Procedure

1. **Verify Binary**:
   Run the test suite on your output:
   ```bash
   python tools/verify_lk.py my_device-fenrir.bin my_device
   ```
2. **Flash to Inactive Slot First**:
   If the device supports A/B slots, flash to the inactive slot (e.g., `lk_b` if currently on `a`), switch active slot via `fastboot set_active b`, and attempt boot.
3. **Emergency Fallback**:
   Always have a BROM-level restore method ready (MTKClient or authorized SP Flash Tool) in the event of an offset calculation error or watchdog panic.

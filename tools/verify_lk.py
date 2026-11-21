#!/usr/bin/env python3
"""
Fenrir LittleKernel Verification Engine
Validates partition layout, cert2 ASN.1 override, stage 1 pivot hook,
and all LittleKernel runtime security patches.
"""

import sys
from pathlib import Path

# Add injector to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "injector"))

from liblk.image import LkImage
from devices import DEVICES


def verify_image(image_path: Path, device_name: str = "x6871") -> bool:
    if not image_path.exists():
        print(f"[-] Image not found: {image_path}")
        return False

    print(f"[*] Verifying LittleKernel image: {image_path} ({image_path.stat().st_size} bytes)")
    image = LkImage(str(image_path))

    if 'lk' not in image.partitions:
        print("[-] Partition 'lk' missing from container!")
        return False

    lk = image.partitions['lk']
    success = True

    # 1. Verify cert2 ASN.1 override
    if not lk.cert2:
        print("[-] Error: cert2 missing from lk partition!")
        success = False
    elif lk.cert2.data[0] != 0xA0:
        print(f"[-] Error: cert2 does not start with ASN.1 0xA0 tag (got 0x{lk.cert2.data[0]:02X})")
        success = False
    else:
        print(f"[+] VERIFIED: cert2 contains Fenrir 0xA0 ASN.1 override header ({len(lk.cert2.data)} bytes)")

    # Find device definition
    target_dev = None
    for dev in DEVICES:
        if dev.name.lower() == device_name.lower():
            target_dev = dev
            break

    if not target_dev:
        print(f"[-] Device '{device_name}' not found in catalog.")
        return False

    # 2. Verify stage 1 pivot hook
    base_addr = lk.lk_address or lk.header.memory_address
    stage1 = target_dev.stages.get('stage1')
    if stage1:
        pivot_off = stage1.pivot_addr - base_addr
        pivot_bytes = lk.data[pivot_off:pivot_off + 4]
        # In ARM64, BL to 0x2800 from 0x11750 is 0x2C, 0xC4, 0xFF, 0x97 (0x97FFC42C)
        if pivot_bytes == b"\x2c\xc4\xff\x97":
            print(f"[+] VERIFIED: Stage 1 pivot hook at 0x{stage1.pivot_addr:X} -> BL 0x{stage1.base_addr:X}")
        else:
            print(f"[-] Error: Pivot hook instruction mismatch at 0x{stage1.pivot_addr:X}: {pivot_bytes.hex()}")
            success = False

    # 3. Verify all patches
    lk_data = bytes(lk.data)
    total_patches = 0
    matched_patches = 0

    for name, stage in target_dev.stages.items():
        if name == 'stage1':
            continue
        total_patches += 1
        repl = stage.replacement
        if repl in lk_data:
            matched_patches += 1
        else:
            print(f"[-] Warning: Patch '{name}' replacement bytecode not found in image!")
            success = False

    print(f"[+] Patches verified: {matched_patches}/{total_patches} present.")

    if success and matched_patches == total_patches:
        print(f"[+] Image verification PASSED. Verified ready for hardware deployment.")
        return True
    else:
        print(f"[-] Image verification FAILED.")
        return False


def main():
    if len(sys.argv) < 2:
        default_img = REPO_ROOT / "x6871-fenrir.bin"
        if default_img.exists():
            target = default_img
        else:
            print(f"Usage: python verify_lk.py <path_to_lk.img> [device]")
            return 1
    else:
        target = Path(sys.argv[1])

    device = sys.argv[2] if len(sys.argv) > 2 else "x6871"
    ok = verify_image(target, device)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

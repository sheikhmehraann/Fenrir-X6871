#!/usr/bin/env python3
"""Verification script for Infinix GT 20 Pro (X6871) patched LK images."""

import sys, os, struct, hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0"))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0", "core"))

from liblk.image import LkImage

def calc_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify_image(label: str, stock_path: str, patched_path: str, expected_patches: list):
    print(f"\nVerifying {label}...")
    if not os.path.exists(patched_path):
        print(f"  Error: {patched_path} does not exist.")
        return False
    if not os.path.exists(stock_path):
        print(f"  Error: {stock_path} does not exist.")
        return False

    with open(stock_path, 'rb') as f:
        stock_raw = f.read()
    with open(patched_path, 'rb') as f:
        patched_raw = f.read()

    print(f"  Stock:   {len(stock_raw):,} bytes | SHA256: {calc_sha256(stock_raw)}")
    print(f"  Patched: {len(patched_raw):,} bytes | SHA256: {calc_sha256(patched_raw)}")

    magic = struct.unpack('<I', patched_raw[:4])[0]
    if magic != 0x58881688:
        print(f"  Fail: Invalid GFH magic (got 0x{magic:08x}, expected 0x58881688)")
        return False
    print(f"  GFH magic: 0x{magic:08x} (valid)")

    patched_img = LkImage(patched_path)
    stock_img = LkImage(stock_path)

    for part in ['lk', 'bl2_ext', 'aee', 'lk_main_dtb']:
        if part not in patched_img.partitions:
            print(f"  Fail: Missing partition {part}")
            return False
        p_len = len(patched_img.partitions[part].data)
        print(f"  Partition '{part}': {p_len:,} bytes")

    # Check that patches match in partition data
    all_ok = True
    for item in expected_patches:
        part_name = item['part']
        part_data = patched_img.partitions[part_name].data
        needle = bytes.fromhex(item['hex'].replace(' ', ''))
        count = part_data.count(needle)
        name = item['name']
        if count >= item['min_count']:
            print(f"  [PASS] {name} ({part_name}): {count} hit(s)")
        else:
            print(f"  [FAIL] {name} ({part_name}): found {count}, expected at least {item['min_count']}")
            all_ok = False

    return all_ok

def main():
    a15_stock = os.path.join(BASE_DIR, "Fenrir-X6871", "A15", "lk-stock-backup.img")
    a15_patched = os.path.join(BASE_DIR, "Fenrir-X6871", "A15", "lk-patched.img")
    a14_stock = os.path.join(BASE_DIR, "Fenrir-X6871", "A14", "lk-stock-backup.img")
    a14_patched = os.path.join(BASE_DIR, "Fenrir-X6871", "A14", "lk-patched.img")

    a15_checks = [
        {'name': 'Force Green State', 'part': 'lk', 'hex': '280300d01f7d09b9c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy Override', 'part': 'lk', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy (bl2_ext)', 'part': 'bl2_ext', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy (aee)', 'part': 'aee', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Spoof SBoot 0x222', 'part': 'lk', 'hex': '48048052080000b9', 'min_count': 2},
        {'name': 'Spoof Lock State (4)', 'part': 'lk', 'hex': '88008052080000b9', 'min_count': 1},
        {'name': 'Prevent Seccfg Relock', 'part': 'lk', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Vol Down Fastboot Jump', 'part': 'lk', 'hex': 'fbffff171f2003d5', 'min_count': 1},
    ]

    a14_checks = [
        {'name': 'Force Green State', 'part': 'lk', 'hex': '280300d01fad09b9c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy Override', 'part': 'lk', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy (bl2_ext)', 'part': 'bl2_ext', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Sec Vfy Policy (aee)', 'part': 'aee', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Spoof SBoot 0x222', 'part': 'lk', 'hex': '48048052080000b9', 'min_count': 2},
        {'name': 'Spoof Lock State (4)', 'part': 'lk', 'hex': '88008052080000b9', 'min_count': 1},
        {'name': 'Prevent Seccfg Relock', 'part': 'lk', 'hex': '00008052c0035fd6', 'min_count': 1},
        {'name': 'Vol Down Fastboot Jump', 'part': 'lk', 'hex': 'fdffff171f2003d5', 'min_count': 1},
    ]

    ok15 = verify_image("Android 15 (XOS 15)", a15_stock, a15_patched, a15_checks)
    ok14 = verify_image("Android 14 (XOS 14)", a14_stock, a14_patched, a14_checks)

    if ok15 and ok14:
        print("\nAll images verified successfully.")
        return 0
    else:
        print("\nVerification found errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

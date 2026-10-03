#!/usr/bin/env python3
"""Build script for Infinix GT 20 Pro (X6871) Android 15 patched LK."""

import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0"))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0", "core"))

from fenrir.engine import Engine, sha256
from devices.x6871 import X6871_A15

STOCK_A15 = os.path.join(BASE_DIR, "Fenrir-X6871", "A15", "lk-stock-backup.img")
OUTPUT_A15 = os.path.join(BASE_DIR, "Fenrir-X6871", "A15", "lk-patched.img")

print("Building Fenrir A15 LK for Infinix GT 20 Pro (X6871)...")

engine = Engine(STOCK_A15)
hits = engine.apply_profile(X6871_A15)
engine.auto_patch_policies()
engine.finalize_and_save(OUTPUT_A15, mode=X6871_A15.cert_mode)

for line in engine.report:
    print(f"  {line}")

out_sz = os.path.getsize(OUTPUT_A15)
out_h = sha256(open(OUTPUT_A15, 'rb').read())

print(f"\nBuild complete:")
print(f"  Output: {OUTPUT_A15}")
print(f"  Size:   {out_sz:,} bytes")
print(f"  SHA256: {out_h}")
print(f"\nFlash commands:")
print(f'  fastboot flash lk_a "{OUTPUT_A15}"')
print(f'  fastboot flash lk_b "{OUTPUT_A15}"')
print(f'  fastboot reboot recovery')

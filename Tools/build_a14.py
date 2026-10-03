#!/usr/bin/env python3
"""Build script for Infinix GT 20 Pro (X6871) Android 14 patched LK."""

import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0"))
sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0", "core"))

from fenrir.engine import Engine, sha256
from devices.x6871 import X6871_A14

STOCK_A14 = os.path.join(BASE_DIR, "Fenrir-X6871", "A14", "lk-stock-backup.img")
OUTPUT_A14 = os.path.join(BASE_DIR, "Fenrir-X6871", "A14", "lk-patched.img")

print("Building Fenrir A14 LK for Infinix GT 20 Pro (X6871)...")

engine = Engine(STOCK_A14)
hits = engine.apply_profile(X6871_A14)
engine.auto_patch_policies()
engine.finalize_and_save(OUTPUT_A14, mode=X6871_A14.cert_mode)

for line in engine.report:
    print(f"  {line}")

out_sz = os.path.getsize(OUTPUT_A14)
out_h = sha256(open(OUTPUT_A14, 'rb').read())

print(f"\nBuild complete:")
print(f"  Output: {OUTPUT_A14}")
print(f"  Size:   {out_sz:,} bytes")
print(f"  SHA256: {out_h}")
print(f"\nFlash commands:")
print(f'  fastboot flash lk_a "{OUTPUT_A14}"')
print(f'  fastboot flash lk_b "{OUTPUT_A14}"')
print(f'  fastboot reboot recovery')

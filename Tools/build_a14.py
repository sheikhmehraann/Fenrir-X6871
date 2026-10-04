#!/usr/bin/env python3
"""Build script for Infinix GT 20 Pro (X6871) Android 14 patched LK using Renkai."""

import sys, os

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOLS_DIR)
BASE_DIR = os.path.dirname(REPO_DIR)

# Prefer Renkai unified engine if present, with fallback to legacy engine
renkai_path = os.path.join(BASE_DIR, "Renkai")
if os.path.exists(renkai_path):
    sys.path.insert(0, renkai_path)
    import devices
    from renkai.engine import RenkaiEngine as Engine
    profile = devices.get_device_profile("x6871_a14")
else:
    sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0"))
    sys.path.insert(0, os.path.join(BASE_DIR, "Fenrir-2.0", "core"))
    from fenrir.engine import Engine
    from devices.x6871 import X6871_A14 as profile

STOCK_A14 = os.path.join(REPO_DIR, "A14", "lk-stock-backup.img")
OUTPUT_A14 = os.path.join(REPO_DIR, "A14", "lk-patched.img")

print("Building Renkai A14 LK for Infinix GT 20 Pro (X6871)...")

engine = Engine(STOCK_A14)
hits = engine.apply_profile(profile)
engine.auto_patch_policies()
engine.finalize_and_save(OUTPUT_A14, mode=profile.cert_mode)

for line in engine.report:
    print(f"  {line}")

import hashlib
out_sz = os.path.getsize(OUTPUT_A14)
with open(OUTPUT_A14, 'rb') as f:
    out_h = hashlib.sha256(f.read()).hexdigest()

print(f"\nBuild complete:")
print(f"  Output: {OUTPUT_A14}")
print(f"  Size:   {out_sz:,} bytes")
print(f"  SHA256: {out_h}")
print(f"\nFlash commands:")
print(f'  fastboot flash lk_a "{OUTPUT_A14}"')
print(f'  fastboot flash lk_b "{OUTPUT_A14}"')
print(f'  fastboot reboot recovery')

#!/usr/bin/env python3
"""
DEFINITIVE BUILD v3 — Fenrir X6871 Stock A14 LK
Applies ALL patches including the now-located force_green_state setter.

Patches:
1. sec_get_vfy_policy      — MOV W0,#0; RET (kill verification)
2. force_green_state_sboot  — MOV W8,#0x222; STR; MOV W0,#0; RET (force sboot state)  
3. force_green_state_setter — STR W0 -> STR WZR at lk+0x050fac (ACTUAL green state writer)
4. bypass_security_control  — B.NE -> NOP
5. spoof_lock_state         — MOV W8,#4; STR; MOV W0,#0; RET
6. dont_relock_seccfg       — MOV W0,#0; RET; NOP×3
7. avb_allow_verification_error — MOV W22,WZR -> MOV W22,#1
"""
import sys, os, struct, hashlib
sys.path.insert(0, os.path.join(r'C:\Users\Admin\Videos\Project-2\fenrir-main-mehraan', 'injector'))

from liblk.image import LkImage
from cert_bypass import CertBypass, apply_cert_bypass

STOCK_A14 = r'C:\Users\Admin\Videos\Project-2\Stock-imgs-A14\lk.img'
OUTPUT = r'C:\Users\Admin\Videos\Project-2\Stock-imgs-A14\lk-A14-fenrir-v3.img'

def hex_to_bytes(s): return bytes.fromhex(s.replace(' ', ''))
def sha256(d): return hashlib.sha256(d).hexdigest()

print("="*70)
print("  FENRIR X6871 A14 — DEFINITIVE BUILD v3")
print("  All patches including force_green_state setter")
print("="*70)

img = LkImage(STOCK_A14)

# Compute trailing
region_end = 0
for partition in img.partitions.values():
    region_end = max(region_end, partition.end_offset)
    for cert in partition.certs:
        region_end = max(region_end, cert.end_offset)
trailing = bytes(img.contents[region_end:])

# ============================================================================
# PATCH 0 (CRITICAL): force_green_state SETTER — STR W0 -> STR WZR
# Only in 'lk' partition, at offset 0x050fac
# Pattern:  28 03 00 d0 00 ad 09 b9 c0 03 5f d6
# Patched:  28 03 00 d0 1f ad 09 b9 c0 03 5f d6
# ============================================================================
print("\n[0] force_green_state (SETTER) — STR W0 -> STR WZR")
GREEN_SETTER_PATTERN = hex_to_bytes('28 03 00 d0 00 ad 09 b9 c0 03 5f d6')
GREEN_SETTER_REPLACE = hex_to_bytes('28 03 00 d0 1f ad 09 b9 c0 03 5f d6')

lk_data = bytearray(img.partitions['lk'].data)
idx = lk_data.find(GREEN_SETTER_PATTERN)
if idx >= 0:
    lk_data[idx:idx+len(GREEN_SETTER_REPLACE)] = GREEN_SETTER_REPLACE
    print(f"    APPLIED at lk+0x{idx:06x}")
    print(f"    {GREEN_SETTER_PATTERN.hex(' ')} -> {GREEN_SETTER_REPLACE.hex(' ')}")
    
    # Verify by decoding
    w1_patched = struct.unpack('<I', GREEN_SETTER_REPLACE[4:8])[0]
    rt = w1_patched & 0x1f
    offset = ((w1_patched >> 10) & 0xfff) * 4
    rn = (w1_patched >> 5) & 0x1f
    print(f"    Now: STR WZR, [X{rn}, #0x{offset:x}] — always writes 0 (GREEN)")
else:
    print(f"    FAILED: Pattern not found in lk partition!")
    sys.exit(1)
img.partitions['lk'].data = bytes(lk_data)

# ============================================================================
# PATCH 1: avb_allow_verification_error — MOV W22,WZR -> MOV W22,#1
# Only in 'lk' partition (matching Working A15 which only has this in lk)
# ============================================================================
print("\n[1] avb_allow_verification_error — MOV W22,WZR -> MOV W22,#1")
AVB_PATTERN = hex_to_bytes('f6 03 1f 2a 60 00 80 52')
AVB_REPLACE = hex_to_bytes('36 00 80 52 60 00 80 52')

lk_data = bytearray(img.partitions['lk'].data)
avb_idx = lk_data.find(AVB_PATTERN)
if avb_idx >= 0:
    lk_data[avb_idx:avb_idx+len(AVB_REPLACE)] = AVB_REPLACE
    print(f"    APPLIED at lk+0x{avb_idx:06x}")
else:
    print(f"    Pattern not found in lk (may be absent in A14)")
img.partitions['lk'].data = bytes(lk_data)

# ============================================================================
# PATCHES 2-6: Mehraan X6871 standard patches (applied to ALL partitions)
# ============================================================================
standard_patches = [
    ('sec_get_vfy_policy',
     '88 02 00 b9 f8 ff ff 17 20 02 00 b4 fd 7b be a9',
     '88 02 00 b9 f8 ff ff 17 00 00 80 52 c0 03 5f d6'),
    ('force_green_state (sboot)',
     'fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 aa 20 00 80 52',
     '48 04 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6 1f 20 03 d5'),
    ('bypass_security_control',
     'e8 0b 40 b9 1f 0d 00 71 21 01 00 54',
     'e8 0b 40 b9 1f 0d 00 71 1f 20 03 d5'),
    ('spoof_lock_state',
     '20 02 00 b4 fd 7b be a9 f3 0b 00 f9 fd 03 00 91',
     '88 00 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6'),
    ('dont_relock_seccfg',
     'fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 2a 28 00 80 52',
     '00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5'),
]

print("\n[2-6] Standard Mehraan X6871 patches")
for name, pat_hex, repl_hex in standard_patches:
    pat = hex_to_bytes(pat_hex)
    repl = hex_to_bytes(repl_hex)
    total = 0
    
    for pname, part in img.partitions.items():
        data = bytearray(part.data)
        start = 0
        while True:
            idx = data.find(pat, start)
            if idx == -1:
                break
            data[idx:idx+len(repl)] = repl
            total += 1
            start = idx + 1
        part.data = bytes(data)
    
    print(f"    {name:40s}: {total} hits")

# ============================================================================
# CERT BYPASS
# ============================================================================
print("\n[7] Certificate bypass (OVERRIDE)")
signed = apply_cert_bypass(img, trailing, CertBypass.OVERRIDE)
print(f"    Re-signed: {signed}")

# ============================================================================
# SAVE
# ============================================================================
with open(OUTPUT, 'wb') as f:
    f.write(bytes(img.contents))

out_size = os.path.getsize(OUTPUT)
with open(OUTPUT, 'rb') as f:
    out_hash = sha256(f.read())

print(f"\n{'='*70}")
print(f"  OUTPUT: {OUTPUT}")
print(f"  Size:   {out_size:,} bytes")
print(f"  SHA256: {out_hash}")
print(f"{'='*70}")

# ============================================================================
# FULL VERIFICATION
# ============================================================================
print(f"\n{'='*70}")
print(f"  POST-BUILD VERIFICATION")
print(f"{'='*70}")

with open(OUTPUT, 'rb') as f:
    out_raw = f.read()
with open(STOCK_A14, 'rb') as f:
    stock_raw = f.read()
with open(r'C:\Users\Admin\Videos\Project-2\Working-X6871-A15-Fenrir\lk.img', 'rb') as f:
    working_raw = f.read()

checks = {
    # Replacement patterns (should be PRESENT)
    'sec_vfy_kill (MOV W0,#0;RET after STR+B)': ('repl', '88 02 00 b9 f8 ff ff 17 00 00 80 52 c0 03 5f d6'),
    'green_sboot (MOV W8,#0x222)': ('repl', '48 04 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6 1f 20 03 d5'),
    'green_setter (STR WZR,[X8,#0x9AC])': ('repl', '28 03 00 d0 1f ad 09 b9 c0 03 5f d6'),
    'bypass_sec (NOP)': ('repl', 'e8 0b 40 b9 1f 0d 00 71 1f 20 03 d5'),
    'lock_state (MOV W8,#4)': ('repl', '88 00 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6'),
    'relock_kill (MOV W0,#0;RET;NOP3)': ('repl', '00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5'),
    'avb_error (MOV W22,#1)': ('repl', '36 00 80 52 60 00 80 52'),
    # Original patterns (should be ABSENT)
    'sec_vfy (orig)': ('orig', '88 02 00 b9 f8 ff ff 17 20 02 00 b4 fd 7b be a9'),
    'bypass_sec (orig B.NE)': ('orig', 'e8 0b 40 b9 1f 0d 00 71 21 01 00 54'),
    'green_setter (orig STR W0)': ('orig', '28 03 00 d0 00 ad 09 b9 c0 03 5f d6'),
    'avb_error (orig MOV WZR)': ('orig', 'f6 03 1f 2a 60 00 80 52'),
}

all_ok = True
print("\n  Patch verification:")
for name, (check_type, pat_hex) in checks.items():
    pat = hex_to_bytes(pat_hex)
    count = out_raw.count(pat)
    
    if check_type == 'repl':
        ok = count > 0
        status = f"PASS ({count} hits)" if ok else "FAIL (0 hits)"
    else:
        ok = count == 0
        status = f"PASS (removed)" if ok else f"FAIL ({count} remaining)"
    
    if not ok:
        all_ok = False
    print(f"    [{status:20s}] {name}")

# Cross-check with Working A15
print("\n  Cross-check with Working A15 Fenrir:")
a15_checks = {
    'green_sboot': '48 04 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6 1f 20 03 d5',
    'sec_vfy_kill': '88 02 00 b9 f8 ff ff 17 00 00 80 52 c0 03 5f d6',  
    'bypass_nop': 'e8 0b 40 b9 1f 0d 00 71 1f 20 03 d5',
    'lock_spoof': '88 00 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6',
    'relock_kill': '00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5',
}
for name, pat_hex in a15_checks.items():
    pat = hex_to_bytes(pat_hex)
    a14 = out_raw.count(pat)
    a15 = working_raw.count(pat)
    match = "MATCH" if a14 > 0 and a15 > 0 else "DIFF"
    print(f"    [{match}] {name}: A14v3={a14}, A15working={a15}")

# Collateral check
print("\n  Collateral corruption check:")
out_img = LkImage(OUTPUT)
for pname in ['lk', 'bl2_ext', 'aee']:
    sp_data = bytearray(LkImage(STOCK_A14).partitions[pname].data)
    pp_data = bytearray(out_img.partitions[pname].data)
    
    if len(sp_data) != len(pp_data):
        print(f"    '{pname}': Size mismatch")
        continue
    
    diff_count = sum(1 for i in range(len(sp_data)) if sp_data[i] != pp_data[i])
    print(f"    '{pname}': {diff_count} bytes changed (expected: patches only)")

# DTB check
dtb_ok = LkImage(STOCK_A14).partitions['lk_main_dtb'].data == out_img.partitions['lk_main_dtb'].data
print(f"    'lk_main_dtb': {'IDENTICAL (untouched)' if dtb_ok else 'MODIFIED (BAD)'}")

if all_ok:
    print(f"\n  {'='*58}")
    print(f"  =   VERIFIED CLEAN — ALL 7 PATCHES APPLIED — FLASH IT   =")
    print(f"  {'='*58}")
else:
    print(f"\n  !! ISSUES DETECTED !!")

print(f"\n  Flash commands:")
print(f'    fastboot flash lk_a "{OUTPUT}"')
print(f'    fastboot flash lk_b "{OUTPUT}"')
print(f'    fastboot reboot')

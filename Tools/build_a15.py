#!/usr/bin/env python3
"""
DEFINITIVE BUILD v4 — A15 CUSTOM LK (Infinix GT 20 Pro - X6871)

Requirements:
1. FULL GREEN: Force verified_boot_state to GREEN (0) across setter, sboot getter, and boot tags.
2. ENFORCING: Keep veritymode & SELinux reporting enforcing / clean state.
3. ALLOW ALL FASTBOOT CMDS: Bypass fastboot security checks so all fastboot/OEM commands are permitted.
4. DEEP VERIFICATION & WALKTHROUGH.
"""

import sys, os, struct, hashlib

SCRIPT_DIR = r"C:\Users\Admin\Videos\Project-2"
MEHRAAN_DIR = os.path.join(SCRIPT_DIR, "fenrir-main-mehraan")
sys.path.insert(0, os.path.join(MEHRAAN_DIR, "injector"))

from liblk.image import LkImage
from cert_bypass import CertBypass, apply_cert_bypass

STOCK_A15 = os.path.join(SCRIPT_DIR, "Stock-imgs-A15", "lk.img")
OUTPUT_A15 = os.path.join(SCRIPT_DIR, "Stock-imgs-A15", "lk-A15-fenrir-v4.img")

def hex_to_bytes(s): return bytes.fromhex(s.replace(' ', ''))
def sha256(d): return hashlib.sha256(d).hexdigest()

print("==============================================================================")
print("     FENRIR A15 — DEFINITIVE BUILD v4 (FULL GREEN, ENFORCING, ALL FASTBOOT)   ")
print("==============================================================================")

img = LkImage(STOCK_A15)

# Compute trailing bytes for cert bypass
region_end = 0
for partition in img.partitions.values():
    region_end = max(region_end, partition.end_offset)
    for cert in partition.certs:
        region_end = max(region_end, cert.end_offset)
trailing = bytes(img.contents[region_end:])

# 1. FORCE GREEN STATE SETTER (A15 offset lk+0x0506cc)
# Pattern:  28 03 00 d0 00 7d 09 b9 c0 03 5f d6
# Patched:  28 03 00 d0 1f 7d 09 b9 c0 03 5f d6
print("\n[1] FULL GREEN STATE SETTER (STR W0 -> STR WZR at lk+0x0506cc)")
green_pat = hex_to_bytes('28 03 00 d0 00 7d 09 b9 c0 03 5f d6')
green_repl = hex_to_bytes('28 03 00 d0 1f 7d 09 b9 c0 03 5f d6')

lk_data = bytearray(img.partitions['lk'].data)
idx_g = lk_data.find(green_pat)
if idx_g >= 0:
    lk_data[idx_g:idx_g+len(green_repl)] = green_repl
    print(f"    [+] Applied at lk+0x{idx_g:06x} (STR WZR, [X8, #0x97C]) -> Forces GREEN state (0)")
else:
    print("    [!] WARNING: Green setter pattern not found!")
img.partitions['lk'].data = bytes(lk_data)

# 2. AVB ALLOW VERIFICATION ERROR / ENFORCING PRESERVATION
print("\n[2] AVB ALLOW VERIFICATION ERROR (lk+0x050a00)")
avb_pat = hex_to_bytes('f6 03 1f 2a 60 00 80 52')
avb_repl = hex_to_bytes('36 00 80 52 60 00 80 52')

lk_data = bytearray(img.partitions['lk'].data)
idx_avb = lk_data.find(avb_pat)
if idx_avb >= 0:
    lk_data[idx_avb:idx_avb+len(avb_repl)] = avb_repl
    print(f"    [+] Applied at lk+0x{idx_avb:06x} (MOV W22, #1)")
img.partitions['lk'].data = bytes(lk_data)

# 3. STANDARD CORE PATCHES (ALLOW ALL FASTBOOT CMDS & GREEN SBOOT & LOCK SPOOF)
standard_patches = [
    ('sec_get_vfy_policy (ALLOW ALL FASTBOOT & SKIP VFY)',
     '88 02 00 b9 f8 ff ff 17 20 02 00 b4 fd 7b be a9',
     '88 02 00 b9 f8 ff ff 17 00 00 80 52 c0 03 5f d6'),
    ('force_green_state (sboot SCHIP_ONLY)',
     'fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 aa 20 00 80 52',
     '48 04 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6 1f 20 03 d5'),
    ('bypass_security_control (NOP B.NE)',
     'e8 0b 40 b9 1f 0d 00 71 21 01 00 54',
     'e8 0b 40 b9 1f 0d 00 71 1f 20 03 d5'),
    ('spoof_lock_state (LKS_LOCK = 4)',
     '20 02 00 b4 fd 7b be a9 f3 0b 00 f9 fd 03 00 91',
     '88 00 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6'),
    ('dont_relock_seccfg (NOP relock)',
     'fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 2a 28 00 80 52',
     '00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5'),
]

print("\n[3] APPLYING CORE PATCHES ACROSS SUB-PARTITIONS:")
for name, pat_hex, repl_hex in standard_patches:
    pat = hex_to_bytes(pat_hex)
    repl = hex_to_bytes(repl_hex)
    total = 0
    for pname, part in img.partitions.items():
        data = bytearray(part.data)
        search = 0
        while True:
            idx = data.find(pat, search)
            if idx == -1: break
            data[idx:idx+len(repl)] = repl
            total += 1
            search = idx + 1
        part.data = bytes(data)
    print(f"    - {name:48s}: {total} hits applied")

# 4. CERTIFICATE BYPASS (OVERRIDE MODE)
print("\n[4] APPLYING CONTAINER CERTIFICATE OVERRIDE BYPASS:")
signed = apply_cert_bypass(img, trailing, CertBypass.OVERRIDE)
print(f"    [+] Re-signed sub-partitions: {signed}")

# 5. WRITE OUTPUT BINARY
with open(OUTPUT_A15, 'wb') as f:
    f.write(bytes(img.contents))

out_sz = os.path.getsize(OUTPUT_A15)
out_h = sha256(open(OUTPUT_A15, 'rb').read())

print(f"\n==============================================================================")
print(f"  BUILD v4 COMPLETE!")
print(f"  Output Path: {OUTPUT_A15}")
print(f"  File Size:   {out_sz:,} bytes")
print(f"  SHA-256:     {out_h}")
print(f"==============================================================================")

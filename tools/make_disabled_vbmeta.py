#!/usr/bin/env python3
"""
Fenrir VBMeta Generator & Patcher
Creates or modifies AVB VBMeta images with dm-verity disabled (flags=2).
Signed with testkey_rsa2048.pem to satisfy LittleKernel AVB verification.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AVBTOOL = REPO_ROOT / "avbtool.py"
DEFAULT_KEY = REPO_ROOT / "testkey_rsa2048.pem"


def create_blank_disabled_vbmeta(output_path: Path) -> bool:
    """Creates a minimal 4096-byte disabled vbmeta image."""
    cmd = [
        sys.executable, str(AVBTOOL), "make_vbmeta_image",
        "--output", str(output_path),
        "--flag", "2"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Failed to generate blank disabled vbmeta: {res.stderr}")
        return False
    print(f"[+] Created minimal disabled vbmeta at {output_path} ({output_path.stat().st_size} bytes)")
    return True


def patch_stock_vbmeta(stock_path: Path, output_path: Path, key_path: Path = DEFAULT_KEY) -> bool:
    """
    Extracts descriptors from stock vbmeta and re-signs with flags=2 (hashtree disabled).
    This preserves chain partition descriptors while disabling dm-verity verification.
    """
    if not stock_path.exists():
        print(f"[-] Stock vbmeta not found: {stock_path}")
        return False

    if not key_path.exists():
        print(f"[-] Signing key not found: {key_path}")
        return False

    # Direct flag modification: byte 0x7B in AVB header is the flags field (big-endian uint32 at 0x78)
    data = bytearray(stock_path.read_bytes())
    if len(data) < 256 or data[:4] != b"AVB0":
        print("[-] Invalid AVB magic in stock vbmeta")
        return False

    # AVB header layout:
    # offset 0x78: uint32 flags
    # We want AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED (2)
    # Re-signing using avbtool:
    cmd = [
        sys.executable, str(AVBTOOL), "make_vbmeta_image",
        "--output", str(output_path),
        "--key", str(key_path),
        "--algorithm", "SHA256_RSA2048",
        "--flag", "2",
        "--include_descriptors_from_image", str(stock_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Re-signing failed: {res.stderr}")
        print("[*] Falling back to direct flag bit patch...")
        data[0x7B] = 0x02
        output_path.write_bytes(data)
        print(f"[+] Applied direct flag patch (flags=2) to {output_path}")
        return True

    print(f"[+] Re-signed vbmeta with flags=2 at {output_path} ({output_path.stat().st_size} bytes)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate or patch AVB VBMeta with dm-verity disabled")
    parser.add_argument("-s", "--stock", type=Path, help="Path to stock vbmeta.img to patch and re-sign")
    parser.add_argument("-o", "--output", type=Path, default=Path("vbmeta_disabled.img"), help="Output file path")
    parser.add_argument("-k", "--key", type=Path, default=DEFAULT_KEY, help="RSA signing key (default: testkey_rsa2048.pem)")
    args = parser.parse_args()

    if args.stock:
        ok = patch_stock_vbmeta(args.stock, args.output, args.key)
    else:
        ok = create_blank_disabled_vbmeta(args.output)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

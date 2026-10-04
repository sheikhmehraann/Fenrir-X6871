#!/usr/bin/env python3
"""Build and verify Infinix GT 20 Pro (X6871) patched LK images using the Renkai engine."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

# Locate Renkai repository if adjacent or in parent hierarchy
_this_dir = Path(__file__).resolve().parent
_repo_root = _this_dir.parent
_candidate_paths = [
    _repo_root.parent / "Renkai",
    _repo_root.parent.parent / "Renkai",
    Path(r"C:\Users\Admin\Videos\Github\Renkai"),
]

_renkai_root = None
for p in _candidate_paths:
    if p.exists() and (p / "renkai" / "engine.py").exists():
        _renkai_root = p
        break

if _renkai_root:
    sys.path.insert(0, str(_renkai_root))
else:
    print("[-] Error: Renkai engine repository not found.")
    print("    Please clone Renkai alongside this repository:")
    print("    git clone https://github.com/sheikhmehraann/Renkai.git")
    sys.exit(1)

try:
    import devices
    from renkai.engine import RenkaiEngine
    from tools.verify import verify_certificate_bypass, verify_headers, verify_patches
except ImportError as e:
    print(f"[-] Failed to import Renkai modules: {e}")
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_and_verify(codename: str, stock_path: Path, output_path: Path) -> bool:
    print(f"\n[*] Processing {codename} via Renkai engine...")
    if not stock_path.exists():
        print(f"    [-] Stock file not found: {stock_path}")
        return False

    profile = devices.get_device_profile(codename)
    if not profile:
        print(f"    [-] Profile not found for codename: {codename}")
        return False

    engine = RenkaiEngine(stock_path)
    engine.apply_device_profile(profile, apply_policy=True)
    engine.save(output_path, cert_mode=profile.cert_mode)

    # Verification
    v_engine = RenkaiEngine(output_path)
    h_ok = verify_headers(v_engine.image)
    c_ok = verify_certificate_bypass(v_engine.image)
    p_ok = verify_patches(v_engine, codename)

    if h_ok and c_ok and p_ok:
        size = output_path.stat().st_size
        csum = sha256_file(output_path)
        print(f"    [+] {profile.name} VERIFIED")
        print(f"        Output: {output_path}")
        print(f"        Size:   {size:,} bytes")
        print(f"        SHA256: {csum}")
        return True
    else:
        print(f"    [!] Verification failed for {codename}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Build X6871 images using Renkai engine")
    parser.add_argument(
        "--version",
        choices=["a15", "a14", "all"],
        default="all",
        help="Target Android version to build (default: all)",
    )
    args = parser.parse_args()

    targets = []
    if args.version in ("a15", "all"):
        targets.append(
            (
                "x6871_a15",
                _repo_root / "A15" / "lk-stock-backup.img",
                _repo_root / "A15" / "lk-patched.img",
            )
        )
    if args.version in ("a14", "all"):
        targets.append(
            (
                "x6871_a14",
                _repo_root / "A14" / "lk-stock-backup.img",
                _repo_root / "A14" / "lk-patched.img",
            )
        )

    all_passed = True
    for codename, stock_p, out_p in targets:
        ok = build_and_verify(codename, stock_p, out_p)
        if not ok:
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

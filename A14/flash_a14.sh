#!/usr/bin/env bash
set -e
echo "==================================================="
echo "  Flashing Fenrir A14 Patched LK (Infinix GT 20 Pro)"
echo "==================================================="
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img
echo "[+] Done! Rebooting..."
fastboot reboot

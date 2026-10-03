#!/usr/bin/env bash
set -e
echo "Flashing Fenrir A14 (X6871)..."
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img
echo "Done. Rebooting to recovery..."
fastboot reboot recovery

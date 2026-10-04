#!/usr/bin/env bash
set -e
echo "Flashing Renkai A15 (X6871)..."
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img

if [ -f "logo-patched.img" ]; then
    fastboot flash logo_a logo-patched.img
    fastboot flash logo_b logo-patched.img
fi

echo "Done. Rebooting to recovery..."
fastboot reboot recovery

@echo off
echo Flashing Renkai A15 (X6871)...
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img

if exist logo-patched.img (
    fastboot flash logo_a logo-patched.img
    fastboot flash logo_b logo-patched.img
)

echo Done. Rebooting to recovery...
fastboot reboot recovery
pause

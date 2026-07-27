@echo off
echo ===================================================
echo   Flashing Fenrir A15 Complete Suite (X6871)
echo ===================================================
echo [*] Flashing Patched Bootloader (LK)...
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img

echo [*] Flashing Stock VBMETA...
fastboot flash vbmeta_a vbmeta-stock.img
fastboot flash vbmeta_b vbmeta-stock.img

echo [*] Flashing OrangeFox Recovery (vendor_boot)...
fastboot flash vendor_boot_a vendor_boot-orangefox.img
fastboot flash vendor_boot_b vendor_boot-orangefox.img

echo [+] All images flashed successfully! Rebooting...
fastboot reboot
pause

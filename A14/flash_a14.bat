@echo off
echo ===================================================
echo   Flashing Fenrir A14 Patched LK (X6871)
echo ===================================================
fastboot flash lk_a lk-patched.img
fastboot flash lk_b lk-patched.img
echo [+] Done! Rebooting...
fastboot reboot
pause

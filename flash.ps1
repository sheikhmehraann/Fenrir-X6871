param(
    [string]$Image = "x6871-fenrir.bin",
    [int]$TimeoutSec = 60
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command fastboot -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Error: 'fastboot' command not found in PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $Image)) {
    Write-Host "[-] Error: Image file '$Image' not found." -ForegroundColor Red
    exit 1
}

Write-Host "[*] Waiting for device in fastboot mode (timeout: ${TimeoutSec}s)..." -ForegroundColor Yellow
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$found = $false

while ($sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
    $devices = fastboot devices 2>&1
    if ($devices -match "fastboot") {
        $found = $true
        break
    }
    Start-Sleep -Seconds 1
}

if (-not $found) {
    Write-Host "[-] Timeout: No fastboot device detected." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Fastboot device detected." -ForegroundColor Green

# Detect current slot
$slotVar = fastboot getvar current-slot 2>&1
$slot = "a"
if ($slotVar -match "current-slot:\s*([ab])") {
    $slot = $matches[1]
    Write-Host "[*] Active slot: $slot" -ForegroundColor Cyan
    $partition = "lk_$slot"
} else {
    Write-Host "[*] Slot not detected, defaulting to partition 'lk'" -ForegroundColor Yellow
    $partition = "lk"
}

Write-Host "[*] Flashing $Image to $partition..." -ForegroundColor Cyan
fastboot flash $partition $Image
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Flash failed!" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Flash successful." -ForegroundColor Green
Write-Host "[*] You can reboot the device with: fastboot reboot" -ForegroundColor White

param(
    [string]$Device = "x6871",
    [string]$Bootloader = ""
)

$ErrorActionPreference = "Stop"

$DeviceLower = $Device.ToLower()

if (-not $Bootloader) {
    $Bootloader = "bin\$($DeviceLower).bin"
}

if (-not (Test-Path $Bootloader)) {
    Write-Host "[-] Bootloader not found: $Bootloader" -ForegroundColor Red
    exit 1
}

Write-Host "[*] Building payload and injector for $Device..." -ForegroundColor Cyan
Write-Host "[*] Bootloader source: $Bootloader" -ForegroundColor Cyan

# 1. Build stage 1 payload
python payload\build_payload.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Failed to build payload" -ForegroundColor Red
    exit 1
}

# 2. Run injector
$OutputFile = "$($DeviceLower)-fenrir.bin"
$env:PYTHONPATH = "$PWD;$PWD\injector;$env:PYTHONPATH"
python injector\inject.py $DeviceLower $Bootloader -o $OutputFile -p payload\build

if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Injection failed" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Successfully generated: $OutputFile" -ForegroundColor Green

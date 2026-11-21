#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

DEVICE="${1:-X6871}"
DEVICE_LOWER=$(echo "$DEVICE" | tr '[:upper:]' '[:lower:]')

if [ -n "$2" ]; then
    BOOTLOADER="$2"
else
    BOOTLOADER="bin/${DEVICE_LOWER}.bin"
fi

if [ ! -f "$BOOTLOADER" ]; then
   echo -e "${RED}Error: Bootloader file '$BOOTLOADER' not found${NC}"
   exit 1
fi

echo
echo -e "${BOLD}Building for device: ${BLUE}$DEVICE${NC}"
echo -e "${BOLD}Bootloader: ${BLUE}$BOOTLOADER${NC}"
echo

rm -rf payload/build

echo -e "${YELLOW}Building payload...${NC}"
if command -v aarch64-none-elf-gcc &> /dev/null && command -v make &> /dev/null; then
    (cd payload && make DEVICE="$DEVICE" all) || python3 payload/build_payload.py
else
    python3 payload/build_payload.py
fi

echo
echo -e "${YELLOW}Injecting payload and applying LittleKernel patches...${NC}"
./inject.sh "$DEVICE" "$BOOTLOADER" -o "${DEVICE_LOWER}-fenrir.bin" -p payload/build

echo
if [ -f "${DEVICE_LOWER}-fenrir.bin" ]; then
   echo -e "${GREEN}Operation completed successfully!${NC}"
   echo -e "Patched bootloader saved as: ${BOLD}${DEVICE_LOWER}-fenrir.bin${NC}"
else
   echo -e "${RED}Injection failed or output file not found!${NC}"
   exit 1
fi

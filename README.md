# Fenrir — Infinix GT 20 Pro (X6871)

[![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro%20%28X6871%29-1081E0?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![SoC](https://img.shields.io/badge/SoC-MediaTek%20Dimensity%208200%20Ultimate-FF6600?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![Android](https://img.shields.io/badge/Android%2014%20%7C%2015-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![License](https://img.shields.io/badge/License-AGPL--3.0-6C5CE7?style=for-the-badge)](LICENSE)

Fenrir is a MediaTek boot-chain exploit and patching project originally developed by
[R0rt1z2](https://github.com/R0rt1z2).

This repository contains the work for bringing Fenrir to the **Infinix GT 20 Pro
(`X6871`)**.

The upstream Fenrir repository is archived. `X6871` is not listed as an upstream
supported device, so the X6871-specific work in this repository should be treated
as a separate port rather than official upstream support.

## What Fenrir does

Fenrir takes advantage of a verification issue in the MediaTek boot chain.

When the bootloader is unlocked, the affected boot chain can skip verification of
`bl2_ext`. Fenrir patches the relevant verification logic so that an unverified
`bl2_ext` can continue through the boot chain.

The upstream implementation patches:

```text
sec_get_vfy_policy()
```

so that it returns `0`.

This gives code execution at EL3 and allows later parts of the boot chain to be
controlled.

The payload can also register custom Fastboot commands, control boot mode, and call
bootloader functions at runtime.

Fenrir also contains code that can spoof the bootloader lock state as locked. The
upstream project notes that this can be useful for integrity checks and custom ROMs,
although additional VBMeta changes may be required depending on the device.

## Boot chain

Normal boot:

```text
BootROM
   |
Preloader
   |
bl2_ext
   |
TEE
   |
GenieZone
   |
LK / AEE
   |
Linux kernel
```

With the vulnerable verification path patched:

```text
BootROM
   |
Preloader
   |
bl2_ext (patched / unverified)
   |
TEE / GenieZone / LK
   |
Linux kernel
```

## X6871 builds

The following X6871 firmware versions are documented in this port:

| Android | OS | Firmware | Status |
|---|---|---|---|
| Android 15 | XOS 15 | `X6871-15.1.2.165SP05(OP001PF001AZ)` | Tested |
| Android 15 | XOS 15 | `X6871-15.1.2.180SP05(OP001PF001AZ)` | Tested |
| Android 14 | XOS 14 | `X6871-H962CF-U-OP-250217V2673` | Tested |

These are X6871 port-specific results. They are not listed as official upstream
Fenrir support.

## Before flashing

Make sure the image matches the exact device and firmware.

Do not flash a bootloader image from another device.

A wrong bootloader, preloader, or other low-level image can permanently brick the
device.

Keep a complete set of stock firmware and a way to restore it before testing.

## Building

The original Fenrir project uses `liblk` for working with MediaTek LK images.

Install the Python requirements:

```bash
pip install -r requirements.txt
```

Put the source bootloader in `bin/` using the device codename:

```text
bin/<device>.bin
```

For example:

```text
bin/pacman.bin
```

Build using:

```bash
./build.sh <device>
```

Or provide the bootloader path directly:

```bash
./build.sh <device> /path/to/bootloader.bin
```

The build script creates the patched bootloader output.

The exact build target and files for `X6871` depend on the port in this repository.

## Flashing

The upstream project provides a `flash.sh` script for devices where Fastboot
flashing is available.

The exact partition and flashing commands for the X6871 port should be taken from
the files and release package included with this repository.

Do not use commands or images intended for another Fenrir-supported device.

## Checking a device

One useful check when researching a new MediaTek device is the `bl2_ext`
verification state.

The upstream project uses an `expdb` dump and looks for:

```text
[PART] img_auth_required = 0
[PART] Image with header, name: bl2_ext
[PART] part: lk_a img: bl2_ext cert vfy(0 ms)
```

If `bl2_ext` is not verified, the device may be affected by the same class of
boot-chain issue. That alone does not mean that a Fenrir port will work; the
device still needs to be researched and tested.

## Current upstream status

The original `R0rt1z2/fenrir` repository was archived on September 20, 2026.

Upstream currently lists these supported devices:

| Device | Codename |
|---|---|
| Nothing Phone (2a) | `Pacman` |
| Nothing Phone (2a) Plus | `PacmanPro` |
| CMF Phone 1 | `Tetris` |
| Lenovo IdeaTab Pro / Xiaoxin Pad Pro 12.7 | `peridotl` |
| Tecno Pova 4 | `LG7n` |
| Tecno Pova 4 Pro | `LG8n` |
| Tecno Pova 5 | `LH7n` |
| Zinwa Q25 | `Q25` |
| Redmi K70E / POCO X6 Pro 5G | `duchamp` |
| Redmi Turbo 4 / POCO X7 Pro | `rodin` |
| Redmi Turbo 5 Max / POCO X8 Pro Max | `dash` |
| Redmi Note 11T Pro / Pro+ / POCO X4 GT / Redmi K50i | `xaga` |
| Xiaomi 12T | `plato` |

`X6871` is not in that upstream list.

## Known limitations

The upstream project documents several limitations:

- Runtime memory modification in the payload can trigger an MMU fault.
- There is no complete porting guide for new devices.
- Payload appending still needs work.
- Custom ROMs may require additional VBMeta changes.
- Fastboot flashing depends on the device exposing the required mode.

## Credits

Fenrir was originally created by
[R0rt1z2](https://github.com/R0rt1z2).

X6871 research and porting work:

- [@ramabondanp](https://github.com/ramabondanp)
- [@mehraann19](https://github.com/sheikhmehraann)

Upstream project:

https://github.com/R0rt1z2/fenrir

## License

This project is based on Fenrir, which is licensed under the
**GNU Affero General Public License v3.0 (AGPL-3.0)**.

See [LICENSE](LICENSE) for the full license text.

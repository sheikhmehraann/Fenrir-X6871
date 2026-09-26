# Fenrir — Infinix GT 20 Pro (X6871)

[![Device](https://img.shields.io/badge/Device-Infinix%20GT%2020%20Pro%20%28X6871%29-1081E0?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![SoC](https://img.shields.io/badge/SoC-MediaTek%20Dimensity%208200%20Ultimate-FF6600?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![XOS](https://img.shields.io/badge/XOS-14%20%7C%2015-00C853?style=for-the-badge&logo=android&logoColor=white)](https://github.com/sheikhmehraann/Fenrir-X6871)
[![License](https://img.shields.io/badge/License-AGPL--3.0-6C5CE7?style=for-the-badge)](LICENSE)

Fenrir for the Infinix GT 20 Pro (`X6871`).

This repository contains the X6871-specific port, patches, builds and testing for Fenrir.

Fenrir was originally created by [R0rt1z2](https://github.com/R0rt1z2). The original project is archived. The X6871 is not in the original upstream device list, so this repository is the X6871 port.

## What it does

Fenrir is based on a vulnerability in the MediaTek boot chain.

When the device is in the unlocked `seccfg` state, the affected boot chain can skip verification of `bl2_ext`. Fenrir patches the verification path so the patched `bl2_ext` can continue through the boot chain.

The original Fenrir PoC patches:

```c
sec_get_vfy_policy()
```

to return `0`.

The code runs at EL3 and affects the boot chain after Preloader.

The original project also includes a payload that can register custom Fastboot commands, control boot mode and call bootloader functions. It also contains lock-state spoofing.

## Boot chain

Normal:

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

With the patched verification path:

```text
BootROM
  |
Preloader
  |
bl2_ext (patched)
  |
TEE / GenieZone
  |
LK / AEE
  |
Linux kernel
```

## X6871 support

These are the X6871 builds currently documented for this repository:

| Android | OS | Build | Status |
|---|---|---|---|
| Android 15 | XOS 15 | `X6871-15.1.2.165SP05(OP001PF001AZ)` | Tested |
| Android 15 | XOS 15 | `X6871-15.1.2.180SP05(OP001PF001AZ)` | Tested |
| Android 14 | XOS 14 | `X6871-H962CF-U-OP-250217V2673` | Tested |

These results are for the X6871 port.

## Installation

> [!CAUTION]
> This modifies the boot chain. Flashing the wrong low-level image can brick the device. Check the device codename and firmware build before flashing.

### Recovery package

1. Boot into OrangeFox or TWRP.
2. Download the matching package from [Releases](https://github.com/sheikhmehraann/Fenrir-X6871/releases).
3. Android 15:
   ```text
   Android-15-Fenrir-Patch-recovery-ab.zip
   ```
4. Android 14:
   ```text
   Android-14-Fenrir-Patch-recovery-ab.zip
   ```
5. In recovery, go to **Wipe → Format Data**.
6. Type `yes` and confirm.
7. Reboot to system.

Format Data is required during the initial setup used by this port.

## Custom kernels

Custom kernels can be used if they are compatible with the X6871 and the ROM being used.

Make sure the required Fenrir components are still present after installing or changing a kernel.

## Custom and ported ROMs

Custom and ported ROMs can be used with the X6871 port.

When changing ROMs, reflash the Fenrir package if the ROM replaces the patched bootloader, boot or recovery components.

Some ROMs may need additional VBMeta changes. Do not assume that every port will boot with the same VBMeta configuration.

## VBMeta

The original Fenrir project notes that custom ROMs may need additional VBMeta changes.

Do not manually disable VBMeta unless it is required by the specific ROM and setup you are using.

## Play Integrity

Fenrir includes the lock-state spoofing from the original PoC.

Play Integrity results depend on the ROM, boot image, security patch level and other modifications on the device. Fenrir alone does not guarantee a particular Play Integrity result.

If it is not working, check:

- `boot.img` matches the ROM and security patch level.
- The ROM is compatible with the X6871 port.
- There are no conflicting Magisk or Play Integrity modules.
- VBMeta has not been changed incorrectly.

## After changing ROMs

If a ROM update replaces the patched components, reinstall the Fenrir package before booting the new system.

If the device boot-loops, return to recovery or Fastboot and restore the correct Fenrir package or the matching stock images.

## Building

The original Fenrir project uses [`liblk`](https://github.com/R0rt1z2/liblk).

Install the requirements:

```bash
pip install -r requirements.txt
```

Place the source bootloader in `bin/`:

```text
bin/<device>.bin
```

Build it with:

```bash
./build.sh <device>
```

Or provide the bootloader path:

```bash
./build.sh <device> /path/to/bootloader.bin
```

The original build process produces a patched LK image.

For X6871, use the build files and configuration in this repository. Do not use bootloader images from another device.

## Checking the boot chain

When researching a MediaTek device, one of the things to check is whether `bl2_ext` is actually being verified.

The original Fenrir project uses an `expdb` dump and looks for entries similar to:

```text
[PART] img_auth_required = 0
[PART] Image with header, name: bl2_ext
[PART] part: lk_a img: bl2_ext cert vfy(0 ms)
```

`img_auth_required = 0` indicates that authentication is not being requested at that point.

This alone does not prove that Fenrir will work on a device. The rest of the boot chain still needs to be checked.

## Upstream Fenrir

The original Fenrir project was made for several MediaTek devices, including:

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

The Infinix GT 20 Pro (`X6871`) is not in that upstream list. This repository contains the X6871-specific work.

## Limitations

The original project documents these limitations:

- Runtime memory modification can trigger an MMU fault.
- Payload appending still needs work.
- There is no complete generic porting guide.
- Custom ROMs may require additional VBMeta changes.
- Flashing depends on the device exposing the required mode.

## Credits

Original Fenrir:

- [R0rt1z2](https://github.com/R0rt1z2)

X6871 research and development:

- [ramabondanp](https://github.com/ramabondanp)
- [mehraann19](https://github.com/mehraann19)

Original project:

https://github.com/R0rt1z2/fenrir

## License

Fenrir is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

See [LICENSE](LICENSE) for the full license text.

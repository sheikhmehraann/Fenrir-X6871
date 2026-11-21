#pragma once

#define DEVICE_NAME "X6871"

#define STAGE1_BASE                  0xffff000050f02800
#define STAGE2_BASE                  0xffff000050f02c00
#define STAGE3_BASE                  0xffff000050f02f00

#define PIVOT_ADDR                   0xffff000050f11750
#define BOOT_MODE_ADDR               0xffff000050fe4968
#define BOOT_MODE_FASTBOOT           99

#define FASTBOOT_INIT_ADDR           0xffff000050f7d684
#define FASTBOOT_HANDLER_ADDR        0xffff000050f80ca0
#define FASTBOOT_TARGET_BUF          0xffff000050fd5510

#define PLATFORM_INIT_ADDR           0xffff000050f02444
#define NOTIFY_ENTER_FASTBOOT_ADDR   0xffff000050f0569c
#define NOTIFY_BOOT_LINUX_ADDR       0xffff000050f0cfb8

#define PRINTF_ADDR                  0xffff000050f686e0
#define VIDEO_PRINTF_ADDR            0xffff000050f3a948

#define FASTBOOT_OKAY_ADDR           0xffff000050f04fb0
#define FASTBOOT_FAIL_ADDR           0xffff000050f04f64
#define FASTBOOT_INFO_ADDR           0xffff000050f04f9c
#define FASTBOOT_REGISTER_ADDR       0xffff000050f04be8
#define FASTBOOT_PUBLISH_ADDR        0xffff000050f04cb4

#define PADDR_TO_KVADDR_ADDR         0xffff000050f54e34
#define KERNEL_ASPACE_ADDR           0xffff000050fea6b8

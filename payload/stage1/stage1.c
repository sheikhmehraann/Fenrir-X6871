#include "common.h"
#include "debug.h"
#include "device_config.h"

#ifdef DEVICE_x6871
static bool detect_key(uint32_t index) {
    return ((bool (*)(uint32_t))DETECT_KEY_ADDR)(index);
}
#endif

__attribute__((section(".text.main"))) int main(void) {
#ifdef DEVICE_x6871
    // X6871 hooks stage1 after boot_mode_check(); override the selected
    // mode here when Volume Down is held.
    if (detect_key(FASTBOOT_KEY_INDEX)) {
        WRITE32NC(BOOT_MODE_ADDR, BOOT_MODE_FASTBOOT);
    }
#else
    // This payload executes before LK calls platform_init(), which handles
    // the initialization of platform-specific hardware components. This is
    // one of the earliest points where we can execute custom code during
    // the boot process.
    printf("Entered pre-platform_init() stage1 payload!\n");
    platform_init();
#endif

    // The caller expects this function to return an integer value.
    return 0;
}

from cert_bypass import CertBypass
from device import Device
from patch_utils import MatchMode
from stage import PatchStage, PayloadStage

DEVICES = [
    Device(
        'X6871',
        'Infinix GT 20 Pro',
        {
            # Stage 1: Hardware Fastboot mode handler & key hook
            'stage1': PayloadStage(
                'stage1',
                0xFFFF000050F02800,
                0xFFFF000050F11750,
                description='Fastboot mode handler and hardware key hook',
            ),

            # Force sboot state to report ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP (LK only!)
            'spoof_sboot_state': PatchStage(
                'spoof_sboot_state',
                pattern='fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 aa 20 00 80 52',
                replacement='48 04 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force sboot state to always be ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP',
            ),

            # Skip security check error branch in LittleKernel commands (LK only!)
            'bypass_security_control': PatchStage(
                'bypass_security_control',
                pattern='e8 0b 40 b9 1f 0d 00 71 21 01 00 54',
                replacement='e8 0b 40 b9 1f 0d 00 71 1f 20 03 d5',
                match_mode=MatchMode.ALL,
                partition='lk',
                description='Skip security error branch - always execute commands',
            ),

            # Force lock state query to unconditionally return LKS_LOCK (4) (LK only!)
            'spoof_lock_state': PatchStage(
                'spoof_lock_state',
                pattern='20 02 00 b4 fd 7b be a9 f3 0b 00 f9 fd 03 00 91',
                replacement='88 00 80 52 08 00 00 b9 00 00 80 52 c0 03 5f d6',
                match_mode=MatchMode.ALL,
                partition='lk',
                description='Force lock state to always be LKS_LOCK (4)',
            ),

            # Force kernel cmdline androidboot.vbmeta.device_state to 'locked' (LK only!)
            'force_avb_device_locked': PatchStage(
                'force_avb_device_locked',
                pattern='48 02 00 90 08 39 03 91 02 01 89 9a',
                replacement='48 02 00 90 08 39 03 91 e2 03 08 aa',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force androidboot.vbmeta.device_state=locked for clean AVB invariant',
            ),

            # Force kernel cmdline androidboot.verifiedbootstate=green (LK only!)
            'force_avb_green_cmdline': PatchStage(
                'force_avb_green_cmdline',
                pattern='a8 03 00 d0 08 11 45 b9 1f 0d 00 71',
                replacement='08 00 80 52 1f 20 03 d5 1f 0d 00 71',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force kernel cmdline androidboot.verifiedbootstate=green in append_boot_state_cmdline',
            ),

            # Force get_avb_boot_state to return AVB_BOOT_STATE_GREEN (0) (LK only!)
            'force_get_avb_boot_state': PatchStage(
                'force_get_avb_boot_state',
                pattern='a8 03 00 d0 00 11 45 b9 c0 03 5f d6',
                replacement='00 00 80 52 c0 03 5f d6 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force get_avb_boot_state to unconditionally return AVB_BOOT_STATE_GREEN (0)',
            ),

            # Force sec_boot_state_get to return SEC_BOOT_STATE_GREEN (0) (LK only!)
            'force_sec_boot_state': PatchStage(
                'force_sec_boot_state',
                pattern='28 09 00 90 00 41 45 b9 c0 03 5f d6',
                replacement='00 00 80 52 c0 03 5f d6 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force sec_boot_state_get to unconditionally return SEC_BOOT_STATE_GREEN (0)',
            ),

            # Unconditionally load slot data into g_boot_info even on AVB error (LK only!)
            'force_avb_load_slot_data': PatchStage(
                'force_avb_load_slot_data',
                pattern='76 00 00 37 f7 03 00 2a a0 f8 ff 35',
                replacement='03 00 00 14 1f 20 03 d5 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force unconditional branch to slot data loader in load_vfy_boot (allow custom partitions)',
            ),

            # Skip image certificate verification on partition images (LK only!)
            'force_avb_skip_cert_vfy': PatchStage(
                'force_avb_skip_cert_vfy',
                pattern='2d 00 00 94 20 f7 ff 34',
                replacement='1f 20 03 d5 b9 ff ff 17',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Unconditionally branch to success (avb_ret=0) and bypass image cert verification',
            ),

            # Force AVB img_auth_required to 0 in load_vfy_boot (LK only!)
            'force_avb_img_auth_0': PatchStage(
                'force_avb_img_auth_0',
                pattern='00 09 43 7a f5 07 9f 1a e1 03 15 2a',
                replacement='1f 20 03 d5 15 00 80 52 e1 03 15 2a',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force img_auth_required=0 and ALLOW_VERIFICATION_ERROR=1 in load_vfy_boot',
            ),

            # Force img_auth_check function to unconditionally return 0 (LK only!)
            'force_img_auth_check_0': PatchStage(
                'force_img_auth_check_0',
                pattern='00 09 43 7a f3 07 9f 1a e1 03 13 2a',
                replacement='1f 20 03 d5 13 00 80 52 e1 03 13 2a',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force img_auth_check to unconditionally return 0',
            ),

            # Force dm-verity mode to ignore_corruption while emitting androidboot.veritymode=enforcing (Green/Locked + DSU compatibility) (LK only!)
            'force_avb_verity_mode_ignore_corruption': PatchStage(
                'force_avb_verity_mode_ignore_corruption',
                pattern='68 02 00 37 a8 63 40 b9 1f 0d 00 71 00 03 00 54 1f 09 00 71 20 02 00 54',
                replacement='42 02 00 f0 42 54 20 91 55 02 00 d0 b5 8a 13 91 1b 00 00 14 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force dm-verity mode to ignore_corruption while emitting androidboot.veritymode=enforcing for full Green/Locked + DSU compatibility',
            ),

            # Prevent LittleKernel from re-locking the seccfg partition (LK only!)
            'dont_relock_seccfg': PatchStage(
                'dont_relock_seccfg',
                pattern='fd 7b be a9 f3 0b 00 f9 fd 03 00 91 f3 03 00 2a 28 00 80 52',
                replacement='00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5',
                match_mode=MatchMode.ALL,
                partition='lk',
                description='Prevent LK from re-locking seccfg',
            ),

            # Unconditionally disable AP watchdog in mtk_wdt_enable (LK only!)
            'disable_ap_watchdog': PatchStage(
                'disable_ap_watchdog',
                pattern='4a 11 8b 1a 29 01 0c 0a 29 01 0a 2a 09 01 00 b9 60 00 00 36',
                replacement='ea 03 0b 2a 29 01 0c 0a 29 01 0a 2a 09 01 00 b9 c0 03 5f d6',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force mtk_wdt_enable to always disable watchdog and return',
            ),

            # Force mtk_wdt_doe_setup to unconditionally run hardware watchdog disable (LK only!)
            'disable_ap_watchdog_doe': PatchStage(
                'disable_ap_watchdog_doe',
                pattern='ff c3 00 d1 fd 7b 01 a9 f4 4f 02 a9 fd 43 00 91 21 03 00 f0 21 18 1e 91',
                replacement='ff c3 00 d1 fd 7b 01 a9 f4 4f 02 a9 fd 43 00 91 2c 00 00 14 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force mtk_wdt_doe_setup to unconditionally disable AP hardware watchdog before kernel jump',
            ),

            # Neutralize Orange warning screen display and 7-second stall (LK only!)
            'neutralize_orange_warning_screen': PatchStage(
                'neutralize_orange_warning_screen',
                pattern='fd 7b bf a9 fd 03 00 91 60 02 00 b0 00 cc 0d 91',
                replacement='c0 03 5f d6 fd 03 00 91 60 02 00 b0 00 cc 0d 91',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Neutralize Orange State Warning screen and msleep delays',
            ),

            # Neutralize AVB show_warning_screen and eliminate 5-second stall (LK only!)
            'neutralize_avb_warning_screen': PatchStage(
                'neutralize_avb_warning_screen',
                pattern='a8 03 00 d0 08 11 45 b9 1f 05 00 71 04 19 43 7a',
                replacement='00 00 80 52 c0 03 5f d6 1f 20 03 d5 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Neutralize AVB show_warning_screen and eliminate 5000ms delay',
            ),

            # Neutralize Orange State warning text printing routine (LK only!)
            'neutralize_orange_state_text_print': PatchStage(
                'neutralize_orange_state_text_print',
                pattern='ff c3 00 d1 fd 7b 01 a9 f4 4f 02 a9 fd 43 00 91 f4 03 00 2a',
                replacement='c0 03 5f d6 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Neutralize Orange State text drawing routine on LCM display',
            ),

            # Set AVB_SLOT_VERIFY_FLAGS_ALLOW_VERIFICATION_ERROR in avb_slot_verify (LK only!)
            'avb_allow_verification_error': PatchStage(
                'avb_allow_verification_error',
                pattern='f8 03 03 2a f9 03 02 aa bf 03 15 f8',
                replacement='38 00 80 52 f9 03 02 aa bf 03 15 f8',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force avb_slot_verify flags to include AVB_SLOT_VERIFY_FLAGS_ALLOW_VERIFICATION_ERROR (1)',
            ),

            # Enable UART printk logging in kernel cmdline (disable_uart=0) (LK only!)
            'enable_kernel_uart_log': PatchStage(
                'enable_kernel_uart_log',
                pattern='6d 74 6b 5f 70 72 69 6e 74 6b 5f 63 74 72 6c 2e 64 69 73 61 62 6c 65 5f 75 61 72 74 3d 31 00',
                replacement='6d 74 6b 5f 70 72 69 6e 74 6b 5f 63 74 72 6c 2e 64 69 73 61 62 6c 65 5f 75 61 72 74 3d 30 00',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force kernel cmdline mtk_printk_ctrl.disable_uart=0 to enable boot logging',
            ),

            # Force AVB public key verification to unconditionally accept any public key as trusted (LK only!)
            'force_avb_public_key_trusted': PatchStage(
                'force_avb_public_key_trusted',
                pattern='c1 06 00 b4 fd 7b bc a9 f7 0b 00 f9 f6 57 02 a9 f4 4f 03 a9',
                replacement='45 00 00 b4 28 00 80 52 a8 00 00 39 00 00 80 52 c0 03 5f d6',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force validate_vbmeta_public_key to unconditionally set *out_key_is_trusted=1 and return AVB_IO_RESULT_OK (0)',
            ),

            # Force LittleKernel to always emit AVB cmdline parameters even when verification is disabled (LK only!)
            'force_avb_cmdline_always': PatchStage(
                'force_avb_cmdline_always',
                pattern='e8 73 43 39 e8 01 08 37',
                replacement='e8 73 43 39 1f 20 03 d5',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Neutralize tbnz branch on VERIFICATION_DISABLED in load_and_verify_boot to always emit full AVB cmdline',
            ),

            # Force OEM factory public key digest in Root of Trust SMC 0xC2000120 to ATF / TEE (LK only!)
            'force_avb_tee_root_of_trust': PatchStage(
                'force_avb_tee_root_of_trust',
                pattern='e0 43 01 91 e2 c3 00 91 01 20 80 52 7f 61 00 94 80 00 00 34 00 05 00 f0 00 90 28 91 b7 83 01 94 e0 b3 00 91 77 61 00 94 80 00 00 34 60 04 00 90 00 38 23 91 b1 83 01 94',
                replacement='09 00 00 14 6f db 7d d2 2b f8 7c 9d ee b6 27 b7 ea 71 d3 9a eb f6 98 54 77 9b 79 53 44 cc 93 58 bd 25 af 2b 00 ff ff 10 01 08 40 a9 03 10 41 a9 e1 0b 03 a9 e3 13 04 a9',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force LittleKernel to pass OEM factory public key digest (6fdb7dd2...) to ATF/TEE via SMC 0xC2000120',
            ),

            # Force OEM factory public key digest in kernel cmdline androidboot.vbmeta.public_key_digest (LK only!)
            'force_avb_cmdline_pubkey_digest': PatchStage(
                'force_avb_cmdline_pubkey_digest',
                pattern='f9 02 00 b4 d8 02 00 b4 e0 03 00 91 c5 de 00 94 e0 03 00 91 e1 03 19 aa e2 03 18 aa cc de 00 94 e0 03 00 91 d8 de 00 94 01 04 80 52 98 14 00 94',
                replacement='09 00 00 14 6f db 7d d2 2b f8 7c 9d ee b6 27 b7 ea 71 d3 9a eb f6 98 54 77 9b 79 53 44 cc 93 58 bd 25 af 2b 00 ff ff 10 01 04 80 52 98 14 00 94',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force LittleKernel to format and emit OEM factory public key digest (6fdb7dd2...) in kernel cmdline',
            ),

            # Force set_verified_boot_state to store 0 (GREEN) into g_verified_boot_state [0x51006C18] (LK only!)
            'force_set_verified_boot_state_green': PatchStage(
                'force_set_verified_boot_state_green',
                pattern='68 07 00 b0 00 19 0c b9 c0 03 5f d6',
                replacement='68 07 00 b0 1f 19 0c b9 c0 03 5f d6',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force set_verified_boot_state to unconditionally store 0 (GREEN) into g_verified_boot_state [0x51006C18]',
            ),

            # Force set_avb_boot_state to store 0 (GREEN) into [0x50FD5510] (LK only!)
            'force_set_avb_boot_state_green': PatchStage(
                'force_set_avb_boot_state_green',
                pattern='a8 03 00 d0 00 11 05 b9 c0 03 5f d6',
                replacement='a8 03 00 d0 1f 11 05 b9 c0 03 5f d6',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force set_avb_boot_state to unconditionally store 0 (GREEN) into [0x50FD5510]',
            ),

            # Force get_lock_state to unconditionally branch to locked return path (LKS_LOCK=4) (LK only!)
            'force_get_lock_state_locked': PatchStage(
                'force_get_lock_state_locked',
                pattern='e8 04 00 f0 08 11 62 39 48 00 00 34 da 8d 01 14',
                replacement='e8 04 00 f0 08 11 62 39 02 00 00 14 da 8d 01 14',
                match_mode=MatchMode.FIRST,
                partition='lk',
                description='Force get_lock_state to unconditionally branch to locked return path (LKS_LOCK=4)',
            ),
        },
        cert_bypass=CertBypass.OVERRIDE,
    ),
]

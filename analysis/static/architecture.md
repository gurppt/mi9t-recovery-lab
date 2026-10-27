# Scope and architecture

Target: stock Xiaomi Mi 9T (davinci_global), MIUI V12.1.4.0.RFJMIXM, Android 11. Official fastboot archive MD5 is 9ce20c36aaef598af2c24c205ac72a79, matching the published archive checksum. Recovery extracted offline, with no device modification. Security patch metadata: 2021-06-01. Bootloader and critical partitions were reported locked by the connected device in prior diagnostics.

The privileged recovery accepts physical USB access in MiAssistant mode through ADB CNXN/OPEN/WRTE/OKAY/CLSE framing. An untrusted USB host should not be able to bypass FRP authorization or firmware signature validation. Baseline is AOSP recovery/minadbd; Xiaomi adds proprietary service handlers. ROM validation and FRP authorization must not be conflated.

Files: firmware/recovery.img; ramdisk/system/bin/recovery (stripped aarch64 ELF); ramdisk/system/lib64/librecovery_ui_ext.so (exports daemon_service_to_fd and file_sync_service); ramdisk/system/bin/adbd (symbols present); firmware/rawprogram*.xml; ramdisk/prop.default (ro.adb.secure=1, ro.debuggable=0). The recovery and librecovery_ui_ext both contain sync:, format-frp:, getmitoken:, failed_decrypt_error and failed_mitoken_is_NULL strings. Init scripts describe separate recovery and adbd services; exact runtime entrypoint must be verified in binary.

Observed target responses: no initialized MiToken -> failed_mitoken_is_NULL; after getmitoken -> bare format-frp returns failed_decrypt_error. No successful FRP reset. Earlier timeout/empty responses were caused or confounded by the host client's simplistic packet parsing and are not vulnerabilities.

Input surfaces: ADB service names and stream data, sideload upload blocks and signed validation metadata, potential sync protocol filenames and data, local update packages. Privileged sinks include firmware/partition writes, data formatting and reboot. Verify which are reachable before authentication and whether filesystem path checks protect device nodes.

Public lead: sidel oad-reference (directory named sideload-reference) contains Alephgsm's Windows Bypass.bat and bundled adb.exe. davinci branch does adb pull of persist/modem, patches them, and adb push of an frp file to /dev/block/sda9. Do not execute this script: it changes unrelated partitions and deletes backups. Its README claims support through MIUI12. This is a hypothesis of a separate sync service path, not a confirmed vulnerability on our target.

Prior work: no prior audit run. Existing diagnostic notes only. EDL signature reuse discussion explicitly questioned Mi9T compatibility. No target exploit confirmed; scope is firmware analysis, not buying tools or opening hardware. All dynamic device writes are deferred until independently supported and recoverable.

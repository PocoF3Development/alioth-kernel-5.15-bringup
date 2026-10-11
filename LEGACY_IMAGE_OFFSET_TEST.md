# Legacy Image offset test candidate

The working local 4.19 Image advertises ARM64 text_offset 0x80000; the failed native 5.15 candidate advertised zero. The new opt-in ARM64_LEGACY_IMAGE_OFFSET option advertises 0x80000 and requires RELOCATABLE. The native entry code preserves the physical sub-2MiB displacement in x23 and uses it for page tables and relocation. Default remains disabled for other boards. This is an experimental bootloader-compatibility hypothesis, not a proven cause or fix. Forced permissive SELinux and no-LTO development settings remain active.

The recovery diagnostic collector only copies crash information into /tmp and changes labels on those copies for retrieval. It does not write partitions. After sideload delivery, the device changed to unauthorized ADB state; device-side USB authorization is required for further commands. No new kernel device test was performed in that state.

## Actual device result

The 5.15.206-g694da97f6bf1 candidate was tested on unlocked alioth active slot A after explicit approval for vendor_boot_a/dtbo_a writes. The 4.19 baseline had sys.boot_completed=1 before the test. Both matching companion-image writes and temporary fastboot boot command succeeded, but the phone returned to fastboot at the 20-second observation without ADB enumeration. Legacy load offset alone did not resolve the failure.

Both local 4.19 companion restore writes succeeded. The temporary PBRP boot lost its USB acknowledgement; after restarting host ADB, the device appeared unauthorized. Recovery and system runtime state could not be verified then. boot_a, system and userdata were not written. No fresh crash log was collected. See legacy-offset-device-test.json for exact image hashes and scope.

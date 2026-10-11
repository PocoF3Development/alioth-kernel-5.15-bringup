# Legacy Image offset test candidate

The working local 4.19 Image advertises ARM64 text_offset 0x80000; the failed native 5.15 candidate advertised zero. The new opt-in ARM64_LEGACY_IMAGE_OFFSET option advertises 0x80000 and requires RELOCATABLE. The native entry code preserves the physical sub-2MiB displacement in x23 and uses it for page tables and relocation. Default remains disabled for other boards. This is an experimental bootloader-compatibility hypothesis, not a proven cause or fix. Forced permissive SELinux and no-LTO development settings remain active.

The recovery diagnostic collector only copies crash information into /tmp and changes labels on those copies for retrieval. It does not write partitions. After sideload delivery, the device changed to unauthorized ADB state; device-side USB authorization is required for further commands. No new kernel device test was performed in that state.

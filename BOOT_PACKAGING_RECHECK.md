# Boot packaging and mainline reference recheck — 2026-10-12

Development only. Android system boot remains unverified.

## Pinned references

- [mainlining/linux nikroks/alioth](https://github.com/mainlining/linux/tree/022f7f866a9377c34301e60ba131121c624d2e56): Linux 6.15.1. Its sm8250 fragment enables EFI_GENERIC_STUB and EFI_ZBOOT in commit 58edbdabd2efae52e02ddc712f45c63b4cb7dbd6. Device patches also cover panel/DSC, charging, audio, regulators and peripherals. Some patches explicitly carry WIP or HACK labels; those are references, not validated vendor BSP replacements.
- [pmaports-alioth](https://github.com/nasaarmas/pmaports-alioth/tree/fef537b30e81c05cd226ca6b13ca3c888c361240): packaged kernel 6.19.6, 48-bit VA/four-level tables, EFI_ZBOOT disabled, gzip Image with appended DTB. Its README identifies disabling EFI_ZBOOT as the breakthrough, after multiple config changes. This does not establish that 48-bit VA is necessary.

## Actual packaged candidate

Kernel 5.15.206-g4c19a131a42f, source-built LLVM 21, LTO disabled; 207 matching modules. Image extracted from the completed OTA boot partition:

- SHA256: 369d96010afc05a7f66a80ccfb035fbe2730426d5979109fd58b1680c93e2357.
- Raw ARM64 Image, 38,787,584 bytes; ARMd magic at offset 56, text_offset 0x80000, image_size 0x26b0000, flags 0xa. Normal MZ/PE EFI stub, not an EFI_ZBOOT compressed wrapper. EFI_ZBOOT is absent from this target tree.
- Embedded config confirms VA39 / three-level page tables, panic timeout zero, diagnostic command line and ramoops enabled. The working local 4.19 recovery also uses VA39 / three levels; retain that baseline pending stronger evidence.
- Final vendor_boot DTB plus packaged alioth overlay gives board ID 44/0, MSM ID 356 with revision 0x20001 among the supported revisions. Working recovery reports board 44/0 and MSM 356/0x20001.
- Final merged DTB reserves ramoops at 0xb0000000, size 0x400000, split into 2 MiB console and 2 MiB pmsg. This matches the working recovery reservation. No separate kmsg record allocation is configured; console logs require the backend to register.

These are checks of packaged bytes, not proof of bootloader handoff.

## Device evidence

The matched Android 17 OTA logical and boot partitions were flashed to the verified active slot and data/metadata erased under explicit user authorization. Original raw Image returned to bootloader fastboot before ADB appeared. A repeat with AVB verification disabled also returned to fastboot. A compression-only gzip candidate, preserving identical decompressed Image, ramdisk, DTB, DTBO and module bundle, returned to fastboot as well.

Temporary 4.19 diagnostic recovery boots and permits USB ADB access. Its dmesg confirms ramoops registration at the expected address and size. Pstore remained empty after the AVB-disabled raw test and the gzip-only test. Empty pstore does not establish whether the bootloader rejected the Image or the kernel died before the backend registered.

No UART hardware is used. Public records exclude device identifiers, host ADB keys, recovery policy/image payloads and raw hardware logs. The diagnostic recovery is for research only, not the production ROM.

A third packaging test used gzip Image plus appended merged alioth DTB while retaining the same vendor_boot DTB/DTBO. It also returned to fastboot before ADB appeared. Neither compression nor an appended DTB alone resolved the failure. Remaining investigations include bootloader-selected DTB and early ARM64 entry, followed by drivers/vendor initialization once kernel execution can be observed.

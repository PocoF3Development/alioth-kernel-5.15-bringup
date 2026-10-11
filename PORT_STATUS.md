# Alioth Linux 5.15 development status

**DEVELOPMENT ONLY — NOT PRODUCTION READY.** Experimental boot-test images are prepared locally. Hardware boot has not been validated, and nothing has been flashed.

## Matching candidate

Kernel `1af01637dc74748d8d160aff54841164026cf7a4`, release `5.15.206-g1af01637dc74`, uses ThinLTO, CFI and BTF. Image, native alioth DTB, core modules and external-display, KGSL, SecureMSM, display and legacy audio build successfully. All 202 staged modules pass depmod symbol/CRC checks without warnings. The 15 nonfatal BTF warnings match the reference warning set; checks were not suppressed. Original donor source remains clean and unchanged. Full upstream histories and attributed imports are preserved in public development repositories.

## Device adaptations

The native GPU/GMU translation includes resources, power levels, interconnect and regulator ownership. KGSL maps the native 64-bit IOMMU resources correctly. SDE, DSI and DISPCC use the separately imported donor 7 nm v4.1 PLL, with K11A panel commands, supplies and alioth GPIOs. The memory node follows the donor `/memory` path for bootloader RAM and DDR-type fixups.

PM8150B SMB5 and FG gen4 use translated interrupts, native ADC/IIO links and the donor battery profile. Experimental buck charging is enabled with 2 A and 4.45 V limits and JEITA retained. PD, HVDCP and the unported charge pump are disabled. Authentication is unported; charging behavior requires device measurement. FG CC_SOC reads its measured value rather than a pointer.

Earlier support includes translated UFS, USB, physical keys, reserved firmware memory, RPMh regulators, touch/fingerprint/NFC/haptics/IR imports and a nonsecure ION bridge. Compile success does not establish that all these devices work. Protected heaps/TrustZone, encryption, remote processors, camera, connectivity, full audio routing and Xiaomi panel features remain incomplete or unvalidated.

## Local image checks

The packer preserves the existing header-3 boot ramdisk and vendor ramdisk metadata, adds matching modules and first-stage load lists, and replaces the kernel and hardware DT. Explicit charging-driver entries cover missing exported OF aliases. The wildcard base board selector and board-44 overlay retain the stock selector layout. An independent unpack verifies the exact Image, original boot ramdisk, every module and metadata file, DTBO table and actual overlay merge. All images fit their partition limits. See test-image-results.json for SHA-256 checksums and test-image-validation.json for validation evidence.

These unsigned images are an experimental boot-log candidate, not proof of bootability or complete vendor compatibility. Bootloader/AVB compatibility and hardware boot evidence remain outstanding. No flashing is authorized or performed. Proprietary ramdisks, firmware and generated images are excluded from Git.

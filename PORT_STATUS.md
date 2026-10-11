# Alioth Linux 5.15 development status

**DEVELOPMENT ONLY — NOT PRODUCTION READY.** Experimental boot-test images are prepared locally. Hardware boot has not been validated, and nothing has been flashed.

## Matching candidate

Kernel `2bb7c26e43e5ee1d132dc405926d84d9bdc14afd`, release `5.15.206-g2bb7c26e43e5`, uses ThinLTO, CFI and BTF. Image, native alioth DTB, core modules and external-display, KGSL, SecureMSM, display and legacy audio build successfully. All 202 staged modules pass depmod symbol/CRC checks without warnings. The 15 nonfatal BTF warnings match the reference warning set; checks were not suppressed. Original donor source remains clean and unchanged. Full upstream histories and attributed imports are preserved in public development repositories.

## Device adaptations

The native GPU/GMU translation includes resources, power levels, interconnect and regulator ownership. KGSL maps the native 64-bit IOMMU resources correctly. SDE, DSI and DISPCC use the separately imported donor 7 nm v4.1 PLL, with K11A panel commands, supplies and alioth GPIOs. The memory node follows the donor `/memory` path for bootloader RAM and DDR-type fixups.

PM8150B SMB5 and FG gen4 use translated interrupts, native ADC/IIO links and the donor battery profile. Experimental buck charging is enabled with 2 A and 4.45 V limits and JEITA retained. PD, HVDCP and the unported charge pump are disabled. Authentication is unported; charging behavior requires device measurement. FG CC_SOC reads its measured value rather than a pointer.

Earlier support includes translated UFS, USB, physical keys, reserved firmware memory, RPMh regulators, touch/fingerprint/NFC/haptics/IR imports and a nonsecure ION bridge. Compile success does not establish that all these devices work. TrustZone runtime behavior, encryption, remote processors, camera, connectivity, full audio routing and Xiaomi panel features remain incomplete or unvalidated.

## Local image checks

The packer preserves the existing header-3 boot ramdisk and vendor ramdisk metadata, adds matching modules and first-stage load lists, and replaces the kernel and hardware DT. Explicit charging-driver entries cover missing exported OF aliases. The wildcard base board selector and board-44 overlay retain the stock selector layout. An independent unpack verifies the exact Image, original boot ramdisk, every module and metadata file, DTBO table and actual overlay merge. All images fit their partition limits. See test-image-results.json for SHA-256 checksums and test-image-validation.json for validation evidence.

These unsigned images are an experimental boot-log candidate, not proof of bootability or complete vendor compatibility. Bootloader/AVB compatibility and hardware boot evidence remain outstanding. No flashing is authorized or performed. Proprietary ramdisks, firmware and generated images are excluded from Git.

## TrustZone and protected-memory checkpoint

QSEECom, SMCInvoke and TZ logging now have translated donor DT nodes. QSEECom's three mandatory shared-heap bridge properties point at the donor-sized CMA pools used by legacy heaps 19, 26 and 27. Donor no-clock, CE instance, reentrancy and UEFI common-library contracts are retained. The release's shared-heap diagnostics use proper string formats and release their DT node reference.

Legacy ION heap 9 maps five single protection targets to native secure-system exporters. Heap 10 uses the donor 164 MiB contiguous pool and native mem-buf lending to the secure-display VMID. The exporter restricts CPU access and reclaims ownership before pages are reused. Assignment errors propagate; unknown ownership stays quarantined by native mem-buf. Legacy flag bits are not forwarded to differently defined DMA-BUF flags. Unsupported flags and mixed protection targets still fail. CMA vmperm allocation errors now preserve their errno instead of returning a null result.

The actual flag resolver passes 544 host cases. All 31 donor QSEE ioctl encodings match on ARM64 and ARM32; matching encodings do not prove matching firmware semantics. Three host fault cases exercise the actual protected-CMA wrapper and its single-VMID RW ACL. Compiled DT checks cover resources, bridge phandles and secure-display pool selection. The complete matching build and 202-module dependency/CRC audit pass; images pass independent unpack and overlay checks. Runtime SCM assignment, protected mapping denial and reclaim remain untested.

**Remaining vendor-security gates:** Kona now has an explicit native SPSS adaptation: the donor interrupt controller and mailbox, PAS14 loader, CX/MX votes, GLINK link for UEFI-loaded firmware, donor fuse selection, bounded IAR scratch and legacy three-app CMAC ioctl. Source and compiled-DT validation do not prove firmware interoperability. ION heap 13 is now implemented with the donor SPSS/HLOS shared ACL; runtime assignment and service behavior remain unverified. The donor vendor manifest includes libspcom and QTI Keymaster, so actual SPSS service behavior must be checked before claiming working authentication or existing-data decryption. Wrapped-key UFS, inline crypto, dm-crypt and dm-default-key are enabled. The newer QSEE driver treats SET_ICE_INFO as redundant and deprecates FBE_CLEAR_KEY, so ioctl-number checks alone do not establish old vendor encryption behavior.

See trustzone-provenance.json, trustzone-validation.json and secure-cma-validation.json. The test images are prepared, unsigned, unbooted and unflashed.

### Kona SPSS preparation

The donor IRQ source was imported with Chris Lew's original authorship and message; adaptations are separate commits. The controller uses native IRQ-domain dispatch, bounds bank allocation, serializes mask updates, and releases parent IRQs before its domain. The firmware payload is 960 KiB inside the 1 MiB reservation; its 4 KiB IAR scratch stays below the adjacent CDSP secure heap. No newer-SoC boot-state/debug register addresses were guessed.

All 24 legacy SPCOM/SPSS command values and layouts match actual donor headers for ARM64 and ARM32. Six host cases exercise the actual legacy CMAC handler with mocked MMIO/services, including allocation/write failures and all three application CMACs. Hardware PAS authentication, GLINK messaging, shared-memory assignment and Android boot are untested.

See spss-provenance.json, spss-abi-validation.json, spss-dt-validation.json and spss-cmac-validation.json.

Latest local experimental bundle: `test-images/5.15.206-g76bb6dd16ad2/` (`boot.img`, `vendor_boot.img`, `dtbo.img`). Complete matching kernel/DT and all 202 core/external modules built successfully. Dependency/symbol-CRC staging, partition bounds, independent unpacked-byte comparisons and actual overlay merge pass. No device boot or flashing has occurred. Runtime SPSS-HLOS shared heap assignment and vendor interoperability remain gates before claiming a working Android boot.

## SPSS/HLOS shared heap checkpoint

The latest source implements heap 13 using the donor 16 MiB reusable pool, 4 MiB alignment and below-4-GiB allocation range. Cached and uncached exporters use composite VMID 36 with RW permission; the optional HLOS flag adds VMID 3 with RW permission. Native mem-buf sharing preserves this ACL and permits composite HLOS CPU mapping only on alioth. Assignment failures propagate, and native ownership quarantine/reclaim remains in effect. Unsupported flag combinations remain rejected. Secure-display lending now uses the donor read-only permission.

The DT includes the required secure-buffer provider. SPSS firmware selection follows SoC 356 silicon revision: v1 uses spss1 names, v2/v2.1 use spss2 names; unknown revisions fail explicitly. Host fault, flag, permission, firmware-selection and compiled-DT checks pass. These checks do not prove real hypervisor assignment, SPSS service operation or Android boot. Heaps 14 and 20 are implemented in the following checkpoint; encryption still requires runtime verification. No device has been flashed or booted.

## CDSP, camera and wrapped-key compatibility checkpoint

Heap 14 now selects the native secure-carveout exporter over the donor fixed 70 MiB region at 0x8e100000, with CP_CDSP token 0x20000000. Cache selection is ignored as in the donor; mixed protection targets are rejected. The native allocator now preserves vmperm allocation errors. Heap 20 accepts nonsecure cached/uncached requests and the camera/system fallback mask, using native system-page exporters. The donor camera allocator rejects secure requests, and this bridge does too. Allocation and SG/cache behavior are translated; donor camera reserve/refill policy and task-name routing are not reproduced. Heap queries now return donor MSM type values 7/8/9/10 rather than the newer kernel enum.

The local stock ramdisks use fscrypt v2, inlinecrypt_optimized, wrappedkey_v0 and dm-default-key metadata encryption. Those native paths are enabled. Donor/native SCM storage key commands match (5: program, 6: clear, 7: derive), with UFS CE 10. Wrapped bytes remain unchanged; raw AES-XTS words retain the donor byte order. ICE/SCM allocations now propagate errors and release/clear key material on failure. A failed derivation cannot overwrite the caller's secret with a failed result. Alioth QSEE ioctls validate copied payloads; legacy key-clear returns the donor disabled-PFK ENODEV rather than claiming key eviction.

The rebuilt candidate uses LTO_NONE, with Clang CFI disabled because it requires LTO; BTF remains enabled. Hardware key derivation, secure ownership, userdata mounting, vendor services and Android boot remain untested. No flashing is performed.

Latest complete matching build and independently validated image bundle: `5.15.206-g76bb6dd16ad2`. All 202 modules pass dependency and symbol-CRC staging checks. The boot/vendor_boot/dtbo sizes are 40,349,696 / 83,611,648 / 320 bytes, within recorded partition limits. The actual unpacked kernel configuration confirms LTO_NONE without Clang CFI. Hardware and Android boot remain untested.

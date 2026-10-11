# Vendor driver integration checkpoint

The native DT needs downstream RPMh ARC corner vote regulators for Qualcomm's modified GCC/GPUCC implementation. pending/sm8250-xiaomi-alioth-corners.dtsi preserves the donor MX/CX/GFX corner definitions and native clock supply names. It is staged outside the active kernel tree until the current Image build finishes. REGULATOR_RPMH must be available before these clocks probe; the current candidate has it modular. Do not treat the native MTP supply topology alone as sufficient.

Release-pinned KGSL, Kona display and legacy Kona audio source compilation reaches LTO. Their module link probes require core provider exports and external-display symbols; core module build is running. No unresolved-symbol checks have been suppressed. Initial display invocation without CONFIG_DRM_MSM built an empty target and is superseded by the actual CONFIG_DRM_MSM=m probe.

Alioth FocalTech SPI, Xiaomi touchfeature, FPC and Goodix sources and the Xiaomi notification chain compile. The display chain still needs actual display lifecycle emitters. The translated input DT includes donor GPIO/regulator/bus wiring and haptic calibration/RTP data. This is compile evidence only.

CS35L41 imports preserve donor authorship, including the platform header and diagnostic fixes. Separate 5.15 adaptations use asoc_rtd_to_codec, mute_stream with no_capture_mute, symmetric_rate, current debugfs APIs and a private static DSP helper. TFA9874 source is staged but has a MUNCH-only firmware variable guard; it is not enabled for alioth. Machine routing and amplifier DT are still required.

Existing October 11 alioth user boot and vendor_boot images were inspected read-only. Both use header 3; DTB is in vendor_boot. Unpacked components and exact mkbootimg arguments are under boot-input/. No images are flashed or published.

## Updated integration

Clock ARC definitions are now integrated and REGULATOR_RPMH/proxy-consumer are built in. Native mode constants are isolated from the legacy ARC header. The alioth notification chain now has release DSI bridge and low-power lifecycle emitters, gated on CONFIG_XIAOMI_DRM_NOTIFIER and primary display_type; both objects compile with the notifier enabled. Module linking against matching candidate exports is still pending.

Full LTO is temporarily replaced by user-authorized ThinLTO. WSL interruption recovery and exact pending gates are recorded in integration-checkpoint.json. Existing DTBO has one version-0 entry, page size 4096, id/rev/custom fields zero; its old overlay must not be applied unmodified to the native DT. Header-3 packing metadata is preserved under boot-input/.

## SPSS/HLOS shared heap checkpoint

The latest source implements heap 13 using the donor 16 MiB reusable pool, 4 MiB alignment and below-4-GiB allocation range. Cached and uncached exporters use composite VMID 36 with RW permission; the optional HLOS flag adds VMID 3 with RW permission. Native mem-buf sharing preserves this ACL and permits composite HLOS CPU mapping only on alioth. Assignment failures propagate, and native ownership quarantine/reclaim remains in effect. Unsupported flag combinations remain rejected. Secure-display lending now uses the donor read-only permission.

The DT includes the required secure-buffer provider. SPSS firmware selection follows SoC 356 silicon revision: v1 uses spss1 names, v2/v2.1 use spss2 names; unknown revisions fail explicitly. Host fault, flag, permission, firmware-selection and compiled-DT checks pass. These checks do not prove real hypervisor assignment, SPSS service operation or Android boot. Heaps 14 and 20 are implemented in the following checkpoint; encryption still requires runtime verification. No device has been flashed or booted.

## CDSP, camera and wrapped-key compatibility checkpoint

Heap 14 now selects the native secure-carveout exporter over the donor fixed 70 MiB region at 0x8e100000, with CP_CDSP token 0x20000000. Cache selection is ignored as in the donor; mixed protection targets are rejected. The native allocator now preserves vmperm allocation errors. Heap 20 accepts nonsecure cached/uncached requests and the camera/system fallback mask, using native system-page exporters. The donor camera allocator rejects secure requests, and this bridge does too. Allocation and SG/cache behavior are translated; donor camera reserve/refill policy and task-name routing are not reproduced. Heap queries now return donor MSM type values 7/8/9/10 rather than the newer kernel enum.

The local stock ramdisks use fscrypt v2, inlinecrypt_optimized, wrappedkey_v0 and dm-default-key metadata encryption. Those native paths are enabled. Donor/native SCM storage key commands match (5: program, 6: clear, 7: derive), with UFS CE 10. Wrapped bytes remain unchanged; raw AES-XTS words retain the donor byte order. ICE/SCM allocations now propagate errors and release/clear key material on failure. A failed derivation cannot overwrite the caller's secret with a failed result. Alioth QSEE ioctls validate copied payloads; legacy key-clear returns the donor disabled-PFK ENODEV rather than claiming key eviction.

The rebuilt candidate uses LTO_NONE, with Clang CFI disabled because it requires LTO; BTF remains enabled. Hardware key derivation, secure ownership, userdata mounting, vendor services and Android boot remain untested. No flashing is performed.

# Final changelog — project archived 2026-10-12

Development only; not production ready. Work stopped at the user's request. No kernel or Android build jobs were running at the shutdown check. No further builds, flashes, wipes, or device tests are planned.

## Outcome

Linux 5.15 has NOT successfully booted recovery or Android on alioth. A complete Android 17 Evolution X source build and OTA installation succeeded, but the resulting system did not boot. No useful 5.15 Linux crash console was recovered. Compilation, ABI checks and successful installation do not establish bootability.

## Implemented development work

- Established a Qualcomm Linux 5.15.206 release-based tree and published attributed donor ports with full upstream ancestry in PocoF3Development.
- Added alioth/SM8250 DT translations for storage, USB, regulators, GPU/GMU, display/DSI/PLL, PMIC charging and fuel gauge, reserved memory, TrustZone and SPSS. This remains an incomplete board port, not full parity with the working donor DTS.
- Imported/adapted Xiaomi peripheral drivers and configuration fragments; integrated core and nine external driver groups into the Android source build using checkout Android Clang r563880c.
- Added legacy ION and secure/shared heap compatibility, including heaps 13/14/20, and vendor encryption interface adaptations. Runtime firmware, ownership, encryption and peripheral behavior remain unvalidated.
- Added matching source-built module packaging, load lists, built-in metadata, dependency and symbol CRC checks, and source/image validators. This product places modules in vendor and the vendor ramdisk; it does not define separate system_dlkm/vendor_dlkm partitions.
- Made system and recovery permissive for development; created private root-ADB diagnostic recovery controls. These settings are unsuitable for production.
- Corrected Qualcomm bootloader UFDT compatibility: packaged base DTB includes /__symbols__, and overlay includes /__fixups__. Retained firmware logs then confirmed overlay application and UEFI ExitBootServices.
- Added opt-in early trace and Immensity-inspired legacy ramoops diagnostic support in a separate experimental branch. Recovery-to-recovery retention worked; physical resets could clear retained evidence.
- Added missing ARM64 vDSO function prototypes for W=1 validation. The related validated 4.19 fix was published separately.

## Completed validation

- Full m evolution build completed, including the module metadata corrections.
- Installed EvolutionX-17.0-20261012-alioth-12.3-Unofficial.zip through normal recovery ADB sideload; the user wiped data afterward. Installation succeeded, system boot failed.
- Read back slot B boot/vendor_boot/dtbo: all three matched the OTA payload manifest hashes. Kernel/DTB and vendor ramdisk module contents matched the validated no-LTO build. OTA repacking means standalone product-image hashes are not the authoritative installed-image comparison.
- Audited 207 modules, early/recovery/charger lists, staged partition contents, dependency closure, built-in metadata and module CRCs. Actual vendor filesystem contents matched staging.
- Separate ThinLTO kernel plus external-driver build succeeded at local kernel revision 920909676d2e8838e95595c4f646cb24a04ec2e9. Its audit found 207 uniquely named modules and 18,580 unique exported symbol providers, with no missing providers, duplicate providers or CRC mismatches. Embedded Image configuration and exported headers were checked. This ThinLTO candidate was not installed as a replacement OTA.
- Native Sparse checked 3,154 units but reported 6,899 warnings and 369 error lines despite returning zero. It is NOT a clean static-analysis pass. DT schema checks also reported findings; missing BSP bindings and reference-schema mismatches limit interpretation.
- Installed Sparse, cppcheck, Smatch and DT schema tooling. Remaining Smatch/clang-tidy/cppcheck analysis was not completed before archiving.

## Device state at stop

Slot A was restored to the matching working 4.19 diagnostic boot/DTBO and permissive root-ADB vendor_boot. ADB lists recovery. Slot B retains the freshly installed no-LTO 5.15 OTA. No claim is made that rebooting to system will work. The final corrected 48-bit/four-level recovery control also exposed no USB; its retained logs were not collected before work was stopped.

## Remaining gates

- Establish reliable evidence of 5.15 Linux entry and the first failing boot stage without UART. Firmware ExitBootServices alone is insufficient.
- Complete the donor board DT translation. Native DTB size is about 154 KB versus about 844 KB for the working donor live DTB; size alone is not a correctness test, but coverage remains incomplete.
- Resolve the early boot failure before claiming module probe, storage/mount, ADB, display, TrustZone, secure heaps or Android vendor compatibility.
- Validate charging safety, encryption/keymaster, modem/WLAN, audio, cameras, sensors, suspend and all other hardware at runtime.
- Triage static/schema findings and reconcile local ThinLTO configuration edits with manifest pins before reproducing a new ROM.

## Final source publication

All source repositories were published to PocoF3Development. The two formerly local kernel commits were reworded only to correct attribution, without changing source trees or authors; the metadata mapping is retained in publication-provenance.json. Published upstream/donor history was not rewritten.

The final device profile preserves the local ThinLTO integration edits and pins the final dependency checkpoints. Ordinary builds default to 4.19; 5.15 requires explicit opt-in. This source publication did not run builds or device tests. The old installed no-LTO OTA and its module/image records remain distinct from the separately validated ThinLTO build.

The canonical external manifest pins every source project, including the device integration revision. The manifest inside the device repository follows its own integration branch to avoid an impossible self-referential commit hash; use the external manifest for an immutable snapshot.

## Per-repository handoff

### core kernel

Repository: [android_kernel_xiaomi_sm8250-5.15](https://github.com/PocoF3Development/android_kernel_xiaomi_sm8250-5.15).

Completed: Ported alioth DT and Xiaomi peripherals, legacy ION/secure heaps 13/14/20, SPSS and vendor encryption interfaces; added UFDT, legacy-offset and retained-log diagnostics. Linux 5.15.206 and external modules compiled. Separate ThinLTO audit covered 207 modules and 18580 unique export providers without missing providers or CRC mismatches.

Missing or unvalidated: 5.15 never booted recovery or Android. No useful Linux crash console was recovered. Board DT coverage, early-entry evidence and all vendor/hardware runtime behavior remain incomplete or unvalidated.

Required next work: Locate the first Linux boot failure without UART, finish donor DT/binding translation, then validate storage, secure firmware, encryption, charging, graphics and peripheral probes. Triage Sparse and DT-schema findings before production hardening.

### legacy audio

Repository: [android_vendor_qcom_opensource_audio-kernel-legacy-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_audio-kernel-legacy-5.15).

Completed: Imported attributed Xiaomi audio/codec changes and MIUS integration; adapted legacy compressed-audio component callbacks and native effect UAPI aliases for the 5.15 source module build.

Missing or unvalidated: No working 5.15 audio runtime. DSP firmware compatibility, board routing, codec/amplifier probes, speaker output and MIUS behavior remain unvalidated.

Required next work: After core boot, validate firmware and board routing, codec probes, PCM/offload/voice paths and amplifier behavior; complete any unsupported donor interfaces.

### display drivers

Repository: [android_vendor_qcom_opensource_display-drivers-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_display-drivers-5.15).

Completed: Imported Xiaomi display changes, connected blank notifications to DSI lifecycle and adapted the alioth external 7 nm PLL. Fixed selected debugfs-disabled initialization and LLVM prototype issues.

Missing or unvalidated: 5.15 recovery/system did not boot; panel/PLL probes, display output, refresh switching and Xiaomi panel features are not hardware validated.

Required next work: Finish the native panel and power/clock binding integration, establish boot logs and test PLL lock, panel bring-up and refresh/touch behavior.

### graphics

Repository: [android_vendor_qcom_opensource_graphics-kernel-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_graphics-kernel-5.15).

Completed: Integrated release-pinned KGSL with the source build, corrected native DT register-range translation and selected the internal kernel API header explicitly. GPU/GMU DT work is in the core tree.

Missing or unvalidated: GPU firmware initialization, IOMMU mappings, clocks and rendering are unvalidated because 5.15 did not boot.

Required next work: Validate GPU/GMU resources and firmware on a booting core; exercise graphics allocation, rendering, fault reporting, suspend and recovery.

### SecureMSM

Repository: [android_vendor_qcom_opensource_securemsm-kernel-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_securemsm-kernel-5.15).

Completed: Integrated QSEECom/secure drivers and native headers; corrected shared-heap diagnostics/node references and preserved donor ICE copy/error behavior. Core-tree ports implement legacy heap and encryption bridges.

Missing or unvalidated: SCM ownership transfer, protected-memory reclaim, SPSS/Keymaster interoperability and encrypted userdata mounting are unvalidated.

Required next work: After early boot, verify secure firmware contracts, heap ownership, QSEE/SPSS services and encryption with real vendor userspace; retain failure propagation.

### multimedia helpers

Repository: [android_vendor_qcom_opensource_mm-drivers-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_mm-drivers-5.15).

Completed: Published the release-pinned multimedia/helper tree with full ancestry and integrated the selected external-display module source into the matching build.

Missing or unvalidated: Compile integration does not establish external-display/audio or multimedia hardware behavior; additional donor binding parity may be required.

Required next work: Validate enabled helper probes and consumers after core boot; reconcile selected feature configuration with actual alioth hardware.

### camera

Repository: [android_vendor_qcom_opensource_camera-kernel-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_camera-kernel-5.15).

Completed: Published full-history release-pinned native camera sources and included the source driver group in the matching Android kernel/module build.

Missing or unvalidated: The Xiaomi camera board port is incomplete. Sensor resources, regulators, context banks, IOMMU streams and old vendor HAL interoperability are not validated.

Required next work: Translate donor camera topology and bindings for this driver, then validate firmware, probes, allocation/IOCTL contracts and each camera on a booting system.

### WLAN platform

Repository: [android_vendor_qcom_opensource_wlan_platform-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_wlan_platform-5.15).

Completed: Published full-history release-pinned CNSS platform sources and integrated the native platform driver module group.

Missing or unvalidated: Wi-Fi firmware startup, platform power/PCIe resources, recovery and suspend/resume are untested on 5.15.

Required next work: Reconcile alioth connectivity resources and firmware selection, then validate CNSS probes, firmware loading, recovery and suspend behavior.

### QCACLD WLAN

Repository: [android_vendor_qcom_opensource_wlan_qcacld-3.0-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_wlan_qcacld-3.0-5.15).

Completed: Adapted detection of Android cfg80211 multi-link API backports and selected LLVM 21 prototypes/array declarations; integrated native QCACLD into the source module build.

Missing or unvalidated: No successful 5.15 boot or verified Wi-Fi connection. Firmware/target compatibility, scanning, association and recovery remain runtime gates.

Required next work: Test the matching CNSS/host-common/fw-api set on a booting core; validate firmware, scan/association, traffic, roaming and suspend/recovery.

### WLAN firmware API

Repository: [android_vendor_qcom_opensource_wlan_fw-api-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_wlan_fw-api-5.15).

Completed: Published the complete release-pinned firmware interface source history and supplied matching headers to the WLAN source build.

Missing or unvalidated: Header compilation does not establish compatibility with alioth firmware or target selection.

Required next work: Verify the firmware/target contract against the paired platform, QCACLD and host-common drivers, then test WLAN hardware behavior.

### WLAN host common

Repository: [android_vendor_qcom_opensource_wlan_qca-wifi-host-cmn-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_wlan_qca-wifi-host-cmn-5.15).

Completed: Integrated release-pinned host-common/QDF sources; fixed debugfs-disabled list API inclusion and selected explicit no-argument definitions for LLVM 21.

Missing or unvalidated: No hardware validation of the paired WLAN stack on 5.15; runtime ownership, recovery and suspend behavior remain untested.

Required next work: Validate the matched firmware/platform/QCACLD set and triage shared-driver failures once core boot and reliable logging are available.

### alioth device integration

Repository: [android_device_xiaomi_alioth](https://github.com/PocoF3Development/android_device_xiaomi_alioth).

Completed: Integrated source-built core and nine external driver groups, Android Clang r563880c, matching module load/metadata placement, native UAPI export, UFDT image packaging and permissive development settings. A no-LTO Android 17 Evolution X OTA built and installed. Final development profile selects ThinLTO; ordinary builds default to maintained 4.19.

Missing or unvalidated: Installed no-LTO 5.15 system did not boot. Separate ThinLTO validation is not a rebuilt/installed complete ROM. Full donor DT and vendor runtime compatibility remain incomplete.

Required next work: Explicitly opt in to 5.15 only for development; use matched source-built images/modules, resolve early boot and validate recovery/system before production SELinux and complete hardware testing.

### SM8250 common integration

Repository: [android_device_xiaomi_sm8250-common](https://github.com/PocoF3Development/android_device_xiaomi_sm8250-common).

Completed: Added native UFS BSG permissions, native WALT tuning paths and USB-controller selection from boot arguments while retaining the legacy common-device base.

Missing or unvalidated: Common boot/runtime behavior on 5.15 is unvalidated; changing init paths does not prove working USB or scheduler behavior.

Required next work: Validate init/ueventd permissions, native USB naming, post-boot tuning and legacy vendor services after core boot.

### boot control

Repository: [android_hardware_qcom_bootctrl-5.15](https://github.com/PocoF3Development/android_hardware_qcom_bootctrl-5.15).

Completed: Adapted GPT utilities to discover native UFS BSG paths instead of relying on a fixed legacy controller path. Kept full upstream ancestry.

Missing or unvalidated: The 5.15 system did not boot, so native boot-control operation and permissions were not hardware validated.

Required next work: Validate native BSG access, partition discovery, slot metadata and OTA boot-control behavior on a booting system.

### video codec

Repository: [android_vendor_qcom_opensource_video-driver-5.15](https://github.com/PocoF3Development/android_vendor_qcom_opensource_video-driver-5.15).

Completed: Integrated Kona VIDC sources, portable trace includes and native legacy V4L2 ABI compatibility; retained donor bitrate values and removed the obsolete PIL module soft dependency.

Missing or unvalidated: Codec firmware startup, memory/resource bindings and old vendor encode/decode behavior remain unvalidated.

Required next work: After core boot, reconcile VIDC DT/firmware resources and test legacy ioctl contracts, supported codec formats and lifecycle/error paths.

### display HAL

Repository: [android_hardware_qcom_display-sm8250-5.15](https://github.com/PocoF3Development/android_hardware_qcom_display-sm8250-5.15).

Completed: Integrated native kernel DRM/UAPI headers, a legacy IDisplayConfig 1.9-to-2.0 bridge, gralloc validation/failure handling and corrected native-format diagnostics.

Missing or unvalidated: Source compilation does not validate old graphics blobs, allocation layouts, composer output or refresh behavior on 5.15.

Required next work: Validate gralloc/Adreno layouts and display-service IPC with actual vendor userspace; exercise composer, rendering and refresh switching after core display works.

### Android build integration

Repository: [android_vendor_lineage-5.15](https://github.com/PocoF3Development/android_vendor_lineage-5.15).

Completed: Preserved native kernel UAPI outputs inside Soong sbox and source-built module/built-in metadata during Android packaging. The integrated no-LTO Android 17 ROM completed.

Missing or unvalidated: No successful 5.15 Android boot. A complete matching ThinLTO ROM remains unbuilt/uninstalled, and runtime vendor compatibility is unvalidated.

Required next work: Reproduce a matched source/kernel/module/image build when development resumes; resolve early boot before claiming usable Android or production readiness.

### bring-up records

Repository: [alioth-kernel-5.15-bringup](https://github.com/PocoF3Development/alioth-kernel-5.15-bringup).

Completed: Preserved source provenance, manifests, validation scripts and build/ABI/packaging/device-test results. Full Android 17 no-LTO build and recovery sideload succeeded; separate ThinLTO module audit passed.

Missing or unvalidated: 5.15 did not boot recovery or Android and no useful Linux crash console was recovered. Static/schema findings and incomplete donor-board coverage remain open.

Required next work: Use the final archived status and pinned source revisions as the handoff; establish early Linux evidence without UART, complete board translation and validate hardware/vendor behavior before resuming production work.

## Preserved test evidence

Workspace: ~/evo/kernel-research/alioth-5.15. Frozen installed-build inputs are under rom-build-images/2026-10-12-ufdt-module-complete-nolto/. Installation/readback evidence is under device-test/2026-10-12-system-boot/full-ota-sideload-test/. ThinLTO outputs are under out/thinlto-validation/; public result files are thinlto-final-build-result.json and thinlto-abi-validation.json.

The original ThinLTO tested revision is 920909676d2e8838e95595c4f646cb24a04ec2e9. Final publication uses the identical source tree after unpublished message-only corrections and the status-only checkpoint. Generated binaries retain the original tested version string and are not claimed to be rebuilt from the final archive commit.

Raw device logs, private ramdisks, generated images, credentials and host keys remain local. Older reports retain historical checkpoints; this document supersedes their current-status and unflashed statements.

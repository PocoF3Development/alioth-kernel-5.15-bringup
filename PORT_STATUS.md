# Alioth 5.15 bring-up — 2026-10-11

Branch: alioth-bringup; revision: dd3744315d2babeb7653bfea5c2c1f95750537dd.
Donor adaptations: after a9d9833cb5121c979b503d612b50595f1b5a28a7, excluding the merge. All 272 later commits are indexed in donor-range.json; driver groups in donor-subsystems.json. Earlier imports are labeled prerequisites, not post-boundary Xiaomi changes.

## Completed

Fetched the release-pinned core, Android common kernel, Clang r450784e (14.0.7), build scripts, dtc and board/driver dependencies. sync-results.json records all 19 small dependency checkouts. The standalone compile uses four jobs and a separate output tree.

Staged 138 unmodified donor DT/binding files with hashes and attribution in donor-provenance.json. This closes all local includes for Kona v1/v2/v2.1 and alioth overlay. These files are not installed into the 5.15 kernel.

Imported the 12 Qualcomm NFC prerequisites and single post-boundary Xiaomi NFC adaptation, preserving original authors/messages. Added separate 5.15 Kconfig/Kbuild integration. NFC_NQ=m resolves through Kconfig, and nq-nci.o compiles with the release compiler. Hardware behavior remains untested; module linking is recorded below.

## Compatibility gates

| Area | Evidence | Required next work |
| --- | --- | --- |
| Downstream DT | Supplied manifests have no DT project. Public r66 DT revision 96dcafd5f50bc2b5446872aabfa50d66bfeb5f8b has no Kona files. | Obtain matching DT source or translate donor nodes to native 5.15 bindings. Reference DT checkout is not a release dependency. |
| Clock bindings | Shared numeric IDs change: GCC 208, display 32, GPU 9, video 22, NPU 44. Some symbols are absent. | Use native symbolic headers and audit compatible strings; never carry old numeric IDs across unchanged. See clock-binding-translation.json. |
| ION | Device selects legacy libion. libgsl embeds /dev/ion and /dev/kgsl-3d0. libgsl, libcvp2 and libcdsprpc import ion allocation functions. New Kona config selects QCOM_DMABUF_HEAPS. | Restore required legacy allocation semantics or prove an ABI-compatible adaptation. A libion shim alone does not cover direct /dev/ion opens. |
| Power | 5.15 has SMB5 and FG-gen4; donor adds Xiaomi battery/charging behavior. | Translate selected post-boundary changes against new IIO/power-supply APIs; retain thermal protection. |
| Peripherals | Donor haptics/touch/fingerprint changes indexed. Xiaomi platform/notifier interfaces differ. | Port selected drivers and dependencies, then compile and check actual board wiring. |
| Multimedia | External audio/camera/display/graphics sources pinned and fetched. Legacy audio explicitly supports Kona. | Audit stock vendor ioctls, firmware, memory heaps and driver nodes before porting Xiaomi adaptations. |
| Boot | Alioth uses header 2/3; reference defaults to header 4/init_boot/DLKM. | Preserve alioth bootloader and partition requirements when packaging. |

## Validation

Logs are under logs/. compile-results.json records the core Image probe, nfc-probe-results.json the NFC object probe. No alioth boot image has been packaged or flashed. Existing 4.19 kernel and ROM configuration remain unchanged.

## Further peripheral work

Imported the exact post-boundary Xiaomi platform selection as an attributed source commit, then adapted its 5.15 Kconfig include separately. MACH_XIAOMI_ALIOTH selects the shared Xiaomi/SM8250 platform flags correctly in the probe configuration.

Imported all seven post-boundary AW8697 commits, preserving authors and stable patch IDs. A separate adaptation commit uses cpu_latency_qos calls, monotonic ktime-based microsecond calibration, the native min helper, and a composite module containing driver plus ring buffer. Both objects and the composite object compile successfully. Runtime calibration and RTP playback are not yet verified. No changes were made to haptic firmware or the production HAL.

## Completed compile/link milestone

- Core Image built successfully from the pinned 5.15.206 reference source/config (about 45 MiB). Full LTO, CFI and BTF were kept enabled.
- Both nq-nci.ko and aw8697_haptic.ko compiled, completed LTO and modpost, linked and received BTF against the reference core exports. The module probe uses copies outside the port repository to avoid generated artifacts in source.
- Modules use the reference core release string, 5.15.206-g5bce8cbd7a74. This is compile/link evidence, not an installable alioth release.
- The reference core has 15 resolve_btfids warnings. Their exact function IDs are absent from emitted BTF and are recorded in btf-warning-audit.json. BPF function availability/runtime must be audited before a production build. No BTF or CFI checks were disabled to hide these warnings.
- artifacts.json records hashes, sizes and module metadata. peripheral-module-results.json records successful module builds; nfc-probe-results.json now records all successful object checks, including haptics.

The next substantial step is an alioth DT/config capable of early boot, plus the required legacy allocator/vendor ABI adaptation. No packaged alioth boot image exists yet.

## Alioth DT and allocator milestone

Added a native alioth DT compile probe with board ID 44, donor SoC revision identifiers, native regulator/clock bindings, UART12, UFS and USB1 peripheral mode. It compiles successfully; DT_TRANSLATION.md records missing board validation and firmware handoff gates. Native MTP regulator limits are still provisional for alioth. No downstream clock IDs were copied.

Added an opt-in /dev/ion modern-ABI system heap bridge. Cached/uncached allocations map heap ID 25 to native QCOM DMA heaps; other heaps/flags fail closed. Existing native ION UAPI remains unchanged. ARM32 and ARM64 layout/ioctl assertions pass for both donor and native headers. The bridge compiles and links against reference exports with LTO/modpost/BTF. ION_COMPATIBILITY.md records remaining secure/carveout/vendor gaps.

alioth-earlyboot.config resolves native clocks, pinctrl, SCM, RPMh regulators, interconnect, UFS PHY/controller and console as built-ins. Seven affected native/bridge objects compile successfully in a separate alioth output directory. This is not a full alioth Image build or runtime validation. Driver results and resolved symbols are saved in alioth-native-driver-results.json and alioth-earlyboot-config-results.json.

No boot image has been packaged or flashed. Before packaging a boot-ready test image, reconcile donor reserved memory/firmware handoff and UFS quirks, translate remaining required heap types, and supply a matching built-in kernel/initramfs and alioth boot header/DT selection. Production kernel/ROM sources remain unchanged.

## Current integration checkpoint (supersedes earlier revision and build-mode notes)

Kernel HEAD: 5f037a60c3c2b98c132903ac0c0309c515848739. User authorized temporary ThinLTO for bring-up. CFI/BTF remain enabled; eight compile jobs and four linker threads. Full LTO first candidate failed on missing built-in provider dependencies. IPC logging, QTI regmap, GDSC, RPMh ARC, memory-buffer, secure-buffer and IOMMU providers are now built in, with regulator proxy votes enabled. A disabled proxy helper header stub needed static inline to avoid duplicate global definitions when regulators are built in.

Translated and compiled touch/fingerprint/NFC/haptics DT plus exact donor static firmware reservations. Native IR SPI2/GPIO115-118 and its no-control supply are integrated. KTZ8866/dual KTZ8866 objects compile after a separate procfs/buffer-validation adaptation. PS5169 source imports retain authorship but its private power-supply ABI remains unresolved and it is disabled; no alioth node was found in the merged donor DT.

The native DT now supplies MX/CX/GFX ARC votes without overwriting native PMIC mode constants. Native memory-buffer HLOS VMID is defined. Nonsecure ION heap IDs 25/22/26 use system or donor-sized CMA backing (SDSP 8 MiB; contiguous 16 MiB below 4 GiB). Only registered heap pairs are advertised. Secure flags, mixed masks, camera and other unported heaps still fail explicitly.

Release display blank notification hooks compile with Xiaomi notifier enabled. External-display provider and CS35L41 module probes link. Full vendor modules still need the matching candidate core export table and native board DT integration.

The complete staged donor DT translation also compiles and its overlay applies. This is a binding audit reference, not the selected candidate DT: legacy msm-bus, PIL and other unsupported interfaces must be translated, so using it directly would not be boot ready. See pending/vendor-dt-compatible-audit.json and pending/vendor-dt-unmatched-enabled.json; metadata and child compatibles are not automatically missing independent drivers.

WSL restarted during the first ThinLTO build. Generated archives and objects with invalid magic were regenerated, including an empty probes archive that broke linking. build-output-repair.json records the scoped output repair. The production tree is unchanged. No test image has been packaged or flashed; the candidate core build is still in validation.


## Latest verified checkpoint

Candidate source 56b0b9a5ac82f372e2023321344ff05ee0bff018 with ThinLTO builds `Image` and `qcom/sm8250-xiaomi-alioth.dtb` successfully (see alioth-build-results.json). QTI_CRYPTO_TZ is enabled to provide the storage encryption backend. Matching core modules and external vendor modules still require validation; display, charging, audio, protected heaps and boot-image packaging remain incomplete. This is not a boot-validated or production-ready release. No flashing was performed.

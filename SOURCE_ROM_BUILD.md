# Android source-built alioth 5.15

Development only; hardware Android boot is unverified. No candidate was flashed
in this source-build pass.

The default device profile now uses native Kbuild with Android checkout Clang
r563880c / LLVM 21, integrated assembly, and no LTO. Core modules and nine vendor
driver groups are built in dependency order. DTB/DTBO are generated from that same
core configuration. No exported prebuilt kernel/module bundle is used.

The device profile contains a pinned manifest for all 11 core/driver/header
repositories and native source/tool/revision dependencies. An explicit `false`
selector preserves the donor 4.19 profile; malformed selectors, missing sources
and unsupported partition layouts fail instead of selecting a hidden fallback.

Real compilation found and fixed Qualcomm compressed-audio UAPI mismatches,
Bionic sched_param redefinition, and missing legacy buffer-sizing headers. The
native compressed ioctl path now also routes next-track codec options through
the component API to the legacy DSP callback. ARM64/ARM comparisons show equal
core/driver sizes, offsets, codec IDs and ioctl values. Scheduler and graphics
headers compile alongside Bionic headers for both Android ABIs.

Current build status: the Android-generated kernel target compiled the core
Image, DTBs and all eight external groups with LLVM 21 and no LTO. All 206
packaged modules pass CRC checks and match across vendor/vendor ramdisk; the 24
first-stage load entries also match. `m bootimage vendorbootimage dtboimage` subsequently passed through the normal
Android/SISO sandbox with source directories read-only. Packaged kernel/config,
DTB/overlay, all 206 vendor-ramdisk modules/metadata and AVB verification passed.
`m evolution` is running again; the final ROM ZIP remains pending. The older completed prebuilt-profile ROM build is archived in
FULL_ROM_BUILD.md and does not establish this new source profile's completion.

Header validation records: compressed-audio-uapi-validation.json,
scheduler-uapi-validation.json, display-uapi-validation.json.

Hardware gates remain open, including secure firmware/FBE, legacy camera/video,
remote storage, WLAN, panel initialization and charging. Source compilation does
not establish any of those runtime results. Images/vendor blobs stay local.

Legacy VIDC userspace headers, Qualcomm V4L2 controls and missing formats/flags are exported from the Xiaomi donor while retaining generic 5.15 V4L2. Individual headers pass Android ARM and ARM64 Clang syntax checks. The historical `msm_vidc.h` and `msm_vidc_utils.h` are alternative ABI headers and are tested separately, as used by their callers. This does not supply a VIDC kernel driver or establish hardware video operation.

Display compatibility exports SDE HDR types through the legacy `msm_drm.h` include path and Qualcomm DX/TIGHT/TILE/ALPHA_SWAP modifiers through `drm_fourcc.h`. HDR includes pass both Android ABIs with display HAL flags; the original failing ARM gralloc translation unit compiles with the revised headers. Existing Android KERNEL_OBJ contained an older 4.19 Image before source compilation: it is not evidence of the new candidate. Final validation requires an embedded 5.15 configuration and matching release/module CRCs.

The compiled kernel release is `5.15.206-g67e836f4cb83`. LLVM 21 exposed and fixed explicit minidump typing, old-style touch/display/WLAN definitions, a WLAN array-bound declaration mismatch, the compressed callback placement, and ambiguity between KGSL internal/UAPI headers. Audio fallbacks now retain native Qualcomm codec/metadata declarations. V4L2 import continuation lines, flush commands and private events were corrected; the encoder translation unit passes an isolated compile. See android-source-build-validation.json and venc-source-compile-validation.json.

The kernel-target compile completed successfully through Android’s generated Ninja graph. The following full `m evolution` pass regenerated host tools and expanded into a broad platform rebuild; its completion is pending. Kernel/module verification is complete independently of the ROM packaging result.

External drivers are staged from Git-tracked and non-generated local source files beneath KERNEL_OBJ. Old objects, module files, Kbuild commands and symbol-version artifacts are excluded. Source revisions and a content digest are recorded in external-source-staging.json; the ABI validator uses the staged Module.symvers files. This preserves Android’s read-only source sandbox. The validated local bundle is rom-build-images/source-5.15.206-g67e836f4cb83-llvm21; it is a development test candidate, not a proven system boot.

The subsequent full-build readiness pass added native DSP loader connections, Kona VIDC as the ninth external group, and QCA6390/CNSS PCIe0 resources. The new 207-module source profile is pinned in the device manifest. Isolated VIDC and GCC/video clock compiles and compiled DT/legacy-ABI checks pass; full `m evolution` packaging of this revision is pending. Earlier 206-module image reports retain their exact tested revision.

The native configuration now resides in the kernel repository under arch/arm64/configs/vendor/xiaomi/{sm8250-common,alioth}.config. Option order matches the migrated Android fragments. The generic 7nm USB HS PHY is built in alongside generic DWC3/QMP, with its real QMP pipe-clock provider wired into GCC. The active LLCC DT now matches the selected Kona v2 module and the donor MMIO/allocation policy. Isolated compile and compiled-DT checks pass; final full-build and packaged-image validation remain pending.

The first broad source-ROM pass stopped in the display HAL at DRM CSC logging: native __s64 and Bionic int64_t use different underlying C types on ARM64. Casting only the logged value to int64_t preserves the UAPI layout and passes the exact failing Android compile. A public full-history display HAL fork is now pinned as the sixteenth source-profile repository; the full build has resumed with canonical kernel configs and the USB/LLCC fixes.

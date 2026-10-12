# Completed source-built Android 17 ROM

Development only; not production ready. The full ROM compiles and its packaged
artifacts pass validation. Android system boot and hardware functionality remain
unverified. No flashing was performed.

The full `. build/envsetup.sh && lunch lineage_alioth-cp2a-user && m evolution`
completed successfully on 2026-10-12. The final pass took 29 minutes and six
seconds, using previously built platform outputs.

ROM: `~/evo/out/target/product/alioth/EvolutionX-17.0-20261012-alioth-12.3-Unofficial.zip`.
Kernel: `5.15.206-g4c19a131a42f`, built from source using checkout Android Clang
r563880c / LLVM 21, integrated assembly and no LTO. The diagnostic kernel forces
permissive SELinux. Canonical configs are in the kernel repository at
`arch/arm64/configs/vendor/xiaomi/{sm8250-common,alioth}.config`.

The matched OTA-extracted images are under
`~/evo/kernel-research/alioth-5.15/rom-build-images/EvolutionX-17.0-20261012-alioth-12.3-Unofficial/`.
Use the matching ROM/vendor contents with the three boot images: kernel modules
are also installed in vendor, so the boot partitions alone do not replace them.
Android repacks ramdisks during target-files generation; the earlier raw-image
bundle remains separate at `rom-build-images/source-5.15.206-g4c19a131a42f-llvm21`.

## Validation

- Full ROM build and ZIP CRC passed. Exact ROM hash is in source-rom-build-validation.json.
- All ten extracted payload partition sizes and SHA256 hashes match the OTA manifest.
- AVB root and chained partitions verify against the configured development public keys.
- OTA boot Image/config and native DTB/overlay match the source outputs; overlay merge passes.
- All 207 modules pass CRC/dependency checks and match vendor and vendor ramdisk packaging.
- Independent vendor filesystem extraction confirms every module and metadata file,
  the post-mount init loader, toolbox binary and modprobe symlink target.
- The first-stage/recovery/charger lists retain 24 essential modules. All nine
  external driver groups compile and are packaged; no donor 4.19 module is reused.
- All 17 source-profile repositories are public with full histories and development
  descriptions; manifest pins are reachable from their published default branches.

Reports: android-source-build-validation.json, android-source-image-validation.json,
ota-source-image-validation.json, ota-payload-validation.json, ota-vendor-validation.json,
source-rom-build-validation.json and public-source-profile-audit.json.

## Compatibility fixes validated during this build

Native UAPI output declarations retain all 1,015 headers inside Soong sbox while
the checkout stays read-only. Normal ARM/ARM64 gralloc and encoder builds pass.
The legacy audio CONFIG_CACHE/SET/GET packet commands receive a narrow export
exception; unrelated configuration leaks remain rejected. Bitrate controls retain
generic V4L2 CQ=2 and scoped Qualcomm legacy CQ=5, with matching VIDC menu indices.
Display CSC logging uses the correct Bionic int64_t type without altering the ABI.

DSP firmware/loaders, Kona VIDC DT/resources, QCA6390/CNSS PCIe resources, USB
7nm HS PHY/pipe clock and Kona LLCC binding adaptations pass their recorded source,
compile and DT checks. External drivers build from source staging beneath KERNEL_OBJ.
Matching audio, graphics and display headers and legacy vendor exports are checked.

## Remaining runtime gates

Actual system boot, secure-world/FBE transactions, firmware/probe completion,
compositor initialization and peripheral operation require hardware evidence.
The connected recovery still runs 4.19; its non-root shell could not read pstore.
No new 5.15 boot test was performed. See ROM_COMPATIBILITY.md for known gaps,
including legacy RMNET/IPA, camera heap behavior and fast-charge interfaces.
Images and proprietary ROM binaries remain local; source and reports are published.
Earlier prebuilt-profile ROM validation is retained in FULL_ROM_BUILD.md.

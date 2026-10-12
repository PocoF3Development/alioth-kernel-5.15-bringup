# Module loading recheck — 2026-10-12

Development only; successful 5.15 recovery/system boot is still unverified.

Compared [SM8450 module wiring](https://github.com/Evolution-X-Devices/device_xiaomi_sm8450-common/blob/25d0e11d5bf4d38702bb59e3397705bfca07105f/BoardConfigCommon.mk#L105) and its second-stage/vendor_dlkm lists at that exact commit. SM8450 uses recovery-specific loading of first plus second-stage modules, source-built external modules, boot-header 4 fragments and a vendor_dlkm partition. Alioth uses boot-header 3, modules in vendor and vendor ramdisk, and nine external build groups drawn from separately pinned source repositories. A separate vendor_dlkm partition or monolithic module repository is not required for the existing alioth layout.

Found and fixed a mode-specific omission: recovery and charger reused the 24-name normal first-stage list, omitting dwc3-msm, legacy USB PHYs and PD PHY. Recovery does not run the normal vendor post-fs-data module service. It now has a dedicated 207-name list matching the complete ramdisk bundle; charger has a 31-name list including USB and power-off support. Normal first-stage remains 24 names; normal vendor init loads all 207 after firmware mounts.

Device functional revision: ccd5598; manifest update d1dfc97 pins that functional revision. Full histories remain public in PocoF3Development.

## Fresh checks

- `m vendorbootimage` through the source build wrapper and lineage_alioth-cp2a-user: PASS, 7m27s.
- Source ABI check: all 207 module vermagics and CRCs, dependency resolution, vendor/ramdisk equality and distinct mode lists: PASS.
- Packaged image check: actual kernel/config, DTB/DTBO merge, 207 ramdisk modules and metadata, AVB image verification: PASS.
- Recovery list covers every packaged module; charger/recovery names are unique and resolve to packaged modules. Missing modules remain fatal.
- Hardware load/probe evidence: NOT established. Correct packaging does not resolve the remaining early failure by itself.

## Additional recovery controls

A diagnostic 5.15 recovery using the working recovery userspace plus the matching 207-module bundle returned to fastboot with the native DTB. A native-DTB board-ID-44 control also returned to fastboot. With the working 4.19 DTB/DTBO, the user observed a persistent POCO logo and physically returned the device to fastboot; no USB transport appeared. This difference does not prove kernel execution. Retained pstore from the donor-DTB test was empty. The donor DTB is a diagnostic control, not a proposed production substitute.

A separate diagnostic kernel build now promotes USB/charger drivers to built-in and uses a distinct recovery release suffix/output directory. It is not mixed with the production 207-module bundle. No UART hardware is used.

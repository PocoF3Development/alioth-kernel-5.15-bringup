# Alioth Linux 5.15 bring-up

**DEVELOPMENT ONLY — NOT PRODUCTION READY.** No boot validation has been completed. No image has been flashed. Driver compilation does not establish hardware compatibility.

Public source repositories:

- [Kernel](https://github.com/PocoF3Development/android_kernel_xiaomi_sm8250-5.15)
- [Display](https://github.com/PocoF3Development/android_vendor_qcom_opensource_display-drivers-5.15)
- [Legacy audio](https://github.com/PocoF3Development/android_vendor_qcom_opensource_audio-kernel-legacy-5.15)

The source repositories preserve the full upstream ancestry of the pinned releases, followed by the original attributed port commits. Original commit IDs, parents, authors, dates and messages are retained. `publication-provenance.json` records source and published branch tips. The bring-up records repository retains its complete development history from its creation. Release manifests and all dependency pins are included. Toolchain binaries, ROM/vendor blobs, generated images and credentials are excluded.

See [PORT_STATUS.md](PORT_STATUS.md) for integration limitations. Result JSON files describe individual probes; successful probes are not a complete boot-image validation. The latest candidate Image, DTB, matching core modules and five vendor module groups build successfully. A separate 202-module bundle passes its dependency/CRC audit; board integration and boot validation remain incomplete. ThinLTO is enabled for faster builds.

> Latest implementation and validation: [PORT_STATUS.md](PORT_STATUS.md).

# Alioth 5.15 feasibility — 2026-10-11

Yes: this release is a credible Qualcomm Kona/SM8250 porting base. It is not a drop-in alioth kernel. Bootability and stock vendor compatibility remain unproven.

## Verified sources

- Vendor release: LA.VENDOR.15.4.8.r1-01600-QCS8250.QISI17.0. Its refs explicitly select kernel platform R38 for kona.
- Kernel platform: AU_LINUX_KERNEL.PLATFORM.2.0.R38.00.00.00.231.009.
- msm-kernel: 5bce8cbd7a740cdfe2203aa95fa3a66e2b8b7f53, Linux 5.15.206; complete upstream ancestry on alioth-bringup.
- Current alioth donor: a67e83add1fa9398814db8451f91347c7c2d09ed, Linux 4.19.325; clean when inspected.
- Both release manifests are saved unchanged under manifests/. All project pins are recorded in project-pins.json.

## Concrete gaps

The 5.15 tree includes build.config.msm.kona and Kona GKI/consolidate fragments, but no alioth-named device tree. Its build helper expects vendor/qcom downstream DTBs; that directory is absent in this checkout and no devicetree project is listed in the supplied manifests. Resolve its actual release source before claiming a complete source sync. Mainline-style qcom/sm8250 device trees are present but do not establish downstream driver compatibility.

The current alioth configuration selects MACH_XIAOMI_ALIOTH, FocalTech/Xiaomi touch features, AW8697 haptics, FPC/Goodix fingerprint, and Xiaomi camera support. Xiaomi-specific selections inspected are absent in the new tree. alioth-config-symbols-absent.txt inventories enabled selections with no matching declaration in the fetched tree; some may have been renamed or moved to external modules. This is a text inventory, not Kconfig resolution.

Qualcomm splits audio, camera, display, video, touch and WLAN components into separately pinned vendor repositories. A kernel-only checkout is insufficient. Existing 4.19 modules must be rebuilt/ported for 5.15, and unchanged userspace blobs require auditing their ioctls, memory allocation, firmware interfaces and device nodes. Camera, display/GPU, audio, modem connectivity and charging are major compatibility gates.

The donor Kona build config uses boot header 4, init_boot and vendor_dlkm/system_dlkm preparation. Current alioth BoardConfig chooses header 2 or 3, embeds DTB and packages separate DTBO. Preserve alioth bootloader/partition requirements while adapting kernel and module packaging; do not copy the QCS8250 packaging wholesale.

## Bring-up order

1. Resolve missing downstream Kona DT source and obtain pinned build tooling plus required external modules. Prove a complete reference dependency graph.
2. Translate alioth board wiring, reserved memory, regulators, storage and serial console into the 5.15 bindings. Establish an alioth config rather than copying 4.19 selections wholesale.
3. Port minimum storage, USB, PMIC and charging support; audit firmware/TrustZone interactions. Prepare a bootable image with the existing alioth layout.
4. Gate progress on serial/pstore evidence and first-stage mount, then display/touch, modem/WLAN, audio, sensors and camera. Keep thermal protection enabled.
5. Validate recovery, encryption, suspend, charging and daily hardware operation before ROM integration.

Initial source findings above are retained. See PORT_STATUS.md for subsequent builds and peripheral ports. Reference core and peripheral compile/link probes now pass, with BTF warnings recorded; no flash or production kernel replacement was performed. This is not a completed port. Release Android/SPL labels do not certify alioth compatibility or the security completeness of a future port.

## Reproducing the development configuration

Clone this repository into your workspace and clone the kernel repository's `alioth-5.15` branch into `msm-kernel`. Supply the release Clang r450784e toolchain under `toolchain/clang-r450784e`. Run `python3 configure-alioth.py` before `python3 compile-alioth.py`. Configuration resolution can drop symbols whose dependencies are unmet; inspect the resolved `.config`. The current native DT is provisional.

`sync-kernel-deps.py` fetches original release-pinned dependencies and refuses to overwrite different existing revisions. The modified display and legacy audio repositories above must be used separately; the sync script does not automatically substitute their published branches. Full matching core and vendor-module builds remain required.

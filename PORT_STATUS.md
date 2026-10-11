# Alioth Linux 5.15 development status

**DEVELOPMENT ONLY — NOT PRODUCTION READY.** No boot validation or flashing has been performed. No boot-test image is ready.

## Current source and validation

Kernel: `3441c6114e2d6e6d501e22b536453e3745af6bf0`; Linux 5.15.206 with ThinLTO, CFI and BTF. Original complete upstream history and attributed donor imports are preserved. Production 4.19 source and ROM outputs are unchanged.

The candidate Image, native alioth DTB and matching core modules build successfully. External-display, KGSL graphics, SecureMSM, display and legacy Kona audio modules all pass compilation, LTO, modpost, linking and BTF against that same candidate. Display consumes actual SecureMSM HDCP and external-display exports. CS35L41 is now selected for alioth and included in the full codec build rather than being left as an old standalone probe artifact.

All 40 produced vendor modules have the matching kernel version. A separate local staging bundle contains 162 core plus 40 vendor modules. Its depmod symbol/CRC audit passes with no warnings. Build success and dependency closure do not validate board wiring, firmware or vendor userspace at runtime.

The Image retains the same 15 nonfatal resolve_btfids warnings as the initial reference; see alioth-btf-warning-comparison.json. No CFI, BTF or modpost checks were suppressed.

## Device adaptations

Native alioth DT includes touch/fingerprint/NFC/haptics, IR, static firmware reservations, RPMh ARC votes, UFS PHY translation and native PMIC physical keys. Power and volume-down use PM8150 PON inputs; volume-up uses PM8150 GPIO6, active low, with donor debounce and supply selection. The physical-key drivers are built in.

The modern ION bridge supports registered nonsecure heaps 25 (system), 22 (ADSP), 26 (contiguous), 27 (QSEE communication) and 19 (TA). Donor-sized reusable CMA pools are retained, with the original 4 MiB alignment and below-4-GiB constraints. The new QSEE pools are 20 MiB and 16 MiB. Mixed masks, unsupported heaps and protected flags still fail explicitly. Secure-world sharing and protected heaps require separate integration.

Compiled DT checks verify key codes/debounce, QSEE pool sizes and heap backend names/types. These are source/build checks, not hardware tests. Optional KTZ8866 drivers compile; PS5169 remains disabled with its private power-supply ABI unresolved and no alioth donor node identified.

## Remaining boot gates

- Translate KGSL GPU/GMU/IOMMU/interconnect DT and reconcile regulator-controlled CX/GX domains with native GPUCC genpd ownership.
- Integrate display/panel nodes and Xiaomi panel/FOD behavior.
- Port charging, gauge, authentication and charge-pump behavior against native power-supply/IIO APIs while retaining protection logic.
- Integrate camera, protected heaps, DSP/firmware, WLAN/Bluetooth and board audio routing.
- Package matching boot, vendor_boot and DTBO for alioth's header-3 layout and selectors, then obtain hardware boot evidence. No flashing is authorized yet.

See integration-checkpoint.json, device-adaptation-record.json, device-dtb-validation.json, alioth-build-results.json, alioth-matching-core-modules-results.json, alioth-vendor-module-results.json and alioth-module-bundle-results.json for the scoped evidence. Previous feasibility and probe history remains in BUILD_NOTES.md and subsystem records.


## GPU, display PLL and charging checkpoint

Native KGSL/GMU resources and speed-bin power levels are translated. The graphics mapping fix and full upstream history are public. The K11A panel commands and supply sequencing are retained. The separately imported donor 7 nm v4.1 PLL module and complete external display module pass compile/modpost/link/BTF. Native display DT and DISPCC object compile. PM8150B charger/gauge IRQs, conservative battery profile and IIO channels are integrated; charging stays disabled pending complete board checks. FG IIO CC_SOC now uses its measured value rather than a pointer. A fresh full matching build, module dependency audit and image packaging are outstanding. No flashing or runtime validation occurred.

# Firmware overlay recheck

The native root-only overlay lacked `__fixups__`, and its packaged base lacked `__symbols__`. Current Android UFDT and a March 2024 Android UFDT revision accept that pair. Qualcomm ABL’s older implementation instead requires both nodes unconditionally. A host build of its single-overlay implementation reproduced rejection of the original pair and accepted the corrected pair; the working donor pair passed. The host list declaration shim only permits compiling the unused multi-overlay entry point; it does not alter the tested overlay algorithm.

Reference: https://github.com/SHIFTPHONES/android_bootable_bootloader_edk2/tree/7d391d8b1059ed48259728cab004ca6f16ee3de2/EmbeddedPkg/Library/LibUfdt

An on-device control retained `Apply Overlay total time: 43 ms`, `Update Device Tree total time: 19 ms`, and `Shutting Down UEFI Boot Services`. The earlier `Dtb overlay failed` message disappeared from that attempt. The user reported a black screen. Linux execution and recovery ADB remain unverified. That control used fastboot boot, which firmware selected as mission mode; the next logging test explicitly reboots into recovery.

The device source now includes compatibility nodes and checks their presence. This metadata correction does not complete the Alioth device-tree port.

Historical minidump records contain 4.19 Immensity and stock versions, with no 5.15 Linux version string found. The Immensity source is https://github.com/UtsavBalar1231/kernel_xiaomi_sm8250, locally available at ~/immensity. These are not crash logs from current 5.15 tests. Raw dumps remain private.

# Firmware overlay recheck

Two retained UEFI records report `ApplyOverlay: ufdt apply overlay failed`, followed by `Error: Dtb overlay failed` and entry into fastboot. This establishes a pre-Linux packaging or overlay blocker for those attempts; it does not explain every earlier logo hang.

A host tool compiled from the current Android checkout’s system/libufdt and external/dtc accepts both the native base/overlay pair and the working donor pair. Host acceptance is therefore insufficient to establish compatibility with this device’s firmware. Next checks must compare firmware-era UFDT behavior and the actual packaged DT selection. No speculative source fix has been promoted.

The retained minidump contains historical 4.19 Immensity and stock records, with no 5.15 Linux version string found. The user identified the Immensity source as https://github.com/UtsavBalar1231/kernel_xiaomi_sm8250. These records must not be attributed to current 5.15 tests.

Raw firmware dumps remain private. The phone was restored to the working 4.19 globally permissive recovery with root ADB. A bootable 5.15 recovery or system has not been demonstrated.

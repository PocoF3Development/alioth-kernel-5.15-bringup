# Alioth Linux 5.15 development archive

**Archived 2026-10-12. Development only; not production ready. Linux 5.15 has not successfully booted recovery or Android on alioth.**

The Android 17 Evolution X no-LTO ROM built and installed through recovery, but system boot failed. No useful 5.15 Linux crash console was recovered. A separate ThinLTO core/module build passed its 207-module dependency/CRC audit; it was not a rebuilt or installed replacement ROM. Build success, successful installation and firmware ExitBootServices do not prove Linux or Android boot.

All remaining source work is preserved in PocoF3Development with full upstream and attributed donor ancestry. Each source repository ends with a final status commit describing completed work, missing or unvalidated support, and required next steps. Existing published commits were retained. Only two previously unpublished kernel commits had their assistance trailers corrected; the source trees match the tested ThinLTO checkpoint.

Regular alioth source builds now default to maintained 4.19. The experimental source profile requires `TARGET_USE_ALIOTH_KERNEL_515=true` and selects ThinLTO. The installed no-LTO OTA remains a separate historical test. The fully pinned handoff manifest is [manifest.xml](android-device-integration/kernel-5.15/manifest.xml).

Completed work includes native alioth/SM8250 DT translation, Xiaomi peripheral imports, GPU/display/PLL integration, PMIC charging/fuel-gauge ports, legacy ION/shared/secure heaps and vendor encryption interfaces, source-built driver modules, native UAPI integration and matching image/module packaging. These are implementations and build checkpoints, not validated hardware support.

The next required work is to establish the first failing Linux boot stage without UART, complete donor board DT/binding coverage, and then validate storage/mounting, USB/ADB, secure firmware and encryption, charging, graphics, audio, camera, connectivity and suspend. Sparse and DT-schema findings remain unresolved. Permissive development settings require production hardening only after functional bring-up.

See [FINAL_CHANGELOG.md](FINAL_CHANGELOG.md) for the complete handoff and per-repository status. [publication-provenance.json](publication-provenance.json) records final source pins and the unpublished commit metadata mapping. Other reports are historical checkpoints and may contain superseded current-status statements. Raw device logs, private ramdisks, firmware, generated images, credentials and host keys are excluded.

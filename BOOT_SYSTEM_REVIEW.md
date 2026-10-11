# Boot-system review

**DEVELOPMENT ONLY — NOT PRODUCTION READY.** No device was flashed or booted. Host tests and image construction cannot certify an Android boot.

The review uses the current ~/evo ROM boot/vendor_boot ramdisks, actual vendor library strings, compiled device tree, embedded kernel configuration and matching module set.

| Area | Evidence / result | Remaining dependency |
| --- | --- | --- |
| Image layout | Header-v3 boot and vendor_boot; independently unpacked and compared; DTBO merged; partition bounds checked | Actual bootloader acceptance and RAM fixups |
| First-stage storage | UFS, device mapper, filesystems and encryption built in; current ramdisk init supports release-specific modules | Hardware UFS initialization and mounting installed partitions |
| Vendor paths | Alioth soc bus restored to /soc; UFS platform path and hardcoded libspcom SPSS path checked | Other vendor consumers may have additional paths |
| SPSS notifications | QSEE IPC IRQ bridge enabled, DT bank 1 bit 0 routed, module included; cleanup defects fixed | Firmware interrupt and restart behavior |
| SPSS CMAC | Legacy PBL text and three-app binary attributes restored only for Kona; actual functions tested with patterned MMIO | Secure processor firmware and key-service operation |
| Firmware delivery | Donor FW_LOADER_USER_HELPER_FALLBACK restored for vendor ueventd firmware directories | Modem partition mount, firmware availability and successful firmware authentication |
| Modules | All staged modules share kernel release; depmod symbols/CRCs and packaged load lists checked | Actual probing, dependencies and device permissions |
| Encryption / heaps | Heap 13/14/20 and key-program/derive host checks pass | Real SCM calls, existing userdata keys and vendor allocation requests |
| AVB | Local ROM vbmeta flags are 3; descriptors still describe original ROM images | Installed vbmeta and bootloader unlock state are unknown; unsigned replacements are not certified |
| Display / GPU / charging | Drivers compile and translated resources are checked | PLL/panel/GMU operation and measured charging behavior |
| Other vendor services | Donor and native contracts reviewed where relevant | Audio, modem, connectivity, camera and remaining ioctl/sysfs contracts are unverified |

Known limitations remain: heap 20 does not reproduce the donor camera reserve/refill or task-name routing; unsupported allocation markers remain rejected. Charging authentication and charge-pump support remain unported; charging uses the previously documented conservative configuration. FBE_CLEAR_KEY returns ENODEV as in the donor without PFK. The libspcom pbl_ce path is absent in both the donor and port; no guessed attribute is supplied. rmt_storage has UIO expectations, but no matching Kona donor DT resource was found; other-SoC memory regions were not transplanted.

The next decisive evidence is a deliberately authorized device boot with early kernel logs, first-stage mount/module results, secure-service results and userdata mount status. The current request does not authorize flashing, so that evidence is unavailable.

# Alioth ROM compatibility with 5.15

Development only; Android boot has not been established. Default selection does not certify runtime compatibility.

## Build and module integration

Alioth now defaults to the 5.15 prebuilt profile. Explicit TARGET_USE_ALIOTH_KERNEL_515=false selects the donor. VAB/vendor_boot remains required, official Lineage prebuilt restrictions remain intact, and Android assembles fresh ramdisks rather than copying an old boot image. Normal boot now requests all 206 matching modules through the dependency-aware Android loader. Recovery and charger retain the 24-module first-stage set. No 4.19 .ko is reused.

The bounded Makefile checks pass for default 5.15 and explicit 4.19; non-VAB is rejected. No full Android build was performed.

## Confirmed source adaptations

The common post-boot script selects the live /proc/sys/walt tree and walt governor on native WALT, while preserving donor kernel/schedutil paths on 4.19. Native input boost receives eight integer CPU frequencies rather than the old cpu:frequency syntax. Migration settings retain the donor two-level values. Native WALT source provides the migration/group/rotation/boost controls and governor attributes used here. Shell syntax passes; device application and SELinux permissions remain unverified.

## Vendor ABI coverage and open gates

| Contract | Source/build evidence | Remaining gate |
| --- | --- | --- |
| 32-bit vendor execution | CONFIG_COMPAT, compat VDSO and emulation enabled | Actual proprietary ioctl and syscall traces |
| Binder/ashmem | Binder IPC/binderfs and ashmem enabled | Device services and binder transaction tests |
| ION and heaps 13/14/20 | Existing allocator/UAPI/secure CMA validations | Camera reserve/refill/POOL_FORCE_ALLOC and real allocations |
| QSEE/SMC/SPSS | Native drivers, IRQ bridge, SPSS legacy sysfs and CMAC adaptations | Firmware transactions and secure world compatibility |
| FBE/ICE | fscrypt/inline encryption/dm-default-key and wrapped key bridge | Unlock installed userdata without modifying it |
| GPU/display | Native KGSL/display modules and translated alioth DT | Probe, panel initialization, EGL and compositor boot |
| Camera | Native camera modules compile | Xiaomi vendor UAPI/DT gaps; not certified |
| WLAN | Matching native modules compile | PCI/CNSS DT and firmware boot |
| Remote storage | Vendor binaries contain /dev/uio references | Exact Kona UIO/reserved-memory contract; no guessed mapping |
| Modem/data | Core stack present | RMNET PERF/SHS donor gaps and modem runtime |
| Charging | Native buck/FG, BQ2597x and DS28E16 import | PD/HVDCP/fast-charge manager and physical safety checks |
| Scheduling | Post-boot WALT paths adapted; Android task profiles use uclamp | Legacy init stune/CFQ writes, vendor perf path/ioctl coverage and policy labels |

legacy-vendor-path-inventory.json records 903 unique literal paths from 1598 source/config/binary files including 772 ELF binaries. It deliberately retains false positives and optional hardware paths. Literal presence cannot establish ioctl compatibility, discover computed paths, or prove sysfs availability. Do not create fake success nodes or weaken error handling to conceal unsupported contracts.

rom-linked-repositories.json records local source heads and shallow/dirty state. Generated external build artifacts remain untouched. Unused release projects can be shallow; active published kernel/driver ancestry is complete. published-repositories-review.json records public visibility and live branch heads, rather than relying on the older publication-provenance snapshot.

Hardware logs from the next permitted recovery/system test are required to close the boot gates. No flashing was performed in this ROM integration pass.

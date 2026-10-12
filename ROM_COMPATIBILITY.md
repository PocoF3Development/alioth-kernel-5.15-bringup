# Alioth ROM compatibility with 5.15

Development only; Android boot has not been established. Default selection does not certify runtime compatibility.

## Build and module integration

Alioth now defaults to source-built 5.15 using Android Clang r563880c and no LTO. The core, nine external module groups and matching DT images are built through the Android kernel task. Explicit TARGET_USE_ALIOTH_KERNEL_515=false selects the donor. VAB/vendor_boot remains required, official Lineage prebuilt restrictions remain intact, and Android assembles fresh ramdisks rather than copying an old boot image. First-stage init requests the 24 essential matching modules in all modes. Normal boot requests all 207 matching modules from /vendor/lib/modules through toolbox_vendor after firmware mounts, using exec_start in post-fs-data and the existing vendor_modprobe SELinux domain. Recovery and charger retain the first-stage set. Loading every driver in first stage risks firmware stalls and a fatal init load failure. No 4.19 .ko is reused.

Profile checks pass for default 5.15 and explicit 4.19; invalid selections, missing sources and non-VAB layouts are rejected. The earlier prebuilt-profile ROM build passed (FULL_ROM_BUILD.md). The current source build has a separate status in SOURCE_ROM_BUILD.md. Device boot remains unverified.

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
| Hardware video codec | Kona VIDC driver passes isolated native LLVM21 compile; translated DT, firmware/PAS reservation, clock ownership and legacy buffer flags checked | Full Android 207-module packaging and actual codec firmware/session tests |
| WLAN | Native modules compile; QCA6390/CNSS/PCIe0 DT now matches donor resources/PHY sequence and native ICC/PMIC contracts | Firmware, PCIe enumeration and network traffic on hardware |
| Remote storage | Vendor binaries contain /dev/uio references | Exact Kona UIO/reserved-memory contract; no guessed mapping |
| Modem/data | Core stack present | RMNET PERF/SHS donor gaps and modem runtime |
| Charging | Native buck/FG, BQ2597x and DS28E16 import | PD/HVDCP/fast-charge manager and physical safety checks |
| Scheduling | Post-boot WALT paths adapted; Android task profiles use uclamp | Legacy init stune/CFQ writes, vendor perf path/ioctl coverage and policy labels |

legacy-vendor-path-inventory.json records 903 unique literal paths from 1598 source/config/binary files including 772 ELF binaries. It deliberately retains false positives and optional hardware paths. Literal presence cannot establish ioctl compatibility, discover computed paths, or prove sysfs availability. Do not create fake success nodes or weaken error handling to conceal unsupported contracts.

rom-linked-repositories.json records local source heads and shallow/dirty state. Generated external build artifacts remain untouched. Unused release projects can be shallow; active published kernel/driver ancestry is complete. published-repositories-review.json records public visibility and live branch heads, rather than relying on the older publication-provenance snapshot.

Hardware logs from the next permitted recovery/system test are required to close the boot gates. No flashing was performed in this ROM integration pass.

## Module loading recheck

validate-android-module-loading.py checks the actual exported module hashes/vermagic, regenerates depmod metadata for the flattened Android layout, validates CRCs against the combined symbol map and walks every hard dependency. The earlier matching prebuilt set of 206 modules passed. The source-built set must independently pass validate-source-build.py before being reported as validated. Android generates modules.dep, modules.alias, modules.softdep and per-mode load lists. Module signatures are not forced and modules are uncompressed. First-stage loading precedes firmware mounts; later loading uses --all=FILE syntax required by toolbox getopt. Module build-in conversion is not required by these checks. Hardware firmware/probe completion, load-service exit status and enforcing-policy access remain unverified.

The native-source build exports the legacy `linux/rmnet_data.h` contract for the library built with `USE_OLD_RMNET_DATA`. The ARM64 librmnetctl source compiles against the revised header. The old protocol-31 RMNET netlink endpoint is absent from the current native driver; those legacy APIs are not established runtime-compatible by this header export. Current RMNET rtnetlink and IPA checks remain separate.

Native UFS boot control uses the existing BSG implementation with `CONFIG_SCSI_UFS_BSG=y`, rather than exporting an unsupported vendor query ioctl. The 5.15 BoardConfig forces `QTI_GPT_UTILS.USE_BSG_FRAMEWORK=true` after product inheritance; the generated Soong value is verified. The utility discovers `/dev/bsg/ufs-bsg0` and `/dev/bsg/ufs-bsg`, retaining legacy root-device discovery. Device ueventd ownership and the existing vendor_bsg_device SELinux type cover the native node. Recovery utility compilation passes; hardware slot switching remains untested. The bootctrl source fork is pinned in the manifest with a path replacement for the original project.

ADSP/CDSP/SLPI native PAS nodes are enabled with donor firmware names/reservations, and ADSP/CDSP loader phandles now resolve correctly. VIDC is the ninth external group (207 total modules). The 206-module packaged-image record remains historical until the ongoing full build is independently revalidated; no firmware or radio boot is claimed from DT compilation.

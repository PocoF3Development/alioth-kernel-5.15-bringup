# Module partition and dependency recheck

This alioth product has system, system_ext, product, vendor and odm logical partitions. Neither system_dlkm nor vendor_dlkm is declared or mounted by its current board/fstab layout. Its custom source-built 5.15 kernel installs all 207 loadable native/external modules under vendor/lib/modules, with matching copies in vendor_boot’s ramdisk lib/modules. No kernel modules were found in the other staged partition trees, including stale 4.19 modules.

The normal first-stage load list has 24 modules; recovery selects all 207 and charger selects its 31-module subset. Hard dependencies are supplied in the same ramdisk and loaded through modules.dep. Native UFS, SM8250 pinctrl, SM8250 interconnect, generic DWC3/QCOM glue and USB/UFS PHY support are built in. Loading an unrelated Kona module does not replace those native built-ins. No DLKM partition migration is required simply to distribute this custom kernel’s module set.

The audit found one obsolete video softdep on subsys-pil-tz. The adapted firmware path uses request_firmware, qcom_mdt_load and SCM PAS authentication, so that nonexistent legacy dependency was removed from the module source. Existing softdeps on built-in smem, arm_smmu and socinfo are valid; the loader tolerates built-ins without loading another object.

The shared source-kernel packaging helper previously passed only .ko files to depmod and omitted modules.builtin, modules.builtin.modinfo and modules.order. It now supplies the matching built-in metadata and flattened order during depmod and installs built-in metadata alongside the module indexes. The fresh full ROM must be regenerated with this rule before flashing.

The source validator now recursively audits every relevant staged partition tree, exact release/vermagic, module placement, dependency prefixes and complete hard/soft dependency closure, matching built-in metadata, and core/external symbol CRCs. Runtime loading still needs a booted 5.15 kernel; this static audit does not establish probe success or system boot.

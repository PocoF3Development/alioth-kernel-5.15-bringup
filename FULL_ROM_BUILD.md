# Evolution X Android 17 with alioth 5.15

Full build completed successfully with `. build/envsetup.sh && lunch lineage_alioth-cp2a-user && m evolution`. The selected profile consumes the matching no-LTO 5.15.206-g689b59f88c4d Image and modules from the research build. It does not compile the external kernel projects through Android's legacy kernel target. The kernel remains forced permissive for diagnostics. This is not production ready and no device was flashed.

Two integration fixes were required: exclude kernel-research from Soong's module search, and keep the no-op Android.mk at the research root to stop Make's recursive module scan. They prevent duplicate definitions from pinned copies of Clang and device-tree tools.

Output ZIP: `~/evo/out/target/product/alioth/EvolutionX-17.0-20261011-alioth-12.3-Unofficial.zip`.

The matching OTA-extracted boot, vendor_boot and dtbo images and their hashes are under `~/evo/kernel-research/alioth-5.15/rom-build-images/EvolutionX-17.0-20261011-alioth-12.3-Unofficial/`. Prefer this matched set when referring to the OTA. Android target-files repacks ramdisks, so raw out-directory image hashes need not match the payload image hashes. The kernel and DTB match, vendor ramdisk contents match, and the four omitted initial /dev nodes are hidden by first-stage init's tmpfs mount.

Validated: ZIP CRC, extraction of boot/vendor_boot/dtbo from the final OTA against recorded target-files SHA256 values, target-files AVB chain verification, boot Image/base DTB/overlay against the exported native artifacts, and independent vendor.img extraction of all 206 matching modules, toolbox and loader. Actual Android modules.dep/alias/softdep exist and dependency paths resolve. Normal first stage requests 24 modules and their dependencies; the post-mount vendor loader requests all 206.

The compiler/package result does not prove Android boot, firmware transactions, decryption or vendor ABI compatibility. Those hardware gates in ROM_COMPATIBILITY.md remain open. Proprietary ROM binaries and images are kept local; only source integration and validation records are published.

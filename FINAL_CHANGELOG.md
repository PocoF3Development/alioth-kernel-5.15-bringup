# Final changelog — project archived 2026-10-12

Development only; not production ready. Work stopped at the user's request. No kernel or Android build jobs were running at the shutdown check. No further builds, flashes, wipes, or device tests are planned.

## Outcome

Linux 5.15 has NOT successfully booted recovery or Android on alioth. A complete Android 17 Evolution X source build and OTA installation succeeded, but the resulting system did not boot. No useful 5.15 Linux crash console was recovered. Compilation, ABI checks and successful installation do not establish bootability.

## Implemented development work

- Established a Qualcomm Linux 5.15.206 release-based tree and published attributed donor ports with full upstream ancestry in PocoF3Development.
- Added alioth/SM8250 DT translations for storage, USB, regulators, GPU/GMU, display/DSI/PLL, PMIC charging and fuel gauge, reserved memory, TrustZone and SPSS. This remains an incomplete board port, not full parity with the working donor DTS.
- Imported/adapted Xiaomi peripheral drivers and configuration fragments; integrated core and nine external driver groups into the Android source build using checkout Android Clang r563880c.
- Added legacy ION and secure/shared heap compatibility, including heaps 13/14/20, and vendor encryption interface adaptations. Runtime firmware, ownership, encryption and peripheral behavior remain unvalidated.
- Added matching source-built module packaging, load lists, built-in metadata, dependency and symbol CRC checks, and source/image validators. This product places modules in vendor and the vendor ramdisk; it does not define separate system_dlkm/vendor_dlkm partitions.
- Made system and recovery permissive for development; created private root-ADB diagnostic recovery controls. These settings are unsuitable for production.
- Corrected Qualcomm bootloader UFDT compatibility: packaged base DTB includes /__symbols__, and overlay includes /__fixups__. Retained firmware logs then confirmed overlay application and UEFI ExitBootServices.
- Added opt-in early trace and Immensity-inspired legacy ramoops diagnostic support in a separate experimental branch. Recovery-to-recovery retention worked; physical resets could clear retained evidence.
- Added missing ARM64 vDSO function prototypes for W=1 validation. The related validated 4.19 fix was published separately.

## Completed validation

- Full m evolution build completed, including the module metadata corrections.
- Installed EvolutionX-17.0-20261012-alioth-12.3-Unofficial.zip through normal recovery ADB sideload; the user wiped data afterward. Installation succeeded, system boot failed.
- Read back slot B boot/vendor_boot/dtbo: all three matched the OTA payload manifest hashes. Kernel/DTB and vendor ramdisk module contents matched the validated no-LTO build. OTA repacking means standalone product-image hashes are not the authoritative installed-image comparison.
- Audited 207 modules, early/recovery/charger lists, staged partition contents, dependency closure, built-in metadata and module CRCs. Actual vendor filesystem contents matched staging.
- Separate ThinLTO kernel plus external-driver build succeeded at local kernel revision 920909676d2e8838e95595c4f646cb24a04ec2e9. Its audit found 207 uniquely named modules and 18,580 unique exported symbol providers, with no missing providers, duplicate providers or CRC mismatches. Embedded Image configuration and exported headers were checked. This ThinLTO candidate was not installed as a replacement OTA.
- Native Sparse checked 3,154 units but reported 6,899 warnings and 369 error lines despite returning zero. It is NOT a clean static-analysis pass. DT schema checks also reported findings; missing BSP bindings and reference-schema mismatches limit interpretation.
- Installed Sparse, cppcheck, Smatch and DT schema tooling. Remaining Smatch/clang-tidy/cppcheck analysis was not completed before archiving.

## Device state at stop

Slot A was restored to the matching working 4.19 diagnostic boot/DTBO and permissive root-ADB vendor_boot. ADB lists recovery. Slot B retains the freshly installed no-LTO 5.15 OTA. No claim is made that rebooting to system will work. The final corrected 48-bit/four-level recovery control also exposed no USB; its retained logs were not collected before work was stopped.

## Remaining gates

- Establish reliable evidence of 5.15 Linux entry and the first failing boot stage without UART. Firmware ExitBootServices alone is insufficient.
- Complete the donor board DT translation. Native DTB size is about 154 KB versus about 844 KB for the working donor live DTB; size alone is not a correctness test, but coverage remains incomplete.
- Resolve the early boot failure before claiming module probe, storage/mount, ADB, display, TrustZone, secure heaps or Android vendor compatibility.
- Validate charging safety, encryption/keymaster, modem/WLAN, audio, cameras, sensors, suspend and all other hardware at runtime.
- Triage static/schema findings and reconcile local ThinLTO configuration edits with manifest pins before reproducing a new ROM.

## Preserved local checkpoints

Workspace: ~/evo/kernel-research/alioth-5.15.

| Component | Final local HEAD |
| --- | --- |
| Core kernel | 920909676d2e8838e95595c4f646cb24a04ec2e9 |
| Experimental early trace | 8723519222bee070ddeb27d154728b3ae07e4c4f |
| Alioth device tree | a36372a3b11bdf52bdc5e04fd59b1b1623b627d6 |
| SM8250 common device tree | cf633a738f95c2c53de62537e3937356252c944e |
| Android vendor lineage | b8e9fe4fbca3d9c2143c506140e39d1529205d37 |
| Video driver | 39850774e3469d331a18a92077eca1a107e9f49c |
| Working 4.19 source | 9662d0a0db1b11aa2e734659d494c2f9f64a6f2e |

The final core-kernel prototype/ThinLTO commits (4037222451c2 and 920909676d2e) remain local; do not infer publication from this table. Alioth has uncommitted ThinLTO changes in kernel-5.15/BoardConfig.mk, validate-source-build.py and validate-source-images.py. They were deliberately preserved, not committed as a completed integration. The installed OTA was built from 2ca0323da599fea5b9b4ea20331d81418f913a6e with no LTO; current manifest pins still describe that profile.

Frozen installed-build inputs and reports: rom-build-images/2026-10-12-ufdt-module-complete-nolto/.
Device readbacks and installation evidence: device-test/2026-10-12-system-boot/full-ota-sideload-test/.
ThinLTO outputs: out/thinlto-validation/; reports thinlto-final-build-result.json and thinlto-abi-validation.json.
Raw device logs, private ramdisks, generated images, credentials and host keys remain local and are excluded from publication.

Older reports in this repository record historical checkpoints; this document supersedes their current-status and unflashed statements.

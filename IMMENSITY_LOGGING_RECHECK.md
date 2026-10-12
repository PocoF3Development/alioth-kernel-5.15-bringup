# Immensity logging adaptation

Donor revision: 99352d52fed2 (local ~/immensity). Its 2a1e5e7dadb21dd0b16d5fe1783522fd6ddf7edb reserves 4 MiB at 0xb0000000 and splits it equally between console and pmsg. Its Xiaomi config selects a 2 MiB printk buffer.

Diagnostic branch alioth-earlytrace now adapts the reservation behind CONFIG_PSTORE_RAM_ALIOTH_LEGACY, default off. It accepts only ramoops_memreserve=4M, uses the existing 5.15 platform-data backend, and gives an enabled native ramoops DT node precedence to avoid duplicate registration. The built-in recovery profile enables it and increases CONFIG_LOG_BUF_SHIFT from 17 to 21. Production kernel configuration remains unchanged pending runtime validation. The candidate uses the corrected UFDT metadata and explicitly requests recovery mode.

Fresh full Image build and affected ram.o build passed with Android LLVM 21 and no LTO. Embedded Image config matches the object config; there are zero loadable modules. Strict code checkpatch and git diff --check passed. W=1 is blocked during prerequisite VDSO compilation by the same three unchanged missing-prototype errors previously recorded, before checking the changed pstore object; this is not reported as a passing W=1 check.

The donor’s proc last_kmsg interface points to an already saved pstore console buffer. It does not create earlier capture, and copying its unowned buffer pointer would require lifetime fixes in 5.15. Recovery already reads the saved console directly from pstore, so that alias has not been imported. Cold resets have cleared the reserved console during tests; absence after such resets cannot prove Linux did not start.

Native DT logging layout already matches the donor. The legacy reservation fallback matters when testing a donor DT without a ramoops node. This work provides logging infrastructure, not proof of a bootable kernel.

The explicit recovery-mode test of 8723519222be also reached UEFI exit after successful overlay application (42 ms). No ADB appeared. Following the physical reset and 4.19 recovery restore, the complete minidump hash was identical to the prior historical dump and the saved console was empty. The production alioth fragment now selects LOG_BUF_SHIFT=21 as well; the legacy reservation fallback remains experimental and default off.

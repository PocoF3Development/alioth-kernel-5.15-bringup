# Final 4.19 changelog — 2026-10-12

Source: ~/evo/kernel/xiaomi/sm8250, branch aosp-17.
Published repository: https://github.com/PocoF3Releases/kernel_xiaomi_sm8250.

## Published change

9662d0a0db1b11aa2e734659d494c2f9f64a6f2e adds declarations for the exported ARM64 vDSO functions, including __kernel_time, in the existing vDSO header. An affected-object W=1 build changed from four missing-prototype errors to zero. The executable .text was byte-identical before/after. This is build-validation hygiene, not a claimed device boot fix. The diagnostic recovery still runs the earlier working runtime kernel.

## Findings preserved for later work — not implemented

- Both 4.19 and 5.15 qpnp-fg-gen4 compare the esr_timer_chg_fast array pointer against zero when calculating fast calibration time. The intended check appears to be its TIMER_MAX element, which defaults to -EINVAL if the DT timer is absent. Proposed correction: validate esr_timer_chg_fast[TIMER_MAX] > 0 before replacing the safe fallback interval. Culprit in 4.19: 53f2a2062b697897686cdb99d4a0ebdef895f7d8; in 5.15: 54d7259445f746ab1eb02b08cae4338735bd2441. No patch or charging runtime validation was completed.
- Both trees' drivers/input/keyboard/nanosic_driver/nano_macro.h begin with a UTF-8 BOM, which caused Sparse parsing failures. Removing the BOM was proposed but not performed.
- Other Sparse warnings, including QRTR pointer annotations and Slimbus address-space handling, were not established as functional defects and were not changed.

No 5.15-only compatibility patches were blindly imported into the working 4.19 tree. Further changes/builds stopped at the user's archive request.

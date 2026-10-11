# Initial alioth DT translation

Uses native sm8250.dtsi and PMIC bindings; does not copy old clock IDs.
Board ID 44 and SoC IDs 356/0x10000, 0x20000, 0x20001 come from the pinned donor overlay/base variants. UART12 and UFS controller/PHY use native addresses. Regulator topology and UFS voltage/current limits currently derive from native SM8250 MTP and require board-specific validation against the donor before runtime testing. USB1 is peripheral, USB2 stays disabled.

This DT is a compile probe, not an accepted boot DT. Missing: donor reserved-memory/firmware handoff reconciliation, PMIC IDs/selection metadata, panel, touchscreen, charger/gauge translation, downstream KGSL, remote processors, audio and camera nodes. Donor UFS vccq_set_npm and hsg4_synclength have no matching native driver properties and are not copied silently. No image should be considered bootable based solely on this DT compiling.

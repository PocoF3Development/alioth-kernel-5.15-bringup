# Alioth DTS coverage recheck — 2026-10-12

The current native DTS port is incomplete. DTB size is not a completeness test.

The working vendor_boot DTB image is 1,425,049 bytes, containing three base FDTs (477,325, 477,321 and 470,403 bytes), plus a separate 458,672-byte alioth overlay. The native image is one 154,385-byte FDT. Working recovery reports DTB index 0 and DTBO index 0.

Collected the actual live working recovery tree privately over USB. It has 4,072 nodes versus 980 in the packaged native merged tree; the source include graphs contain 136 versus 49 files. These counts include pinctrl, parameter and non-driver nodes and do not prove that every missing donor node belongs to this device.

The initial compatibility-name comparison flags 565 enabled donor nodes across 244 compatibility groups. These are review candidates, not 565 proven missing devices: native regulators, clocks, GPIO, power-on, charging, USB, CPUs and firmware use changed bindings. The accompanying driver-string inventory helps distinguish translation candidates from missing drivers, but matching text is not a binding or probe validation.

Full legacy audio routing, camera resource/context-bank topology, Bluetooth power/UART contracts, IPA/RMNET interfaces and some vendor power/performance paths remain open. Preserve donor provenance and standalone changes where useful; translate clock IDs, interrupt domains, IOMMU streams, bus providers and firmware contracts for the selected 5.15 drivers rather than copying flattened phandles.

A 5.15 recovery candidate with USB support built in and 149 matching native modules failed before ADB. A separate VA48/four-level build with otherwise identical diagnostic settings also returned to fastboot; VA48 is not established as a fix. Working 4.19 warm recovery reboot retained a 146,605-byte console record, verifying pstore access and retention on that baseline. The isolated alioth-earlytrace kernel branch adds disabled-by-default pre-MMU ramoops breadcrumbs to locate silent early failures without UART. Its runtime result is pending.

No successful 5.15 recovery or Android system boot is claimed.

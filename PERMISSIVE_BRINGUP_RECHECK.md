# Global permissive bring-up — 2026-10-12

Explicitly requested temporary development configuration; not production ready.

The 5.15 profile enables SECURITY_SELINUX_FORCE_PERMISSIVE and SECURITY_SELINUX_DEVELOP. Kernel enforcement starts disabled, the enforcing boot parameter is clamped to zero, and selinuxfs writes requesting enforcement are acknowledged while retaining zero. This also handles Android user-build init attempting to enable enforcement. The embedded configuration was checked in production and diagnostic Images.

Device functional revision 5530f83541f89d2b50218f89f047312d9d48bd1f adds explicit androidboot.selinux=permissive and enforcing=0 arguments to the selected 5.15 profile. Manifest update 0fc4b0f pins it. The explicit 4.19 source fallback remains separately selected; research recovery uses a private modified ramdisk.

The temporary 4.19 diagnostic recovery now writes zero to selinuxfs during early-init. Device checks returned getenforce=Permissive and enforce=0. This is global permissive mode, not just permissive init/shell domains. Host ADB keys, policy/image payloads and device identifiers remain private.

Android 17 source boot/vendor_boot images completed rebuilding with the explicit boot arguments (10m11s). Source and packaged-image checks passed for all 207 matching modules and embedded configuration. System-side runtime verification remains pending successful 5.15 boot.

Isolated diagnostic candidates contain their own 149 rebuilt native modules and distinct release suffixes; no mixing with the production 207-module bundle. CRCs, dependencies and embedded configs passed. VA48, a single-revision DTB and EFI-disabled controls returned to fastboot before ADB. The pre-MMU entry-marker option builds enabled and disabled; strict patch style checks passed. W=1 object preparation hit pre-existing missing-prototype errors in unchanged vDSO code; default-warning object checks passed and the disabled object contains no marker instructions. Runtime marker capture remains pending. No UART hardware is used.

The no-EFI gzip recovery control with a merged single-revision DTB and erased dtbo stayed at the POCO logo without exposing ADB or returning to fastboot. Physical reset was required; restored globally permissive 4.19 diagnostic recovery still had no retained entry marker. Correcting only the diagnostic USB-controller argument did not expose ADB. No 5.15 execution is established by the logo.

USB source correction: alioth functional revision 901967f selects a600000.usb for the native child node; common revision cf633a7 uses ro.boot.usbcontroller in system and charger init instead of hard-coding a600000.dwc3. The legacy 4.19 profile keeps its original argument. Runtime validation of this correction is pending.

The clock/power-preservation and gzip-with-appended-merged-DTB controls also exposed no ADB or fastboot. The user confirmed a POCO-logo hang on the former. Fastboot-path pstore retention must be tested separately before absence of a breadcrumb can localize the failure.

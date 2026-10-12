# Global permissive bring-up — 2026-10-12

Explicitly requested temporary development configuration; not production ready.

The 5.15 profile enables SECURITY_SELINUX_FORCE_PERMISSIVE and SECURITY_SELINUX_DEVELOP. Kernel enforcement starts disabled, the enforcing boot parameter is clamped to zero, and selinuxfs writes requesting enforcement are acknowledged while retaining zero. This also handles Android user-build init attempting to enable enforcement. The embedded configuration was checked in production and diagnostic Images.

Device functional revision 5530f83541f89d2b50218f89f047312d9d48bd1f adds explicit androidboot.selinux=permissive and enforcing=0 arguments to the selected 5.15 profile. Manifest update 0fc4b0f pins it. The explicit 4.19 source fallback remains separately selected; research recovery uses a private modified ramdisk.

The temporary 4.19 diagnostic recovery now writes zero to selinuxfs during early-init. Device checks returned getenforce=Permissive and enforce=0. This is global permissive mode, not just permissive init/shell domains. Host ADB keys, policy/image payloads and device identifiers remain private.

Android 17 source boot/vendor_boot images are rebuilding with the explicit boot arguments. System-side runtime verification remains pending successful 5.15 boot.

Isolated diagnostic candidates contain their own 149 rebuilt native modules and distinct release suffixes; no mixing with the production 207-module bundle. CRCs, dependencies and embedded configs passed. VA48, a single-revision DTB and EFI-disabled controls returned to fastboot before ADB. The pre-MMU entry-marker option builds enabled and disabled; strict patch style checks passed. W=1 object preparation hit pre-existing missing-prototype errors in unchanged vDSO code; default-warning object checks passed and the disabled object contains no marker instructions. Runtime marker capture remains pending. No UART hardware is used.

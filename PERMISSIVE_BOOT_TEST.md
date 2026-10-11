# Permissive device boot test

The 5.15.206-g10845c8acffd development candidate uses SECURITY_SELINUX_FORCE_PERMISSIVE=y. This explicitly keeps SELinux permissive even when user init requests enforcing; policy loading and denial logging remain active. The source option defaults to n. Do not use this test configuration in production.

All eight vendor groups and 206 matching modules compiled; packaging and independent image checks passed. Actual-source host checks covered 14 enforcing-request/boot-parameter cases.

On unlocked alioth slot A, matching vendor_boot_a and dtbo_a writes succeeded and fastboot accepted the temporary boot.img. boot_a was not written. The device returned to fastboot without ADB enumeration at the first 20-second observation. Android boot was not achieved; the failure cause is not yet known.

Local 4.19 vendor_boot and dtbo restore images were successfully written back and reboot recovery was requested. These restore images came from current local ROM output, not a partition backup. System and userdata were not written. See permissive-device-test.json for the scoped record.

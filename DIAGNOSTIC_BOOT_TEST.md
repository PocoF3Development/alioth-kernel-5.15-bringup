# Verbose boot diagnostic candidate

This development variant retains forced permissive SELinux, the legacy 512 KiB ARM64 Image offset and no-LTO builds. It adds ignore_loglevel, loglevel=8, initcall_debug, panic=0, printk.devkmsg=on and printk.always_kmsg_dump=1 in both compiled CMDLINE and alioth chosen bootargs. The packaged merged DT and embedded kernel configuration are checked independently.

PANIC_TIMEOUT is changed from -1 to 0, and QCOM_FORCE_WDOG_BITE_ON_PANIC is disabled. This removes those configured immediate panic-reboot paths; it does not disable hardware watchdogs or guarantee retention if firmware resets the device. Native ramoops console and pmsg reservations remain unchanged. This is a diagnostic candidate, not a proven fix for Android boot.

The user reported Magisk installed, but the device was observed in Evolution X recovery running 4.19.325-cip136-st20-perf-gbd43bde102a8. The recovery shell was UID 2000, su was absent, ADB root was disabled and pstore was unreadable. After a reboot request, ADB remained unauthorized; the existing WSL host key did not restore access. System Magisk root was not verified. No partition writes or diagnostic candidate hardware test were performed during this turn.

The preceding 5.15 legacy-offset test returned to fastboot. Full donor parity and native WLAN/Xiaomi camera integration remain incomplete as documented in DONOR_CONFIG_PARITY.md.

## Built candidate

5.15.206-g689b59f88c4d / 689b59f88c4d56b4e588a8f47247eae6d46537a6 compiled with all eight external build groups and 206 staged matching modules. depmod passed. Independent image unpacking, exact bundled module checks, actual DTBO merge, embedded configuration and merged diagnostic bootargs checks passed. Device test remains pending because recovery ADB is unauthorized; no successful Android boot is claimed.

# Built-in recovery control — 2026-10-12

Requested comparison against the largely built-in 4.19 configuration. The native 5.15 diagnostic already builds USB glue/PHY support into the Image, but still has 149 native loadable modules. This separate control selects the 148 formerly modular native configuration symbols as built-in and disables CONFIG_MODULES, while keeping VA39, EFI disabled, no LTO and no pre-MMU marker writes. It is building; no recovery boot is claimed.

The private recovery ramdisk starts ADB before recovery UI, requests root ADB and is globally permissive. Root ADB was verified on 4.19 (UID 0 and su context), allowing direct read-only collection of the actual firmware DTB and inactive boot partition backups. Private authorization material and raw device data are not published.

This is a recovery isolation experiment. External display/audio/camera/GPU/vendor modules are not converted by this native-only configuration; the production Android source profile still uses its matching 207-module bundle. Only a measured boot result can justify promoting the needed built-in dependencies.

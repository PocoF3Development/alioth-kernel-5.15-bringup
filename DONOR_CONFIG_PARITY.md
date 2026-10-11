# Donor configuration parity review

This candidate is experimental and is not certified to boot Android. The donor alioth.config and sm8250-common.config are audited in donor-config-parity.json against the resolved native 5.15 configuration. Disabled debugging selections are respected, including DEBUG_FS, PAGE_OWNER and PAGE_PINNER. LTO remains disabled for development builds.

The port includes donor battery authentication, BQ2597x charge-pump, proximity, touch-common and common peripheral sources with preserved authorship. The charge-pump driver does not establish safe fast charging: the PD/fast-charge manager is still unported. Optional dual-backlight panel PWM and tablet keyboard host-reset hooks return EOPNOTSUPP if their provider is absent.

Incomplete donor selections: DVB_MPQ, DVB_MPQ_DEMUX, RMNET_PERF, RMNET_SHS and TECHPACK_CAMERA_XIAOMI. Native QCA6390 WLAN and Kona camera compilation also does not establish PCI/CNSS DT integration or Xiaomi camera ABI/DT compatibility. Camera heap reserve/refill behavior remains incomplete. These are explicit gaps, not equivalent implementations.

No flashing or device boot test has been performed. Image assembly and static validation must not be interpreted as successful runtime boot.

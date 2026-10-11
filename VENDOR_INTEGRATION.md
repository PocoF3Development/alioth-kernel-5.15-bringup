# Vendor driver integration checkpoint

The native DT needs downstream RPMh ARC corner vote regulators for Qualcomm's modified GCC/GPUCC implementation. pending/sm8250-xiaomi-alioth-corners.dtsi preserves the donor MX/CX/GFX corner definitions and native clock supply names. It is staged outside the active kernel tree until the current Image build finishes. REGULATOR_RPMH must be available before these clocks probe; the current candidate has it modular. Do not treat the native MTP supply topology alone as sufficient.

Release-pinned KGSL, Kona display and legacy Kona audio source compilation reaches LTO. Their module link probes require core provider exports and external-display symbols; core module build is running. No unresolved-symbol checks have been suppressed. Initial display invocation without CONFIG_DRM_MSM built an empty target and is superseded by the actual CONFIG_DRM_MSM=m probe.

Alioth FocalTech SPI, Xiaomi touchfeature, FPC and Goodix sources and the Xiaomi notification chain compile. The display chain still needs actual display lifecycle emitters. The translated input DT includes donor GPIO/regulator/bus wiring and haptic calibration/RTP data. This is compile evidence only.

CS35L41 imports preserve donor authorship, including the platform header and diagnostic fixes. Separate 5.15 adaptations use asoc_rtd_to_codec, mute_stream with no_capture_mute, symmetric_rate, current debugfs APIs and a private static DSP helper. TFA9874 source is staged but has a MUNCH-only firmware variable guard; it is not enabled for alioth. Machine routing and amplifier DT are still required.

Existing October 11 alioth user boot and vendor_boot images were inspected read-only. Both use header 3; DTB is in vendor_boot. Unpacked components and exact mkbootimg arguments are under boot-input/. No images are flashed or published.

## Updated integration

Clock ARC definitions are now integrated and REGULATOR_RPMH/proxy-consumer are built in. Native mode constants are isolated from the legacy ARC header. The alioth notification chain now has release DSI bridge and low-power lifecycle emitters, gated on CONFIG_XIAOMI_DRM_NOTIFIER and primary display_type; both objects compile with the notifier enabled. Module linking against matching candidate exports is still pending.

Full LTO is temporarily replaced by user-authorized ThinLTO. WSL interruption recovery and exact pending gates are recorded in integration-checkpoint.json. Existing DTBO has one version-0 entry, page size 4096, id/rev/custom fields zero; its old overlay must not be applied unmodified to the native DT. Header-3 packing metadata is preserved under boot-input/.

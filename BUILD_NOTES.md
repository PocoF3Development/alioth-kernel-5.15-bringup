# Reproducing compile probes

Run scripts inside WSL/Ubuntu from the Linux checkout. Do not run Windows Git against these repositories.

- sync-kernel-deps.py fetches only selected manifest-pinned dependencies. It refuses to switch an existing checkout with local changes or a different HEAD; vendor driver ports are therefore preserved.
- compile-reference.py builds a standalone msm-kernel Image from gki_defconfig plus the release Kona fragment, with release-pinned Clang 14 and four compilation jobs. This is a core compile probe, not the complete Qualcomm common/msm mixed build or alioth packaging.
- compile-nfc-probe.py resolves alioth board selection plus NFC and AW8697 modules, prepares separate headers, and compiles the NFC and haptic composite objects. Despite its initial filename, it now covers both imported peripherals. It does not establish full module linking or hardware support.

Output directories are confined to this research folder. The reference probe retains full LTO. The current packaged candidate was built with ThinLTO, CFI and BTF. For subsequent development builds, alioth-build-speed.config selects LTO_NONE and disables Clang CFI because it requires LTO. Run configure-alioth.py and rebuild the complete matching kernel/module set before packaging this different mode. BTF remains enabled. No ROM out directory is used.

Manifests and project-pins.json preserve upstream revision provenance. Local source imports are on msm-kernel's alioth-bringup branch. Reference DT source is only investigative and is not claimed to match the release.

SPSS checks: run validate-alioth-spss-abi.py, validate-alioth-spss-dt.py and validate-alioth-spss-cmac.py. ABI validation uses actual donor/native headers for ARM64 and ARM32. CMAC tests extract the actual legacy ioctl case and mock MMIO/services; they do not test secure firmware.

Additional checks: validate-alioth-spss-vmperm.py and validate-alioth-spss-compat.py exercise extracted production helpers with mocked services.

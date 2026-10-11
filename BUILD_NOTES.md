# Reproducing compile probes

Run scripts inside WSL/Ubuntu from the Linux checkout. Do not run Windows Git against these repositories.

- sync-kernel-deps.py fetches only selected manifest-pinned dependencies. It refuses to switch an existing checkout with local changes or a different HEAD; vendor driver ports are therefore preserved.
- compile-reference.py builds a standalone msm-kernel Image from gki_defconfig plus the release Kona fragment, with release-pinned Clang 14 and four compilation jobs. This is a core compile probe, not the complete Qualcomm common/msm mixed build or alioth packaging.
- compile-nfc-probe.py resolves alioth board selection plus NFC and AW8697 modules, prepares separate headers, and compiles the NFC and haptic composite objects. Despite its initial filename, it now covers both imported peripherals. It does not establish full module linking or hardware support.

Output directories are confined to this research folder. Core full LTO remains enabled as selected by the reference config; its global optimization phase runs separately from parallel compilation and can take substantial time. No ROM out directory is used.

Manifests and project-pins.json preserve upstream revision provenance. Local source imports are on msm-kernel's alioth-bringup branch. Reference DT source is only investigative and is not claimed to match the release.

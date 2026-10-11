# Standalone kernel research workspace, not an Android Make module tree.
# Soong's FindFirstNamedAt stops descending after finding this file.
# Do not include subdirectory Android.mk files: these are pinned source/tool
# copies whose matching kernel artifacts are consumed explicitly by BoardConfig.

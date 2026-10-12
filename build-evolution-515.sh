#!/bin/bash
set -o pipefail
cd -- "$(dirname -- "$0")/../.." || exit 1
export TARGET_USE_ALIOTH_KERNEL_515=true
. build/envsetup.sh || exit 1
lunch lineage_alioth-cp2a-user || exit 1
if (( $# )); then
    m "$@"
else
    m evolution
fi

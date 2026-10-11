#!/usr/bin/env python3
"""Resolve the experimental alioth configuration; run before building."""
import os, subprocess
from pathlib import Path
p = Path(__file__).resolve().parent
k = p / 'msm-kernel'
o = p / 'out/alioth-config'
o.mkdir(parents=True, exist_ok=True)
(p / 'logs').mkdir(exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(p / 'toolchain/clang-r450784e/bin') + ':' + env['PATH']
base = ['make', '-C', str(k), 'O=' + str(o), 'ARCH=arm64', 'LLVM=1', 'LLVM_IAS=1']
subprocess.run(base + ['gki_defconfig'], env=env, check=True)
fragments = [k / 'arch/arm64/configs/vendor/kona_GKI.config', p / 'alioth-bringup.config', p / 'alioth-earlyboot.config', p / 'alioth-build-speed.config', p / 'alioth-donor-parity.config']
subprocess.run([str(k / 'scripts/kconfig/merge_config.sh'), '-m', '-O', str(o), str(o / '.config')] + [str(f) for f in fragments], env=env, check=True, cwd=k)
subprocess.run(base + ['olddefconfig'], env=env, check=True)
print('Experimental configuration resolved; inspect .config before building.')

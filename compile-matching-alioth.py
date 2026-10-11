#!/usr/bin/env python3
"""Rebuild one matching kernel and external module set for the test image."""
from pathlib import Path
import os, subprocess, json, time
p = Path(__file__).resolve().parent
k = p / 'msm-kernel'
o = p / 'out/alioth-config'
env = os.environ.copy()
env['PATH'] = str(p / 'toolchain/clang-r450784e/bin') + ':' + env['PATH']
subprocess.run(['python3', str(p / 'compile-alioth.py')], check=True)
start = time.time()
cmd = ['make', '-C', str(k), 'O=' + str(o), 'ARCH=arm64', 'LLVM=1',
       'LLVM_IAS=1', '-j8', 'LD=ld.lld --threads=4', 'modules']
with (p / 'logs/alioth-matching-core-modules.log').open('w') as log:
    r = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
result = {'returncode': r.returncode, 'seconds': time.time() - start,
          'kernel_source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=k, text=True).strip(),
          'kernel_release': (o / 'include/config/kernel.release').read_text().strip()}
(p / 'alioth-matching-core-modules-results.json').write_text(json.dumps(result, indent=2) + '\n')
print('core modules', r.returncode, flush=True)
if r.returncode:
    raise SystemExit(r.returncode)
subprocess.run(['python3', str(p / 'compile-alioth-vendor.py')], check=True)
subprocess.run(['python3', str(p / 'stage-alioth-modules.py')], check=True)

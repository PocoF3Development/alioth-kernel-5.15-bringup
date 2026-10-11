#!/usr/bin/env python3
"""Stage only verified matching core/vendor modules; do not alter ROM images."""
from pathlib import Path
import subprocess, shutil, json
p=Path(__file__).resolve().parent;o=p/'out/alioth-config';v=p/'sources/vendor/qcom/opensource'
release=(o/'include/config/kernel.release').read_text().strip()
stage=p/'staging/matching-modules';lib=stage/'lib/modules'/release;lib.mkdir(parents=True,exist_ok=True)
rows=[]
def install(source,relative):
 vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(source)]).decode().strip()
 if vermagic.split()[0]!=release:raise RuntimeError('Stale module: '+str(source))
 dest=lib/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);rows.append(str(relative))
for name in (o/'modules.order').read_text().splitlines():install(o/name,Path('kernel')/name)
roots=[v/'graphics-kernel',v/'display-drivers',v/'audio-kernel/legacy',v/'securemsm-kernel',v/'mm-drivers/msm_ext_display']
for root in roots:
 for name in (root/'modules.order').read_text().splitlines():
  source=Path(name)
  if not source.is_absolute():source=root/source
  install(source,Path('extra')/root.name/source.relative_to(root))
for name in ['modules.builtin','modules.builtin.modinfo']:shutil.copy2(o/name,lib/name)
(lib/'modules.order').write_text('\n'.join(rows)+'\n')
combined=stage/'combined.symvers';combined.write_text((o/'Module.symvers').read_text()+''.join((root/'Module.symvers').read_text() for root in roots))
r=subprocess.run(['depmod','-e','-E',str(combined),'-b',str(stage),release],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(p/'logs/alioth-module-dependency-audit.log').write_text(r.stdout)
result={'kernel_release':release,'module_count':len(rows),'modules':rows,'depmod_returncode':r.returncode,'depmod_output':r.stdout,'runtime_validated':False,'boot_image_ready':False}
(p/'alioth-module-bundle-results.json').write_text(json.dumps(result,indent=2)+'\n');print('Staged',len(rows),'matching modules; depmod',r.returncode,flush=True)
if r.returncode or r.stdout.strip():raise SystemExit(1)

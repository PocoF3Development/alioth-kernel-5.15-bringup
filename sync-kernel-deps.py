#!/usr/bin/env python3
"""Fetch only manifest-pinned kernel dependencies, recording per-project results."""
import concurrent.futures,json,subprocess
from pathlib import Path
W=Path(__file__).resolve().parent
pins=json.loads((W/'project-pins.json').read_text())
selected=[p for p in pins if p['name'] in ['kernel/build','kernel_platform/external/dtc','platform/vendor/qcom/kona','device/qcom/common'] or (p['manifest']=='vendor' and ('kernel' in p['name'] or any(x in p['name'] for x in ['display-drivers','mm-drivers','touch-drivers','video-driver','wlan/fw-api','wlan/platform','wlan/qca-wifi-host-cmn','wlan/qcacld-3.0'])))]
(W/'logs').mkdir(exist_ok=True)
def fetch(p):
 dest=W/'sources'/p.get('path',p['name']); dest.mkdir(parents=True,exist_ok=True)
 log=W/'logs'/(p['name'].replace('/','_')+'.log')
 try:
  if (dest/'.git').exists():
   current=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=dest,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
   if current.returncode==0:
    dirty=subprocess.check_output(['git','status','--porcelain'],cwd=dest,text=True)
    if current.stdout.strip()!=p['revision']:
     raise RuntimeError('Existing checkout has local changes or a different HEAD; refusing to switch it')
    status={'name':p['name'],'revision':p['revision'],'path':str(dest.relative_to(W)),'status':'ok','local_changes_preserved':bool(dirty)}
    print(json.dumps(status),flush=True); return status
  with log.open('w') as f:
   def run(args): subprocess.run(args,cwd=dest,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
   if not (dest/'.git').exists():
    run(['git','init']); run(['git','remote','add','origin','https://git.codelinaro.org/clo/la/'+p['name']+'.git'])
   run(['git','fetch','--depth=1','origin',p['revision']]); run(['git','checkout','--detach','FETCH_HEAD'])
  status={'name':p['name'],'revision':p['revision'],'path':str(dest.relative_to(W)),'status':'ok'}
 except Exception as e: status={'name':p['name'],'status':'failed','error':str(e),'log':str(log.relative_to(W))}
 print(json.dumps(status),flush=True); return status
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(fetch,selected))
(W/'sync-results.json').write_text(json.dumps(results,indent=2)+'\n')

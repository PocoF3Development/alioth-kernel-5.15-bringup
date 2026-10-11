#!/usr/bin/env python3
"""Standalone Kona compile probe; does not package an alioth boot image."""
import os,subprocess,json,time
from pathlib import Path
W=Path(__file__).resolve().parent; K=W/'msm-kernel'; O=W/'out/reference-kona'; O.mkdir(parents=True,exist_ok=True)
T=W/'toolchain/clang-r450784e/bin'; env=os.environ.copy(); env['PATH']=str(T)+':'+env['PATH']
env['ARCH']='arm64'; env['LLVM']='1'; env['LLVM_IAS']='1'
cmd=['make','-C',str(K),'O='+str(O),'ARCH=arm64','LLVM=1','LLVM_IAS=1','-j4']
results=[]
def run(args,name):
 start=time.time()
 with (W/'logs'/name).open('w') as log:
  rc=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
 results.append({'command':args,'returncode':rc,'seconds':round(time.time()-start,1),'log':'logs/'+name})
 (W/'compile-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(name,'returncode',rc,flush=True)
 if rc: raise SystemExit(rc)
run(cmd+['gki_defconfig'],'reference-defconfig.log')
run([str(K/'scripts/kconfig/merge_config.sh'),'-m','-O',str(O),str(O/'.config'),str(K/'arch/arm64/configs/vendor/kona_GKI.config')],'reference-merge.log')
run(cmd+['olddefconfig'],'reference-olddefconfig.log')
run(cmd+['Image'],'reference-Image.log')

#!/usr/bin/env python3
import os,subprocess,json,time
from pathlib import Path
p=Path(__file__).resolve().parent;k=p/'msm-kernel';o=p/'out/alioth-config'
env=os.environ.copy();env['PATH']=str(p/'toolchain/clang-r450784e/bin')+':'+env['PATH']
base=['make','-C',str(k),'O='+str(o),'ARCH=arm64','LLVM=1','LLVM_IAS=1','-j8','LD=ld.lld --threads=4']
results=[]
for target in ['Image','qcom/sm8250-xiaomi-alioth.dtb']:
 start=time.time()
 with (p/'logs'/('alioth-'+target.replace('/','_')+'.log')).open('w') as log:r=subprocess.run(base+[target],env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'target':target,'returncode':r.returncode,'seconds':time.time()-start});(p/'alioth-build-results.json').write_text(json.dumps(results,indent=2));print(target,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)

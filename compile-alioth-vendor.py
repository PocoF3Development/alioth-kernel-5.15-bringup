#!/usr/bin/env python3
"""Build vendor modules against the matching experimental alioth core."""
from pathlib import Path
import os, subprocess, json, time
p=Path(__file__).resolve().parent;k=p/'msm-kernel';o=p/'out/alioth-config'
v=p/'sources/vendor/qcom/opensource';env=os.environ.copy();env['PATH']=str(p/'toolchain/clang-r450784e/bin')+':'+env['PATH']
base=['make','-C',str(k),'O='+str(o),'ARCH=arm64','LLVM=1','LLVM_IAS=1','-j8','LD=ld.lld --threads=4']
entries=[('ext-display',v/'mm-drivers/msm_ext_display',['MM_ROOT='+str(v/'mm-drivers'),'KERNEL_SRC='+str(k)]),('graphics',v/'graphics-kernel',['CONFIG_ARCH_KONA=y','KERNEL_SRC='+str(k),'KGSL_PATH='+str(v/'graphics-kernel')]),('securemsm',v/'securemsm-kernel',['CONFIG_ARCH_KONA=y','KERNEL_SRC='+str(k),'SSG_MODULE_ROOT='+str(v/'securemsm-kernel')]),('display',v/'display-drivers',['CONFIG_ARCH_KONA=y','CONFIG_DRM_MSM=m','KERNEL_SRC='+str(k),'KERNEL_ROOT='+str(k),'DISPLAY_ROOT='+str(v/'display-drivers')]),('audio',v/'audio-kernel/legacy',['MODNAME=audio','CONFIG_ARCH_KONA=y','KERNEL_SRC='+str(k),'AUDIO_ROOT='+str(v/'audio-kernel/legacy'),'LEGACY_PATH='+str(v/'audio-kernel/legacy')])]
results=[]
for name,root,args in entries:
 symbols=v/'mm-drivers/msm_ext_display/Module.symvers'
 extra=[]
 if name in ['display','audio'] and symbols.exists():extra.append(str(symbols))
 secure_symbols=v/'securemsm-kernel/Module.symvers'
 if name=='display' and secure_symbols.exists():extra.append(str(secure_symbols))
 if extra:args+=['KBUILD_EXTRA_SYMBOLS='+' '.join(extra)]
 cmd=base+['M='+str(root)]+args+['modules'];start=time.time()
 with (p/'logs'/('alioth-vendor-'+name+'.log')).open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'returncode':r.returncode,'seconds':time.time()-start,'kernel_source_head':subprocess.check_output(['git','-C',str(k),'rev-parse','HEAD']).decode().strip(),'vendor_source_head':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD']).decode().strip(),'kernel_release':(o/'include/config/kernel.release').read_text().strip()});(p/'alioth-vendor-module-results.json').write_text(json.dumps(results,indent=2)+'\n');print(name,r.returncode,flush=True)

raise SystemExit(1 if any(r["returncode"] for r in results) else 0)

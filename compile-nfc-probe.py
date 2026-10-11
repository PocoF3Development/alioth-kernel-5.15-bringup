#!/usr/bin/env python3
import os,subprocess,json,shutil,time
from pathlib import Path
W=Path(__file__).resolve().parent; K=W/'msm-kernel'; O=W/'out/nfc-probe'; O.mkdir(parents=True,exist_ok=True)
shutil.copyfile(W/'out/reference-kona/.config',O/'.config')
subprocess.run([str(K/'scripts/config'),'--file',str(O/'.config'),'--module','NFC_NQ','--enable','MACH_XIAOMI_ALIOTH','--enable','INPUT_MISC','--module','INPUT_AW8697_HAPTIC'],check=True)
env=os.environ.copy();env['PATH']=str(W/'toolchain/clang-r450784e/bin')+':'+env['PATH']
args=['make','-C',str(K),'O='+str(O),'ARCH=arm64','LLVM=1','LLVM_IAS=1','-j4'];results=[]
for target,name in [('olddefconfig','nfc-probe-config.log'),('modules_prepare','nfc-probe-prepare.log'),('drivers/nfc/nq-nci.o','nfc-probe-object.log'),('drivers/input/misc/aw8697_haptic/aw8697_haptic.o','haptic-probe-object.log')]:
 start=time.time()
 with (W/'logs'/name).open('w') as f:rc=subprocess.run(args+[target],env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 results.append({'target':target,'returncode':rc,'seconds':round(time.time()-start,1),'log':'logs/'+name})
 (W/'nfc-probe-results.json').write_text(json.dumps(results,indent=2)+'\n');print(name,rc,flush=True)
 if rc:raise SystemExit(rc)

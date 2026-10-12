from pathlib import Path
import subprocess, time, json
p=Path(__file__).resolve().parent
while subprocess.run(['kill','-0','1606451'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0: time.sleep(5)
results=[]
for name in ['compile-alioth-vendor.py','stage-alioth-modules.py','pack-alioth-test-images.py','validate-alioth-boot-system.py','validate-alioth-test-images.py']:
 r=subprocess.run(['python3',str(p/name)],capture_output=True,text=True)
 results.append({'script':name,'returncode':r.returncode,'output':(r.stdout+r.stderr)[-4000:]})
 (p/'donor-parity-final-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(name,r.returncode,flush=True)
 if r.returncode: break

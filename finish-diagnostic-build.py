from pathlib import Path
import subprocess,time,json
p=Path(__file__).resolve().parent
while subprocess.run(['kill','-0','1786524'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:time.sleep(5)
r=[]
for n in ['pack-alioth-test-images.py','validate-alioth-boot-system.py','validate-alioth-test-images.py','validate-alioth-image-offset.py','validate-alioth-boot-diagnostics.py']:
 x=subprocess.run(['python3',str(p/n)],capture_output=True,text=True)
 r.append({'script':n,'returncode':x.returncode,'output':(x.stdout+x.stderr)[-3500:]})
 (p/'diagnostic-final-results.json').write_text(json.dumps(r,indent=2)+'\n')
 print(n,x.returncode,flush=True)
 if x.returncode:break

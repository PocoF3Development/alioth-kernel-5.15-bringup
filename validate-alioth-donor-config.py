#!/usr/bin/env python3
"""Inventory donor fragment coverage without treating dropped symbols as enabled."""
from pathlib import Path
import re,json,subprocess,hashlib
p=Path(__file__).resolve().parent;k=p/'msm-kernel';o=p/'out/alioth-config';d=Path('/home/johnmart19/evo/kernel/xiaomi/sm8250')
def parse(s):
 r=dict(re.findall(r'^CONFIG_(\w+)=(.*)$',s,re.M));r.update({x:'n' for x in re.findall(r'^# CONFIG_(\w+) is not set$',s,re.M)});return r
want={};inputs=[]
for name in ['sm8250-common','alioth']:
 f=d/f'arch/arm64/configs/vendor/xiaomi/{name}.config';want.update(parse(f.read_text()));inputs.append({'path':str(f.relative_to(d)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
actual=parse((o/'.config').read_text());rows=[]
aliases={'BUILD_ARM64_DT_OVERLAY':'Native DTC overlay + mkdtimg + independently merged board-44 overlay','ION_CAMERA_HEAP':'ALIOTH_ION_COMPAT implements nonsecure heap 20 through native system DMA heaps; donor reserve/refill unported','CMDLINE':'Native DT ramoops reserves donor 0xb0000000/4 MiB with 2 MiB console and pmsg; cgroup_disable=pressure retained','QCA_CLD_WLAN':'External QCA6390 wlan.ko and CNSS platform module builds; PCI/CNSS DT runtime integration remains incomplete','QCA_CLD_WLAN_PROFILE':'External module build explicitly selects qca6390 profile'}
for key,value in want.items():
 resolved=actual.get(key)
 if resolved==value:status='exact';note=''
 elif value=='n' and resolved is None:status='disabled_or_removed';note='No enabled implementation under the old symbol'
 elif key in aliases:status='mapped_with_limits';note=aliases[key]
 elif value=='y' and resolved=='m':status='module';note='Native module must be included and loaded instead of being built in'
 else:status='missing';note='Required implementation/configuration has not reached donor parity'
 rows.append({'symbol':'CONFIG_'+key,'donor':value,'resolved':resolved,'status':status,'note':note})
blockers=[r['symbol'] for r in rows if r['status']=='missing']
report={'donor_head':subprocess.check_output(['git','-C',str(d),'rev-parse','HEAD'],text=True).strip(),'kernel_head':subprocess.check_output(['git','-C',str(k),'rev-parse','HEAD'],text=True).strip(),'kernel_release':(o/'include/config/kernel.release').read_text().strip(),'fragments_in_order':['sm8250-common.config','alioth.config'],'inputs':inputs,'rows':rows,'missing_requirements':blockers,'complete_donor_parity':not blockers,'hardware_boot_verified':False,'flashed':False}
(p/'donor-config-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'options':len(rows),'missing_requirements':blockers,'complete_donor_parity':not blockers}))

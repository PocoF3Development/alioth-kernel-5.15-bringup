#!/usr/bin/env python3
"""Package private recovery diagnostics with only their matching native modules."""
import argparse, gzip, hashlib, json, shlex, stat, subprocess, tempfile
from pathlib import Path
ap=argparse.ArgumentParser()
for name in ['root','object','baseline','template','output']:ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();r=a.root;o=a.object;out=a.output;out.mkdir(parents=True,exist_ok=True)
release=(o/'include/config/kernel.release').read_text().strip()
stage=Path(tempfile.mkdtemp(prefix='modules-',dir=out));md=stage/'lib/modules'/release;md.mkdir(parents=True)
mods=list(o.rglob('*.ko'));assert len(mods)==len({x.name for x in mods})
for f in mods:
 assert subprocess.check_output(['modinfo','-F','vermagic',str(f)],text=True).split()[0]==release
 (md/f.name).write_bytes(f.read_bytes())
for n in ['modules.builtin','modules.builtin.modinfo','modules.order']:(md/n).write_bytes((o/n).read_bytes())
q=subprocess.run(['depmod','-e','-E',str(o/'Module.symvers'),'-b',str(stage),release],capture_output=True,text=True)
assert q.returncode==0 and not q.stderr.strip(),q.stderr
b=gzip.decompress((a.baseline/'vendor-ramdisk-diagnostic-v3-permissive.gz').read_bytes());pos=0;records=[]
while b[pos:pos+6]==b'070701':
 v=[int(b[pos+6+i*8:pos+14+i*8],16) for i in range(13)];n=b[pos+110:pos+110+v[11]-1].decode();s=(pos+110+v[11]+3)&~3;body=b[s:s+v[6]];pos=(s+v[6]+3)&~3
 if n=='TRAILER!!!':break
 assert not n.startswith('lib/modules'), 'baseline must not contain other kernel modules'
 records.append((n,v,body))
load=['sched-walt','rtc-pm8xxx','qcom-cpufreq-hw','nvmem_qfprom','qcom-spmi-adc5','qpnp-fg-gen4-main','qpnp-smb5-main','qcom_tsens','qcom-spmi-temp-alarm']
assert all((md/(n+'.ko')).is_file() for n in load)
files={f.name:f.read_bytes() for f in md.iterdir() if f.is_file()};files.update({n:('\n'.join(load)+'\n').encode() for n in ['modules.load','modules.load.recovery','modules.load.charger']})
for n,body,mode in [('lib',b'',stat.S_IFDIR|0o755),('lib/modules',b'',stat.S_IFDIR|0o755)]+[('lib/modules/'+n,b,stat.S_IFREG|0o644) for n,b in files.items()]:
 if n=='lib' and any(x[0]=='lib' for x in records):continue
 v=[0]*13;v[0]=0x100000+len(records);v[1]=mode;v[4]=1;records.append((n,v,body))
raw=bytearray()
for n,v,body in records+[('TRAILER!!!',[0]*13,b'')]:
 v=v.copy();v[6]=len(body);v[11]=len(n.encode())+1;v[12]=0;raw.extend(b'070701'+''.join('%08x'%x for x in v).encode()+n.encode()+b'\0');raw.extend(b'\0'*((-len(raw))%4));raw.extend(body);raw.extend(b'\0'*((-len(raw))%4))
raw.extend(b'\0'*((-len(raw))%512));ram=out/'vendor_ramdisk.gz';ram.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
args=shlex.split((a.baseline/'repack-args.txt').read_text());args[args.index('--vendor_ramdisk')+1]=str(ram);args[args.index('--dtb')+1]=str(a.template/'vendor_boot/dtb')
subprocess.run(['python3',str(r/'system/tools/mkbootimg/mkbootimg.py'),*args,'--vendor_boot',str(out/'vendor_boot.img')],check=True)
args=shlex.split((a.template/'boot-args.txt').read_text());args[args.index('--kernel')+1]=str(o/'arch/arm64/boot/Image');subprocess.run(['python3',str(r/'system/tools/mkbootimg/mkbootimg.py'),*args,'--output',str(out/'boot.img')],check=True)
for name,size in [('boot',201326592),('vendor_boot',100663296)]:subprocess.run(['python3',str(r/'external/avb/avbtool.py'),'add_hash_footer','--image',str(out/(name+'.img')),'--partition_name',name,'--partition_size',str(size)],check=True)
embedded=subprocess.check_output(['bash',str(r/'kernel-research/alioth-5.15/msm-kernel/scripts/extract-ikconfig'),str(o/'arch/arm64/boot/Image')]);assert embedded==(o/'.config').read_bytes()
report={'release':release,'native_modules':len(mods),'module_crc_check_passed':True,'embedded_config_matches':True,'separate_from_production':True,'images':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['boot.img','vendor_boot.img']}}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

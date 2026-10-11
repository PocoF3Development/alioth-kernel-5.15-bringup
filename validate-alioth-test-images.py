from pathlib import Path
import subprocess,json,gzip,struct,hashlib
p=Path(__file__).resolve().parent
r=(p/'out/alioth-config/include/config/kernel.release').read_text().strip()
o=p/'test-images'/r
w=p.parents[1]
def run(a): return subprocess.run(a,check=True,capture_output=True).stdout
for name in ['boot','vendor_boot']:
 run(['python3',str(w/'system/tools/mkbootimg/unpack_bootimg.py'),'--boot_img',str(o/(name+'.img')),'--out',str(o/('verify-'+name))])
assert (o/'verify-boot/kernel').read_bytes()==(p/'out/alioth-config/arch/arm64/boot/Image').read_bytes()
assert (o/'verify-boot/ramdisk').read_bytes()==(p/'boot-input/boot/ramdisk').read_bytes()
assert (o/'verify-vendor_boot/dtb').read_bytes()==(o/'alioth-base.dtb').read_bytes()
data=gzip.decompress((o/'verify-vendor_boot/vendor_ramdisk').read_bytes())
entries={};pos=0;trailers=0
while pos<len(data):
 while pos<len(data) and data[pos]==0: pos+=1
 if pos==len(data): break
 assert data[pos:pos+6] in [b'070701',b'070702']
 fields=[int(data[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
 size,nsize=fields[6],fields[11];pos+=110
 name=data[pos:pos+nsize-1].decode();pos=(pos+nsize+3)&~3
 payload=data[pos:pos+size];pos=(pos+size+3)&~3
 if name=='TRAILER!!!': trailers+=1
 else: entries[name]=payload
lib=p/'staging/matching-modules/lib/modules'/r
for f in lib.rglob('*'):
 if f.is_file(): assert entries['lib/modules/'+r+'/'+f.relative_to(lib).as_posix()]==f.read_bytes()
result=json.loads((o/'test-image-results.json').read_text())
for kind in ['modules.load','modules.load.recovery','modules.load.charger']:
 assert entries['lib/modules/'+r+'/'+kind].decode().splitlines()==result['first_stage_modules']
dtbo=(o/'dtbo.img').read_bytes();header=struct.unpack('>8I',dtbo[:32]);assert header[0]==0xd7b7ab1e and header[4]==1 and header[6]==4096
entry=struct.unpack('>8I',dtbo[header[5]:header[5]+32]);assert entry[2:4]==(0,0)
(o/'verify-overlay.dtbo').write_bytes(dtbo[entry[1]:entry[1]+entry[0]])
run(['fdtoverlay','-i',str(o/'verify-vendor_boot/dtb'),'-o',str(o/'verify-merged.dtb'),str(o/'verify-overlay.dtbo')])
assert run(['fdtget','-t','x',str(o/'verify-vendor_boot/dtb'),'/','qcom,board-id']).strip()==b'0 0'
assert run(['fdtget','-t','x',str(o/'verify-merged.dtb'),'/','qcom,board-id']).strip()==b'2c 0'
assert b'memory\n' in run(['fdtget','-l',str(o/'verify-merged.dtb'),'/'])
report={'kernel_release':r,'independent_unpack_passed':True,'kernel_and_boot_ramdisk_match':True,'all_staged_modules_and_metadata_match':True,'ramdisk_archives':trailers,'dtbo_table_and_actual_overlay_merge_passed':True,'runtime_tested':False,'flashed':False}
(p/'test-image-validation.json').write_text(json.dumps(report,indent=2)+'\n');(o/'test-image-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

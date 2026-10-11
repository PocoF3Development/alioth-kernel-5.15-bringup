#!/usr/bin/env python3
"""Export matching native artifacts for regular Android image assembly, never ramdisks."""
from pathlib import Path
import hashlib,json,shutil,subprocess
p=Path(__file__).resolve().parent
workspace=p.parents[1]
record=json.loads((p/'test-image-results.json').read_text())
release=record['kernel_release']
assert subprocess.check_output(['git','-C',str(p/'msm-kernel'),'rev-parse','HEAD'],text=True).strip()==record['kernel_source_head'], 'Source changed since validated build'
assert (p/'out/alioth-config/include/config/kernel.release').read_text().strip()==release
validation=json.loads((p/'test-image-validation.json').read_text())
assert validation['kernel_release']==release and validation['independent_unpack_passed']
bundle=json.loads((p/'alioth-module-bundle-results.json').read_text())
assert bundle['kernel_release']==release and bundle['depmod_returncode']==0 and not bundle['depmod_output'].strip()
image=p/'test-images'/release
for name,meta in record['images'].items():
 assert hashlib.sha256((image/name).read_bytes()).hexdigest()==meta['sha256']
target=workspace/'device/xiaomi/alioth/kernel-5.15/prebuilt'
assert not target.exists(), 'Bundle exists: preserve it and select a clean export directory before refreshing'
target.mkdir(parents=True)
(target/'dtb').mkdir();(target/'modules').mkdir()
shutil.copy2(p/'out/alioth-config/arch/arm64/boot/Image',target/'Image')
shutil.copy2(image/'alioth-base.dtb',target/'dtb/alioth.dtb')
shutil.copy2(image/'dtbo.img',target/'dtbo.img')
root=p/'staging/matching-modules/lib/modules'/release
modules=[]
for name in bundle['modules']:
 src=root/name;dest=target/'modules'/src.name
 assert not dest.exists(), 'Module basename collision'
 shutil.copy2(src,dest);modules.append(src.name)
load=record['first_stage_modules'];assert set(load)<=set(modules)
prefix='$(ALIOTH_KERNEL_515_BUNDLE)/modules/'
s='BOARD_VENDOR_RAMDISK_KERNEL_MODULES := '+' '.join(prefix+x for x in modules)+'\n'
normal_load=load+[x for x in modules if x not in load]
s+='BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := '+' '.join(normal_load)+'\n'
s+='BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := '+' '.join(load)+'\n'
s+='BOARD_VENDOR_RAMDISK_CHARGER_KERNEL_MODULES_LOAD := '+' '.join(load)+'\n'
(target/'modules.mk').write_text(s)
manifest={'kernel_release':release,'kernel_head':record['kernel_source_head'],'modules':len(modules),'module_load':normal_load,'recovery_module_load':load,'charger_module_load':load,'runtime_boot_verified':False,'files':{}}
for f in sorted(target.rglob('*')):
 if f.is_file():manifest['files'][f.relative_to(target).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
(target/'bundle.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'export':str(target),'kernel_release':release,'modules':len(modules),'production_ready':False}))

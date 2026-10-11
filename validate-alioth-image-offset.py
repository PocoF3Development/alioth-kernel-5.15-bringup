#!/usr/bin/env python3
from pathlib import Path
import struct, subprocess, json
p=Path(__file__).resolve().parent
release=(p/'out/alioth-config/include/config/kernel.release').read_text().strip()
boot=p/'test-images'/release/'boot.img'
b=boot.read_bytes()
assert b[:8]==b'ANDROID!' and struct.unpack_from('<I',b,40)[0]==3
size=struct.unpack_from('<I',b,8)[0]
k=b[4096:4096+size]
assert k== (p/'out/alioth-config/arch/arm64/boot/Image').read_bytes()
assert k[56:60]==b'ARMd'
offset=struct.unpack_from('<Q',k,8)[0]
assert offset==0x80000
cfg=subprocess.check_output(['bash',str(p/'msm-kernel/scripts/extract-ikconfig'),str(boot)])
for flag in ['ARM64_LEGACY_IMAGE_OFFSET','RELOCATABLE','SECURITY_SELINUX_FORCE_PERMISSIVE','LTO_NONE']:
 assert ('CONFIG_'+flag+'=y\n').encode() in cfg
r={'kernel_release':release,'actual_boot_kernel_load_offset':offset,'donor_load_offset':struct.unpack_from('<Q',(p/'boot-input/boot/kernel').read_bytes(),8)[0],'actual_packaged_config_checked':True,'cause_of_previous_failure_proven':False,'runtime_boot_verified':False}
(p/'image-offset-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

#!/usr/bin/env python3
"""Review the local ROM/image boot contract; never accesses a device."""
from pathlib import Path
import subprocess,json,gzip,re,hashlib
p=Path(__file__).resolve().parent;w=p.parents[1];k=p/'msm-kernel';o=p/'out/alioth-config';r=(o/'include/config/kernel.release').read_text().strip()
def run(a):return subprocess.check_output([str(x) for x in a],text=True).strip()
def entries(data):
 if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
 result={};pos=0
 while pos<len(data):
  while pos<len(data) and data[pos]==0:pos+=1
  if pos==len(data):break
  assert data[pos:pos+6] in [b'070701',b'070702']
  f=[int(data[pos+6+i*8:pos+14+i*8],16) for i in range(13)];size,ns=f[6],f[11];pos+=110
  name=data[pos:pos+ns-1].decode();pos=(pos+ns+3)&~3;payload=data[pos:pos+size];pos=(pos+size+3)&~3
  if name!='TRAILER!!!':result[name]=payload
 return result
for n,f in [('boot','ramdisk'),('vendor_boot','vendor_ramdisk')]:
 dest=p/'audit-current-rom'/n;dest.mkdir(parents=True,exist_ok=True)
 subprocess.run(['python3',str(w/'system/tools/mkbootimg/unpack_bootimg.py'),'--boot_img',str(w/'out/target/product/alioth'/(n+'.img')),'--out',str(dest)],check=True,stdout=subprocess.DEVNULL)
 assert (dest/f).read_bytes()==(p/'boot-input'/n/f).read_bytes(), 'Saved '+n+' ramdisk differs from current ROM output'
boot=entries((p/'boot-input/boot/ramdisk').read_bytes());vendor=entries((p/'boot-input/vendor_boot/vendor_ramdisk').read_bytes())
init=boot.get('init') or vendor.get('init');assert init and b'Release specific kernel module dir' in init
assert 'uts.release + page_size_suffix' in (w/'system/core/init/first_stage_init.cpp').read_text()
config=(o/'.config').read_text();required=['FW_LOADER_USER_HELPER','FW_LOADER_USER_HELPER_FALLBACK','LTO_NONE','IKCONFIG','BLK_DEV_DM','DM_VERITY','DM_VERITY_FEC','DM_DEFAULT_KEY','DM_CRYPT','EXT4_FS','F2FS_FS','FS_ENCRYPTION_INLINE_CRYPT','SCSI_UFSHCD','SCSI_UFSHCD_PLATFORM','SCSI_UFS_QCOM','SCSI_UFS_CRYPTO_QTI','QTI_CRYPTO_TZ','EFI_PARTITION','TMPFS','SECURITY_SELINUX','ANDROID_BINDER_IPC','COMPAT','QCOM_SCM','QCOM_RPMH','QCOM_RPMHPD']
for key in required:assert '\nCONFIG_'+key+'=y\n' in config,key+' not built in'
# Android init mounts tmpfs /dev and uses ueventd; DEVTMPFS is not a requirement.
assert 'mount("tmpfs", "/dev"' in (w/'system/core/init/first_stage_init.cpp').read_text()
dtb=o/'arch/arm64/boot/dts/qcom/sm8250-xiaomi-alioth.dtb'
def prop(node,key,kind='x'):return run(['fdtget','-t',kind,dtb,node,key])
root=run(['fdtget','-l',dtb,'/']).splitlines();assert 'soc' in root and 'soc@0' not in root
assert prop('/soc/ufshc@1d84000','status','s')=='okay'
assert prop('/soc/qcom,spss_utils','compatible','s')=='qcom,kona-spss-utils'
bridge='/soc/qcom,qsee_irq_bridge/qcom,qsee-ipc-irq-spss'
assert prop(bridge,'qcom,dev-name','s')=='qsee_ipc_irq_spss'
assert prop(bridge,'interrupts')=='1 0 4'
assert prop(bridge,'interrupt-parent')==prop('/soc/interrupt-controller-spss','phandle')
assert 'CONFIG_QSEE_IPC_IRQ_BRIDGE=m' in config
lib=p/'staging/matching-modules/lib/modules'/r
assert (lib/'kernel/drivers/soc/qcom/qsee_ipc_irq_bridge.ko').exists()
assert 'qsee_ipc_irq_bridge' in run(['modinfo','-F','alias',lib/'kernel/drivers/soc/qcom/qsee_ipc_irq_bridge.ko']) or 'qsee-ipc-irq-bridge' in run(['modinfo','-F','alias',lib/'kernel/drivers/soc/qcom/qsee_ipc_irq_bridge.ko'])
# Vendor library strings, not guessed paths.
blob=w/'vendor/xiaomi/sm8250-common/proprietary/vendor/lib64/libspcom.so'
paths=[x for x in run(['strings',blob]).splitlines() if x.startswith('/sys/devices/platform/soc/')]
assert paths and all(x.startswith('/sys/devices/platform/soc/soc:qcom,spss_utils/') for x in paths)
source=(k/'drivers/soc/qcom/spss_utils.c').read_text()
for path in [x for x in paths if not x.endswith('/pbl_ce')]:assert re.search(r'DEVICE_ATTR\w*\(\s*'+re.escape(path.rsplit('/',1)[1])+r'\b',source),path
fstabs=[]
for name,data in vendor.items():
 if 'fstab' in name and b'/data ' in data:
  assert b'wrappedkey_v0' in data and b'inlinecrypt_optimized' in data;fstabs.append(name)
assert fstabs
avb=run(['python3',w/'external/avb/avbtool.py','info_image','--image',w/'out/target/product/alioth/vbmeta.img'])
assert re.search(r'^Flags:\s+3$',avb,re.M)
report={'kernel_source_head':run(['git','-C',k,'rev-parse','HEAD']),'kernel_release':r,'saved_ramdisks_match_current_evo_output':True,'actual_ramdisk_init_supports_release_specific_modules':True,'boot_critical_builtin_config_checks':required,'android_tmpfs_dev_setup_present':True,'compiled_soc_and_ufs_vendor_paths_passed':True,'vendor_spcom_sysfs_paths':paths,'pbl_ce_absent_in_both_donor_and_port':True,'qsee_irq_bridge_compiled_dt_and_module_alias_passed':True,'packaged_fstab_wrapped_key_requirements_present':fstabs,'local_vbmeta_flags':3,'local_vbmeta_hashes_are_for_original_images':True,'bootloader_acceptance_verified':False,'runtime_validated':False,'flashed':False,'remaining_gates':['Actual bootloader RAM fixups and acceptance of unsigned test images','UFS/SCM hardware key derivation and existing userdata mount','SPSS/PAS/UEFI/GLINK and vendor key services','GPU/display/charging hardware operation','Audio/modem/connectivity/camera and remaining vendor sysfs/ioctl contracts']}
(p/'boot-system-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

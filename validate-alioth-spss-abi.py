#!/usr/bin/env python3
"""Compare actual donor/native SPSS ABI constants and layouts on both ARM ABIs."""
from pathlib import Path
import subprocess,re,json,tempfile
p=Path(__file__).resolve().parent
roots={'donor':p.parents[1]/'kernel/xiaomi/sm8250','native':p/'msm-kernel'}
clang=p/'toolchain/clang-r450784e/bin/clang'
constants=['SPCOM_GET_IONFD','SPCOM_SET_IONFD','SPCOM_POLL_STATE','SPSS_IOC_SET_FW_CMAC','SPSS_IOC_WAIT_FOR_EVENT','SPSS_IOC_SIGNAL_EVENT','SPSS_IOC_IS_EVENT_SIGNALED','SPCOM_CMD_RESTART_SP','SPCOM_CMD_SEND','SPCOM_CMD_SEND_MODIFIED','SPCOM_CMD_CREATE_CHANNEL','SPCOM_CMD_LOCK_ION_BUF','SPCOM_CMD_UNLOCK_ION_BUF']
structs=['spcom_user_command','spcom_send_command','spcom_user_create_channel_command','spcom_user_restart_sp_command','spcom_user_send_modified_command','spcom_ion_handle','spcom_poll_param','spss_ioc_set_fw_cmac','spss_ioc_wait_for_event','spss_ioc_signal_event','spss_ioc_is_signaled']
results={}
with tempfile.TemporaryDirectory(prefix='alioth-spss-abi-') as tmp:
 for target in ['aarch64-linux-gnu','armv7a-linux-gnueabi']:
  outputs={}
  for label,root in roots.items():
   source='#include <linux/types.h>\ntypedef __u32 uint32_t; typedef __s32 int32_t; typedef _Bool bool;\n#define __packed __attribute__((packed))\n'
   source += '#include "'+str(root/'include/uapi/linux/spcom.h')+'"\n#include "'+str(root/'include/uapi/linux/spss_utils.h')+'"\n'
   for name in constants: source+='const unsigned int abi_'+name+' = '+name+';\n'
   for name in structs: source+='const unsigned int abi_size_'+name+' = sizeof(struct '+name+');\n'
   f=Path(tmp)/(label+'.c');f.write_text(source)
   r=subprocess.run([str(clang),'--target='+target,'-I/usr/include/x86_64-linux-gnu','-S','-emit-llvm',str(f),'-o','-'],capture_output=True,text=True,check=True)
   outputs[label]=dict(re.findall(r'@(abi_\w+) = .*?constant i32 (-?\d+)',r.stdout))
  assert outputs['donor']==outputs['native'],outputs
  assert len(outputs['native'])==len(constants)+len(structs)
  results[target]=outputs['native']
report={'actual_header_abi_matches':results,'runtime_tested':False}
(p/'spss-abi-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SPSS/SPCOM ABI: 24 constants/layouts match on ARM64 and ARM32')

#!/usr/bin/env python3
from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent
release=(p/'out/alioth-config/include/config/kernel.release').read_text().strip()
boot=p/'test-images'/release/'boot.img'
cfg=subprocess.check_output(['bash',str(p/'msm-kernel/scripts/extract-ikconfig'),str(boot)])
for option in ['SECURITY_SELINUX_FORCE_PERMISSIVE','ARM64_LEGACY_IMAGE_OFFSET','PSTORE_CONSOLE','PSTORE_RAM','PRINTK_TIME','LTO_NONE']:
 assert ('CONFIG_'+option+'=y\n').encode() in cfg
assert b'CONFIG_PANIC_TIMEOUT=0\n' in cfg
assert b'CONFIG_QCOM_FORCE_WDOG_BITE_ON_PANIC=y\n' not in cfg
cmdline=next(l for l in cfg.decode().splitlines() if l.startswith('CONFIG_CMDLINE='))
dtb=p/'test-images'/release/'overlaid.dtb'
args=subprocess.check_output(['fdtget','-t','s',str(dtb),'/chosen','bootargs'],text=True).strip()
for option in ['ignore_loglevel','loglevel=8','initcall_debug','panic=0','printk.devkmsg=on','printk.always_kmsg_dump=1']:
 assert option in args and option in cmdline
r={'kernel_release':release,'actual_packaged_config_checked':True,'actual_merged_dt_bootargs_checked':True,'panic_timeout':0,'forced_panic_watchdog_bite':False,'diagnostic_arguments':args,'device_tested':False,'android_boot_verified':False}
(p/'boot-diagnostics-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

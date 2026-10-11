#!/usr/bin/env python3
from pathlib import Path
import subprocess, tempfile, json
p=Path(__file__).resolve().parent
s=(p/'msm-kernel/security/selinux/selinuxfs.c').read_text()
start=s.index('if (IS_ENABLED(CONFIG_SECURITY_SELINUX_FORCE_PERMISSIVE) && new_value)')
end=s.index('\n\n\told_value = enforcing_enabled(state);',start)
block=s[start:end]
h=(p/'msm-kernel/security/selinux/hooks.c').read_text()
start=h.index('selinux_enforcing_boot = IS_ENABLED(CONFIG_SECURITY_SELINUX_FORCE_PERMISSIVE)')
end=h.index(';',start)+1
boot=h[start:end]
cases=0
with tempfile.TemporaryDirectory() as td:
 for enabled in [0,1]:
  source='#include <assert.h>\n#define IS_ENABLED(x) '+str(enabled)+'\n#define pr_warn_once(...) ((void)0)\nint main(void) {\n'
  for value in [0,1,-1,2]:
   source+='{ int new_value='+str(value)+'; '+block+' assert(new_value=='+str(0 if enabled else int(bool(value)))+'); }\n';cases+=1
  for value in [0,1,2]:
   source+='{ unsigned long enforcing='+str(value)+'; int selinux_enforcing_boot=-1; '+boot+' assert(selinux_enforcing_boot=='+str(0 if enabled else int(bool(value)))+'); }\n';cases+=1
  source+='return 0; }\n'
  f=Path(td)/'test.c';f.write_text(source);exe=Path(td)/'test'
  subprocess.run(['cc','-Wall','-Werror',str(f),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
r={'actual_source_cases':cases,'production_option_default':'n','forced_permissive_requested':True,'runtime_verified':False}
(p/'permissive-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

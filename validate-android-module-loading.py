#!/usr/bin/env python3
"""Check the exported Android module layout without loading modules on the host."""
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile
p=Path(__file__).resolve().parent
workspace=p.parents[1]
b=workspace/'device/xiaomi/alioth/kernel-5.15/prebuilt'
d=json.loads((b/'bundle.json').read_text())
for name,sha in d['files'].items():
    assert hashlib.sha256((b/name).read_bytes()).hexdigest()==sha,name
modules={x.name:x for x in (b/'modules').glob('*.ko')}
assert len(modules)==d['modules']==206
for key in ['module_load','vendor_module_load','recovery_module_load','charger_module_load']:
    assert len(d[key])==len(set(d[key]))
    assert set(d[key])<=modules.keys()
assert set(d['vendor_module_load'])==modules.keys()
stage=Path(tempfile.mkdtemp(prefix='android-module-audit-',dir=p/'staging'))
lib=stage/'lib/modules/0.0';lib.mkdir(parents=True)
firmware={}
for name,src in modules.items():
    shutil.copy2(src,lib/name)
    magic=subprocess.check_output(['modinfo','-F','vermagic',str(src)],text=True).split()[0]
    assert magic==d['kernel_release'],(name,magic)
    fw=subprocess.check_output(['modinfo','-F','firmware',str(src)],text=True).splitlines()
    if fw: firmware[name]=fw
for name in ['modules.builtin','modules.builtin.modinfo']:
    shutil.copy2(p/'out/alioth-config'/name,lib/name)
(lib/'modules.order').write_text('\n'.join(modules)+'\n')
r=subprocess.run(['depmod','-e','-E',str(p/'staging/matching-modules/combined.symvers'),'-b',str(stage),'0.0'],capture_output=True,text=True)
assert r.returncode==0 and not (r.stdout+r.stderr).strip(),r.stdout+r.stderr
edges={}
for line in (lib/'modules.dep').read_text().splitlines():
    name,deps=line.split(':',1); edges[name]=deps.split()
assert edges.keys()==modules.keys()
for name,deps in edges.items(): assert set(deps)<=modules.keys(),(name,deps)
def closure(names):
    seen=set()
    def visit(name,active):
        assert name not in active,('dependency cycle',name)
        if name in seen: return
        for dep in edges[name]: visit(dep,active|{name})
        seen.add(name)
    for name in names: visit(name,set())
    return sorted(seen)
first=closure(d['module_load']); full=closure(d['vendor_module_load'])
rc=(workspace/'device/xiaomi/alioth/kernel-5.15/init.alioth.modules.rc').read_text()
assert 'on post-fs-data' in rc and 'exec_start vendor.alioth-modules' in rc
assert '--all=/vendor/lib/modules/modules.load' in rc
assert 'seclabel u:r:vendor_modprobe:s0' in rc
report={'kernel_release':d['kernel_release'],'module_count':len(modules),'first_stage_requested':len(d['module_load']),'first_stage_hard_dependency_closure':first,'vendor_requested':len(d['vendor_module_load']),'vendor_hard_dependency_closure_count':len(full),'flattened_depmod_crc_passed':True,'bundle_hashes_vermagic_passed':True,'declared_module_firmware':firmware,'firmware_limitation':'Dynamic firmware names and probe success require device checks. No proprietary firmware copied.','loader':'Android first-stage libmodprobe plus toolbox_vendor vendor_modprobe after post-fs-data mounts','all_modules_built_in_required':False,'android_product_build_performed':False,'runtime_module_loading_verified':False}
(p/'android-module-loading-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['first_stage_hard_dependency_closure','declared_module_firmware']}))

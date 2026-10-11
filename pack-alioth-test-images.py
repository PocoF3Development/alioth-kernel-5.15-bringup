#!/usr/bin/env python3
"""Package local experimental images, without flashing or copying vendor firmware."""
from pathlib import Path
import gzip, hashlib, json, shlex, struct, subprocess, fnmatch, os
p = Path(__file__).resolve().parent
workspace = p.parents[1]
o = p / 'out/alioth-config'
release = (o / 'include/config/kernel.release').read_text().strip()
bundle = json.loads((p / 'alioth-module-bundle-results.json').read_text())
assert bundle['kernel_release'] == release and bundle['depmod_returncode'] == 0
assert not bundle['depmod_output'].strip()
lib = p / 'staging/matching-modules/lib/modules' / release
dtb = o / 'arch/arm64/boot/dts/qcom/sm8250-xiaomi-alioth.dtb'
out = p / 'test-images' / release
out.mkdir(parents=True, exist_ok=True)
def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True).stdout
def prop(node, name):
    r = subprocess.run(['fdtget', '-t', 's', str(dtb), node, name], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''
aliases = []
for line in (lib / 'modules.alias').read_text().splitlines():
    fields = line.split()
    if len(fields) == 3 and fields[1].startswith('of:'):
        aliases.append((fields[1], fields[2]))
selected = set()
# These release drivers have OF match tables but omit MODULE_DEVICE_TABLE.
explicit_of = {'qcom,pm8150-smb5': 'qpnp_smb5_main', 'qcom,fg-gen4': 'qpnp_fg_gen4_main', 'qcom,qseecom': 'qseecom_dlkm', 'qcom,smcinvoke': 'smcinvoke_dlkm', 'qcom,tz-log': 'tz_log_dlkm', 'qcom,spcom': 'spcom'}
def visit(node, parent_enabled=True):
    enabled = parent_enabled and prop(node, 'status') in ('', 'ok', 'okay')
    if enabled:
        for compatible in prop(node, 'compatible').split():
            if compatible in explicit_of:
                selected.add(explicit_of[compatible])
            modalias = 'of:N' + node.rsplit('/', 1)[-1].split('@')[0] + 'T' + prop(node, 'device_type') + 'C' + compatible
            for pattern, module in aliases:
                if fnmatch.fnmatchcase(modalias, pattern):
                    selected.add(module)
    children = run(['fdtget', '-l', str(dtb), node]).decode().splitlines()
    for child in children:
        visit(node.rstrip('/') + '/' + child, enabled)
visit('/')
module_paths = bundle['modules']
known = {Path(path).stem.replace('-', '_'): path for path in module_paths}
assert len(known) == len(module_paths), 'Ambiguous module basename'
if 'sched_walt' in known:
    selected.add('sched_walt')
assert selected <= known.keys()
assert {'msm_kgsl', 'msm_drm', 'msm_alioth_dsi_pll', 'qpnp_smb5_main', 'qpnp_fg_gen4_main', 'qseecom_dlkm', 'smcinvoke_dlkm', 'tz_log_dlkm', 'qcom_spss', 'spss_utils', 'spcom'} <= selected, selected
load_list = [Path(path).name for path in module_paths if Path(path).stem.replace('-', '_') in selected]
# A newc archive concatenated after the existing archive preserves its metadata.
archive = bytearray()
inode = 0x100000
def append(name, mode, data=b''):
    global inode
    assert not name.startswith('/') and '..' not in Path(name).parts
    inode += 1
    fields = [inode, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(name.encode()) + 1, 0]
    archive.extend(b'070701' + ''.join(f'{x:08x}' for x in fields).encode())
    archive.extend(name.encode() + b'\0')
    archive.extend(b'\0' * (-len(archive) % 4))
    archive.extend(data)
    archive.extend(b'\0' * (-len(archive) % 4))
directories = set()
files = []
for file in sorted(lib.rglob('*')):
    if file.is_file():
        name = 'lib/modules/' + release + '/' + file.relative_to(lib).as_posix()
        files.append((name, file.read_bytes()))
        directories.update(str(parent) for parent in Path(name).parents if str(parent) != '.')
for name in sorted(directories, key=lambda x: (len(Path(x).parts), x)):
    append(name, 0o40755)
for name, data in files:
    append(name, 0o100644, data)
for name in ['modules.load', 'modules.load.recovery', 'modules.load.charger']:
    append('lib/modules/' + release + '/' + name, 0o100644, ('\n'.join(load_list) + '\n').encode())
append('TRAILER!!!', 0)
archive.extend(b'\0' * (-len(archive) % 512))
original = gzip.decompress((p / 'boot-input/vendor_boot/vendor_ramdisk').read_bytes())
ramdisk = out / 'vendor_ramdisk.gz'
ramdisk.write_bytes(gzip.compress(original + bytes(archive), compresslevel=9, mtime=0))
mkboot = workspace / 'system/tools/mkbootimg/mkbootimg.py'
bootargs = shlex.split((p / 'boot-input/boot-arguments.txt').read_text())
for flag, value in [('--kernel', o / 'arch/arm64/boot/Image'), ('--ramdisk', p / 'boot-input/boot/ramdisk')]:
    bootargs[bootargs.index(flag) + 1] = str(value)
run(['python3', str(mkboot)] + bootargs + ['--output', str(out / 'boot.img')])
# Preserve the stock wildcard base-DTB selector; the overlay restores board 44.
base_dtb = out / 'alioth-base.dtb'
base_dtb.write_bytes(dtb.read_bytes())
run(['fdtput', '-t', 'x', str(base_dtb), '/', 'qcom,board-id', '0', '0'])
vendorargs = shlex.split((p / 'boot-input/vendor_boot-arguments.txt').read_text())
for flag, value in [('--dtb', base_dtb), ('--vendor_ramdisk', ramdisk)]:
    vendorargs[vendorargs.index(flag) + 1] = str(value)
run(['python3', str(mkboot)] + vendorargs + ['--vendor_boot', str(out / 'vendor_boot.img')])
overlay = out / 'alioth-test-overlay.dts'
overlay.write_text('/dts-v1/;\n/plugin/;\n/ { qcom,board-id = <44 0>; fragment@0 { target-path = "/"; __overlay__ { qcom,board-id = <44 0>; model = "Xiaomi alioth 5.15 development boot test"; }; }; };\n')
run(['dtc', '-@', '-I', 'dts', '-O', 'dtb', '-o', str(out / 'alioth-test-overlay.dtbo'), str(overlay)])
run([str(workspace / 'out/host/linux-x86/bin/mkdtimg'), 'create', str(out / 'dtbo.img'), '--page_size=4096', '--id=0', '--rev=0', str(out / 'alioth-test-overlay.dtbo')])
run(['fdtoverlay', '-i', str(base_dtb), '-o', str(out / 'overlaid.dtb'), str(out / 'alioth-test-overlay.dtbo')])
limits = {'boot.img': 201326592, 'vendor_boot.img': 100663296, 'dtbo.img': 33554432}
images = {}
for name, limit in limits.items():
    data = (out / name).read_bytes()
    assert len(data) <= limit
    images[name] = {'size': len(data), 'partition_limit': limit, 'sha256': hashlib.sha256(data).hexdigest()}
result = {'kernel_release': release, 'images': images, 'bundled_modules': len(module_paths),
          'first_stage_modules': load_list, 'overlay_merge_passed': True, 'base_board_selector': [0, 0], 'overlay_board_selector': [44, 0],
          'flashed': False, 'boot_validated': False, 'production_ready': False,
          'charging': 'Experimental buck only, 2 A / 4.45 V with JEITA; no PD/HVDCP/charge pump',
          'limitations': 'TEE/vendor multimedia, remote processors and full device functionality remain unvalidated. Unsigned test images require bootloader/AVB compatibility assessment before use.'}
(out / 'test-image-results.json').write_text(json.dumps(result, indent=2) + '\n')
(p / 'test-image-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(str(out), flush=True)
print(json.dumps(images, indent=2), flush=True)

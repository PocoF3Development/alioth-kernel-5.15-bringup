#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,tempfile
p=Path(__file__).resolve().parent;k=p/'msm-kernel'
donor=p.parents[1]/'kernel/xiaomi/sm8250'
def run(args): return subprocess.check_output(args,text=True).strip()
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 source=(k/'drivers/dma-buf/alioth_ion_compat.c').read_text()
 a=source.index('struct alioth_secure_heap {');b=source.index('static const char *alioth_spss_heap_name',a)
 defines='\n'.join(f'#define ION_FLAG_CP_{name} (1U << {bit})' for name,bit in [('TOUCH',17),('BITSTREAM',18),('PIXEL',19),('NON_PIXEL',20),('CAMERA',21)])
 code='#include <stdint.h>\n#include <stddef.h>\n#include <assert.h>\ntypedef uint32_t u32;\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\n#define ION_FLAG_SECURE (1U<<31)\n#define ION_FLAG_ALLOW_NON_CONTIG (1U<<28)\n#define ION_FLAGS_CP_MASK 0x6FFE8000\n'+defines+'\n'+source[a:b]
 code+=r'''
int main(void) {
 unsigned int mask, extra, tests=0;
 for (mask=0; mask<32; mask++) {
  unsigned int cp=mask<<17;
  for (extra=0; extra<16; extra++) {
   unsigned int flags=cp | ((extra&1)?ION_FLAG_SECURE:0) |
    ((extra&2)?ION_FLAG_ALLOW_NON_CONTIG:0) |
    ((extra&4)?(1U<<16):0) | ((extra&8)?1:0);
   int expected=(extra&1) && !(extra&12) && mask && !(mask&(mask-1));
   assert((alioth_secure_heap_name(flags)!=NULL)==expected);tests++;
  }
 }
 for (unsigned int bit=0;bit<32;bit++) {
  unsigned int flags=ION_FLAG_SECURE|ION_FLAG_CP_PIXEL|(1U<<bit);
  int expected=(bit==19 || bit==28 || bit==31);
  assert((alioth_secure_heap_name(flags)!=NULL)==expected);tests++;
 }
 return tests==544?0:1;
}
'''
 (t/'flags.c').write_text(code);subprocess.run(['cc','-Wall','-Wextra','-Werror',str(t/'flags.c'),'-o',str(t/'flags')],check=True);subprocess.run([str(t/'flags')],check=True)
 headers=[donor/'include/uapi/linux/qseecom.h',k/'include/uapi/linux/qseecom.h']
 names=set(re.findall(r'^#define (QSEECOM_IOCTL_\w+)',headers[0].read_text(),re.M));abi=[]
 for i,h in enumerate(headers):
  assert names<=set(re.findall(r'^#define (QSEECOM_IOCTL_\w+)',h.read_text(),re.M))
  code='#include <stdint.h>\n#include <stdio.h>\n#include "'+str(h)+'"\nint main(void) {\n'
  code+='\n'.join('printf("'+n+' %lx\\n", (unsigned long)'+n+');' for n in sorted(names))+'\n}\n'
  (t/f'abi{i}.c').write_text(code);subprocess.run(['cc',str(t/f'abi{i}.c'),'-o',str(t/f'abi{i}')],check=True);abi.append(run([str(t/f'abi{i}')]))
 assert abi[0]==abi[1], 'Donor QSEE ioctl number/size mismatch'
 # Compile the real UAPI constants for both ARM pointer widths without libc.
 clang=p/'toolchain/clang-r450784e/bin/clang'
 for target in ['aarch64-linux-gnu','arm-linux-gnueabi']:
  ir=[]
  for i,h in enumerate(headers):
   code='typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;typedef unsigned long long uint64_t;typedef int int32_t;\n#include "'+str(h)+'"\n'
   code+='\n'.join('const unsigned int abi_'+n+' = '+n+';' for n in sorted(names))
   (t/'cross.c').write_text(code)
   subprocess.run([str(clang),'-target',target,'-I/usr/include/x86_64-linux-gnu','-S','-emit-llvm',str(t/'cross.c'),'-o',str(t/'cross.ll')],check=True)
   ir.append([x for x in (t/'cross.ll').read_text().splitlines() if x.startswith('@abi_')])
  assert ir[0]==ir[1], target+' QSEE ioctl ABI mismatch'

dtb=p/'out/alioth-config/arch/arm64/boot/dts/qcom/sm8250-xiaomi-alioth.dtb'
def prop(node,key,kind='x'): return run(['fdtget','-t',kind,str(dtb),node,key])
assert prop('/soc/qseecom@82400000','reg')=='0 82400000 0 3a00000'
assert prop('/soc/smcinvoke@87900000','reg')=='0 87900000 0 2200000'
assert prop('/soc/tz-log@146bf720','reg')=='0 146bf720 0 3000'
for key,region in [('qseecom_mem','alioth-qseecom-cma'),('qseecom_ta_mem','alioth-qseecom-ta-cma'),('user_contig_mem','alioth-user-contig-cma')]:
 assert prop('/soc/qseecom@82400000',key)==prop('/reserved-memory/'+region,'phandle')
assert prop('/soc/qseecom@82400000','qcom,qsee-reentrancy-support')=='2'
assert prop('/reserved-memory/alioth-secure-display-cma','size')=='0 a400000'
assert prop('/dma-heaps/alioth-secure-display','qcom,token')=='2000000'
assert prop('/dma-heaps/alioth-secure-display','memory-region')==prop('/reserved-memory/alioth-secure-display-cma','phandle')
result={'kernel_head':run(['git','-C',str(k),'rev-parse','HEAD']),'secure_flag_cases_passed':544,'qsee_donor_ioctl_number_and_size_matches':len(names),'qsee_checked_abis':['arm64','arm32'],'compiled_dt_resources_and_three_shmbridge_regions_passed':True,'runtime_validated':False}
(p/'trustzone-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

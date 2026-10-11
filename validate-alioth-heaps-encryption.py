#!/usr/bin/env python3
"""Host tests of actual heap selectors and ICE/SCM functions; services mocked."""
from pathlib import Path
import subprocess,tempfile,json,re
p=Path(__file__).resolve().parent;k=p/'msm-kernel'
def function(source,name):
 pos=source.index(name+'(');start=source.rfind('\n',0,pos)+1;brace=source.index('{',pos);depth=1;i=brace+1
 while depth:
  depth+=(source[i]=='{')-(source[i]=='}');i+=1
 return source[start:i]
ion=(k/'drivers/dma-buf/alioth_ion_compat.c').read_text()
for name,val in [('ALIOTH_ION_SYSTEM_SECURE',7),('ALIOTH_ION_HYP_CMA',8),('ALIOTH_ION_SECURE_CARVEOUT',9),('ALIOTH_ION_CAMERA',10)]:
 assert int(re.search(r'^#define '+name+r'\s+(\d+)',ion,re.M).group(1))==val
code=r"""
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
#include <stdio.h>
typedef uint32_t u32; typedef unsigned char u8;
#define ION_FLAG_CP_CDSP (1U<<29)
#define ION_FLAG_SECURE (1U<<31)
#define ALIOTH_ION_CACHED 1
#define BLK_CRYPTO_MAX_WRAPPED_KEY_SIZE 128
#define ARRAY_SIZE(a) (sizeof(a)/sizeof(a[0]))
#define __cpu_to_be32s(p) (*(p)=__builtin_bswap32(*(p)))
#define pr_err(...) ((void)0)
#define EXPORT_SYMBOL(x)
struct ice_mmio_data {int unused;};
struct blk_crypto_key { unsigned int size; unsigned char raw[128]; struct {int is_hw_wrapped;} crypto_cfg;};
struct qtee_shm {void *vaddr; uintptr_t paddr; size_t size;};
static int allocations,frees,fail_allocation,scm_error,scm_calls;static unsigned char captured[128];static unsigned captured_size;
static void memzero_explicit(void *p,size_t n){memset(p,0,n);}
static int qtee_shmbridge_allocate_shm(size_t n,struct qtee_shm *s){allocations++;if(allocations==fail_allocation)return -ENOMEM;s->vaddr=malloc(n);assert(s->vaddr);memset(s->vaddr,0xa5,n);s->paddr=(uintptr_t)s->vaddr;s->size=n;return 0;}
static void qtee_shmbridge_flush_shm_buf(struct qtee_shm *s){(void)s;}
static void qtee_shmbridge_inv_shm_buf(struct qtee_shm *s){(void)s;}
static void qtee_shmbridge_free_shm(struct qtee_shm *s){frees++;for(size_t i=0;i<s->size;i++)assert(((unsigned char*)s->vaddr)[i]==0);free(s->vaddr);}
static int qcom_scm_config_set_ice_key(int slot,uintptr_t addr,unsigned int size,int mode,unsigned int mask,int type){(void)slot;(void)mode;(void)mask;(void)type;scm_calls++;captured_size=size;memcpy(captured,(void*)addr,size);return scm_error;}
static int qcom_scm_derive_raw_secret(uintptr_t key,unsigned int n,uintptr_t secret,unsigned int size){(void)key;(void)n;scm_calls++;memset((void*)secret,0x42,size);return scm_error;}
static void reset(void){allocations=frees=fail_allocation=scm_error=scm_calls=0;}
"""
code+=function(ion,'alioth_cdsp_heap_name')+'\n'
code+='#define BIT(x) (1U << (x))\nstruct ion_heap_data {const char *name; unsigned int type,heap_id;};\n'
a=ion.index('struct alioth_ion_heap {');b=ion.index('struct alioth_secure_heap {',a)
code+='#define ION_HEAP_TYPE_SYSTEM 0\n#define ION_HEAP_TYPE_DMA 4\n#define ALIOTH_ION_CAMERA 10\n'+ion[a:b]+function(ion,'alioth_nonsecure_heap_name')+'\n' 
src=(k/'drivers/soc/qcom/crypto-qti-tz.c').read_text();code+='#define ICE_CIPHER_MODE_XTS_256 3\n'+function(src,'crypto_qti_program_key')+'\n'+function(src,'crypto_qti_derive_raw_secret_platform')
qsee=(p/'sources/vendor/qcom/opensource/securemsm-kernel/qseecom/qseecom.c').read_text()
a=qsee.index('case QSEECOM_IOCTL_SET_ICE_INFO:');b=qsee.index('\n\tdefault:',a)
code+='\n#define CONFIG_MACH_XIAOMI_ALIOTH 1\n#define QSEECOM_IOCTL_SET_ICE_INFO 1\n#define QSEECOM_IOCTL_FBE_CLEAR_KEY 2\nstruct qseecom_ice_data_t {int flag;};\nstruct qseecom_ice_key_data_t {uintptr_t key,salt;unsigned int key_len,salt_len;};\nstatic int copy_fault;\nstatic int copy_from_user(void *dst,const void *src,size_t n){if(copy_fault)return 1;memcpy(dst,src,n);return 0;}\nstatic int ice_ioctl(unsigned int cmd,void *argp){switch(cmd){\n'+qsee[a:b]+'\ndefault:return -EINVAL;}}\n'
code+=r"""
int main(void){
 struct qseecom_ice_data_t ice={0};struct qseecom_ice_key_data_t clear={0};
 assert(!ice_ioctl(QSEECOM_IOCTL_SET_ICE_INFO,&ice));
 assert(ice_ioctl(QSEECOM_IOCTL_FBE_CLEAR_KEY,&clear)==-ENODEV);
 copy_fault=1;assert(ice_ioctl(QSEECOM_IOCTL_SET_ICE_INFO,NULL)==-EFAULT);assert(ice_ioctl(QSEECOM_IOCTL_FBE_CLEAR_KEY,NULL)==-EFAULT);copy_fault=0;
 for(unsigned int bit=0;bit<32;bit++) {
  assert((alioth_nonsecure_heap_name(BIT(20),BIT(bit))!=NULL)==(bit==0));
  assert((alioth_nonsecure_heap_name(BIT(20)|BIT(bit),0)!=NULL)==(bit==20||bit==25));
 }
 assert(!strcmp(alioth_nonsecure_heap_name(BIT(20),1),"qcom,system"));
 assert(!strcmp(alioth_nonsecure_heap_name(BIT(20),0),"qcom,system-uncached"));
 assert(!strcmp(alioth_nonsecure_heap_name(BIT(20)|BIT(25),1),"qcom,system"));
 for(unsigned int flags=0;flags<4;flags++)assert(alioth_cdsp_heap_name((1U<<29)|((flags&1)?1:0)|((flags&2)?(1U<<31):0)));
 for(unsigned int bit=0;bit<32;bit++)assert((alioth_cdsp_heap_name((1U<<29)|(1U<<bit))!=NULL)==(bit==0||bit==29||bit==31));
 struct blk_crypto_key key={.size=64};for(unsigned i=0;i<64;i++)key.raw[i]=i;
 reset();assert(!crypto_qti_program_key(NULL,&key,2,8,0,0));assert(allocations==1&&frees==1&&scm_calls==1&&captured[0]==3&&captured[3]==0);
 reset();key.crypto_cfg.is_hw_wrapped=1;key.size=80;assert(!crypto_qti_program_key(NULL,&key,2,8,0,0));assert(!memcmp(captured,key.raw,80)&&frees==1);
 reset();fail_allocation=1;assert(crypto_qti_program_key(NULL,&key,0,0,0,0)==-ENOMEM&&frees==0&&scm_calls==0);
 reset();scm_error=-EIO;assert(crypto_qti_program_key(NULL,&key,0,0,0,0)==-EIO&&frees==1);
 reset();key.size=129;assert(crypto_qti_program_key(NULL,&key,0,0,0,0)==-EINVAL&&allocations==0);
 unsigned char wrapped[80]={0},secret[32];
 reset();fail_allocation=2;assert(crypto_qti_derive_raw_secret_platform(wrapped,80,secret,32)==-ENOMEM&&frees==1&&scm_calls==0);
 reset();scm_error=-EIO;memset(secret,0x77,32);assert(crypto_qti_derive_raw_secret_platform(wrapped,80,secret,32)==-EIO&&frees==2);for(unsigned i=0;i<32;i++)assert(secret[i]==0x77);
 reset();assert(!crypto_qti_derive_raw_secret_platform(wrapped,80,secret,32)&&frees==2);for(unsigned i=0;i<32;i++)assert(secret[i]==0x42);
 reset();assert(crypto_qti_derive_raw_secret_platform(wrapped,0,secret,32)==-EINVAL&&allocations==0);
 return 0;
}
"""
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/'test.c';f.write_text(code);subprocess.run(['cc','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-sign-compare',str(f),'-o',str(f.with_suffix(''))],check=True);subprocess.run([str(f.with_suffix(''))],check=True)
def prop(node,key,kind='x'):return subprocess.check_output(['fdtget','-t',kind,str(p/'out/alioth-config/arch/arm64/boot/dts/qcom/sm8250-xiaomi-alioth.dtb'),node,key],text=True).strip()
assert prop('/dma-heaps/alioth-cdsp-secure','qcom,token')=='20000000'
assert prop('/dma-heaps/alioth-cdsp-secure','qcom,dma-heap-type')=='0'
# Locate the fixed donor region independently from the heap's phandle.
assert prop('/dma-heaps/alioth-cdsp-secure','memory-region')==prop('/reserved-memory/memory@8bf00000','phandle')
assert prop('/reserved-memory/memory@8bf00000','reg')=='0 8e100000 0 4600000'
result={'kernel_source_head':subprocess.check_output(['git','-C',str(k),'rev-parse','HEAD'],text=True).strip(),'actual_functions_extracted':True,'heap14_flag_cases_passed':36,'camera_flag_and_mask_cases_passed':67,'donor_heap_query_types_passed':True,'crypto_host_cases_passed':9,'wrapped_bytes_and_raw_word_order_passed':True,'allocation_failures_and_scm_errors_passed':True,'failed_derive_does_not_copy_secret':True,'compiled_cdsp_dt_passed':True,'qsee_donor_error_cases_passed':4,'shared_key_material_zeroed_before_free':True,'scm_mocked':True,'runtime_validated':False}
(p/'heaps-encryption-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

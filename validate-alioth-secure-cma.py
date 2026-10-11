#!/usr/bin/env python3
"""Exercise actual protected/shared CMA wrapper with assignment fault injection."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).resolve().parent
s=(p/'msm-kernel/drivers/dma-buf/heaps/qcom_cma_heap.c').read_text()
a=s.index('static struct dma_buf *secure_cma_heap_allocate');b=s.index('static const struct dma_heap_ops secure_cma_heap_ops',a)
stubs=r"""
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#define PERM_READ 4
#define PERM_WRITE 2
#define VMID_HLOS 3
#define VMID_CP_SEC_DISPLAY 16
#define VMID_CP_SPSS_HLOS_SHARED 36
#define ERR_PTR(x) ((void *)(intptr_t)(x))
#define IS_ERR(x) ((uintptr_t)(x) >= (uintptr_t)-4095)
struct dma_heap {int unused;}; struct dma_buf {int unused;};
struct cma_heap {int secure_vmid;bool explicit_hlos;};
struct mem_buf_lend_kernel_arg {unsigned int nr_acl_entries;int *vmids,*perms;};
static struct cma_heap cma;static struct dma_buf buffer;
static int alloc_error,assign_error,lends,shares,puts;
static void *dma_heap_get_drvdata(struct dma_heap *h) {(void)h;return &cma;}
static int msm_secure_get_vmid_perms(int vmid) {return vmid==16?4:6;}
static struct dma_buf *cma_heap_allocate(struct dma_heap *h,unsigned long len,unsigned long fd,unsigned long flags) {
 (void)h;assert(len==4096&&fd==7&&flags==0);return alloc_error?ERR_PTR(alloc_error):&buffer;
}
static int mem_buf_lend(struct dma_buf *b,struct mem_buf_lend_kernel_arg *a) {
 assert(b==&buffer&&a->nr_acl_entries==1&&a->vmids[0]==16&&a->perms[0]==4);lends++;return assign_error;
}
static int mem_buf_share(struct dma_buf *b,struct mem_buf_lend_kernel_arg *a) {
 assert(b==&buffer&&a->nr_acl_entries==(cma.explicit_hlos?2:1)&&a->vmids[0]==36&&a->perms[0]==6);
 if(cma.explicit_hlos)assert(a->vmids[1]==3&&a->perms[1]==6);
 shares++;return assign_error;
}
static void dma_buf_put(struct dma_buf *b) {assert(b==&buffer);puts++;}
"""
tests=r"""
int main(void) {
 struct dma_heap heap;int mode;
 for(mode=0;mode<3;mode++) {
  cma.secure_vmid=mode?36:16;cma.explicit_hlos=mode==2;
  alloc_error=-12;assign_error=lends=shares=puts=0;
  assert(secure_cma_heap_allocate(&heap,4096,7,0)==ERR_PTR(-12)&&!lends&&!shares&&!puts);
  alloc_error=0;assign_error=-5;
  assert(secure_cma_heap_allocate(&heap,4096,7,0)==ERR_PTR(-5)&&(lends+shares)==1&&puts==1);
  assign_error=-99;
  assert(secure_cma_heap_allocate(&heap,4096,7,0)==ERR_PTR(-99)&&(lends+shares)==2&&puts==2);
  assign_error=0;
  assert(secure_cma_heap_allocate(&heap,4096,7,0)==&buffer&&(lends+shares)==3&&puts==2);
 }
 return 0;
}
"""
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);(t/'test.c').write_text(stubs+s[a:b]+tests)
 subprocess.run(['cc','-Wall','-Wextra','-Werror',str(t/'test.c'),'-o',str(t/'test')],check=True)
 subprocess.run([str(t/'test')],check=True)
result={'actual_wrapper_host_fault_cases_passed':12,'secure_display_read_only_acl_passed':True,'spss_composite_and_explicit_hlos_rw_acl_passed':True,'input_forwarding_and_failure_release_passed':True,'runtime_hyp_assign_validated':False}
(p/'secure-cma-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

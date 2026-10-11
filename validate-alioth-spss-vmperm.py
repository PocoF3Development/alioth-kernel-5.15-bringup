#!/usr/bin/env python3
"""Test actual composite-VMID ACL and mapping logic with mocked hypervisor calls."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).resolve().parent
source=(p/'msm-kernel/drivers/soc/qcom/mem_buf/mem_buf_dma_buf.c').read_text()
def function(name):
 start=source.index(name+'(');start=source.rfind('\n',0,start)+1
 brace=source.index('{',start);depth=1;end=brace+1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]+'\n'
code=''.join(function(x) for x in ['mem_buf_vmid_is_local','mem_buf_vmperm_update_state','validate_lend_vmids','validate_lend_mapcount','mem_buf_share'])
stubs=r"""
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
typedef uint32_t u32;
#define VMID_HLOS 3
#define VMID_CP_SPSS_HLOS_SHARED 36
#define PERM_READ 4
#define PERM_WRITE 2
#define PERM_EXEC 1
#define GH_RM_TRANS_TYPE_LEND 1
#define GH_RM_TRANS_TYPE_SHARE 2
#define GFP_KERNEL 0
#define WARN_ON(x) assert(!(x))
#define pr_err_ratelimited(...) ((void)0)
#define kmalloc_array(n,s,g) malloc((n)*(s))
#define kfree free
static int current_vmid=3;
struct mem_buf_vmperm {int *vmids,*perms;u32 nr_acl_entries,max_acl_entries,mapcount;int current_vm_perms;};
struct dma_buf {int unused;};
struct mem_buf_lend_kernel_arg {int nr_acl_entries;int *vmids,*perms;};
static int calls,seen_nr,seen_vmids[3],seen_perms[3];
static int mem_buf_lend_internal(struct dma_buf *b,struct mem_buf_lend_kernel_arg *a,u32 op) {
 (void)b;assert(op==2);calls++;seen_nr=a->nr_acl_entries;
 memcpy(seen_vmids,a->vmids,a->nr_acl_entries*sizeof(int));memcpy(seen_perms,a->perms,a->nr_acl_entries*sizeof(int));return -5;
}
"""
tests=r"""
int main(void) {
 int vmids[2]={36,3},perms[2]={6,6},stored_v[3],stored_p[3];
 struct mem_buf_vmperm v={stored_v,stored_p,0,3,1,0};
 struct mem_buf_lend_kernel_arg a={1,vmids,perms};struct dma_buf b;
 bool alias;
#ifdef CONFIG_MACH_XIAOMI_ALIOTH
 alias=true;
#else
 alias=false;
#endif
 assert(mem_buf_vmid_is_local(3));assert(mem_buf_vmid_is_local(36)==alias);assert(!mem_buf_vmid_is_local(16));
 mem_buf_vmperm_update_state(&v,vmids,perms,1);assert(v.current_vm_perms==(alias?6:0));
 assert(validate_lend_mapcount(&v,&a)==alias);
 assert(validate_lend_vmids(&a,2)==(alias?0:-EINVAL));assert(validate_lend_vmids(&a,1)==(alias?-EINVAL:0));
 assert(mem_buf_share(&b,&a)==-5);assert(calls==1&&seen_nr==(alias?1:2)&&seen_vmids[0]==36&&seen_perms[0]==6);
 assert(a.nr_acl_entries==1&&a.vmids==vmids&&a.perms==perms);
 if(!alias)assert(seen_vmids[1]==3&&seen_perms[1]==7);
 a.nr_acl_entries=2;assert(mem_buf_share(&b,&a)==-5);assert(seen_nr==2&&seen_vmids[1]==3&&seen_perms[1]==6);
 a.nr_acl_entries=1;perms[0]=4;mem_buf_vmperm_update_state(&v,vmids,perms,1);assert(v.current_vm_perms==(alias?4:0));assert(!validate_lend_mapcount(&v,&a));
 vmids[0]=16;mem_buf_vmperm_update_state(&v,vmids,perms,1);assert(!v.current_vm_perms);
 current_vmid=4;vmids[0]=36;mem_buf_vmperm_update_state(&v,vmids,perms,1);assert(!v.current_vm_perms&&!mem_buf_vmid_is_local(36));
 return 0;
}
"""
with tempfile.TemporaryDirectory(prefix='alioth-vmperm-') as tmp:
 t=Path(tmp);(t/'test.c').write_text(stubs+code+tests)
 for flags in [[],['-DCONFIG_MACH_XIAOMI_ALIOTH']]:
  subprocess.run(['cc','-Wall','-Wextra','-Werror','-Wno-sign-compare']+flags+[str(t/'test.c'),'-o',str(t/'test')],check=True)
  subprocess.run([str(t/'test')],check=True)
report={'actual_functions_extracted':True,'alioth_and_other_platform_modes_passed':True,'composite_acl_not_expanded':True,'explicit_hlos_rw_preserved':True,'private_vm_mapping_denied':True,'non_hlos_vm_alias_denied':True,'read_only_acl_cannot_pin_for_rw':True,'runtime_hypervisor_tested':False}
(p/'spss-vmperm-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

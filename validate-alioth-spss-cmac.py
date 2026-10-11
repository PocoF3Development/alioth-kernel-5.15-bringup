#!/usr/bin/env python3
"""Exercise actual legacy SPSS CMAC ioctl case with mocked MMIO/services."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).resolve().parent
source=(p/'msm-kernel/drivers/soc/qcom/spss_utils.c').read_text()
a=source.index(' case SPSS_IOC_SET_FW_CMAC:');b=source.index('\n\tcase SPSS_IOC_SET_FW_AND_APPS_CMAC:',a)
case=source[a:b]
c=r"""
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#define __packed __attribute__((packed))
#include "HEADER"
#define CMAC_MEM_SIZE 4096
static bool kona_spss,is_iar_active,fail_map;
static void *cmac_mem;
static unsigned long cmac_mem_addr;
static uint32_t saved_fw_cmac[4],saved_apps_cmac[8][4];
static int fw_error,apps_error,gets;
static void *ioremap(unsigned long addr,size_t size) {assert(size==4096);return fail_map?0:(void*)1;}
static int spss_set_saved_fw_cmac(uint32_t *data,size_t size) {assert(size==16);return fw_error;}
static int spss_set_saved_uefi_apps_cmac(void) {return apps_error;}
static int spss_get_fw_calc_cmac(void) {gets++;return 0;}
static int spss_get_apps_calc_cmac(void) {gets++;return 0;}
static int handle(unsigned cmd,void *req,size_t size) {int ret;switch(cmd) {CASE default:return -EINVAL;}return 0;}
static void reset(void) {kona_spss=true;is_iar_active=false;fail_map=false;cmac_mem=0;fw_error=apps_error=gets=0;memset(saved_fw_cmac,0,sizeof(saved_fw_cmac));memset(saved_apps_cmac,0xa5,sizeof(saved_apps_cmac));}
int main(void) {
 struct spss_ioc_set_fw_cmac req; unsigned i,j;
 for(i=0;i<4;i++)req.cmac[i]=i+100;
 for(i=0;i<3;i++)for(j=0;j<4;j++)req.apps_cmac[i][j]=1000+i*100+j;
 reset();kona_spss=false;assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req))==-EINVAL);assert(!is_iar_active);
 reset();assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req)-1)==-EINVAL);assert(!is_iar_active);
 reset();fail_map=true;assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req))==-ENOMEM);assert(!is_iar_active);
 reset();fw_error=-EIO;assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req))==-EIO);assert(!is_iar_active);
 reset();apps_error=-EIO;assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req))==-EIO);assert(!is_iar_active);
 reset();assert(handle(SPSS_IOC_SET_FW_CMAC,&req,sizeof(req))==0);assert(is_iar_active && gets==2);
 assert(!memcmp(saved_fw_cmac,req.cmac,16));assert(!memcmp(saved_apps_cmac,req.apps_cmac,48));
 for(i=3;i<8;i++)for(j=0;j<4;j++)assert(saved_apps_cmac[i][j]==0);
 return 0;
}
"""
c=c.replace('HEADER',str(p/'msm-kernel/include/uapi/linux/spss_utils.h')).replace('CASE',case)
with tempfile.TemporaryDirectory(prefix='alioth-cmac-') as tmp:
 f=Path(tmp)/'test.c';f.write_text(c);exe=Path(tmp)/'test'
 subprocess.run(['gcc',str(f),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
report={'actual_case_extracted_from_source':True,'host_cases_passed':6,'three_app_layout_and_unused_slots_checked':True,'mmio_and_services_mocked':True,'runtime_tested':False}
(p/'spss-cmac-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

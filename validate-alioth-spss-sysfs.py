#!/usr/bin/env python3
"""Exercise actual Kona vendor CMAC sysfs functions with patterned MMIO."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).resolve().parent
source=(p/'msm-kernel/drivers/soc/qcom/spss_utils.c').read_text()
def func(name):
 a=source.index('static ssize_t '+name);b=source.index('\nstatic DEVICE_ATTR',a);return source[a:b]
c=r"""
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#include <stdarg.h>
typedef uint32_t u32;typedef uint8_t u8;
#define __iomem
#define CMAC_SIZE_IN_BYTES 16
#define CMAC_SIZE_IN_DWORDS 4
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
struct device {int unused;};struct device_attribute {int unused;};
static void *cmac_mem;
static u32 readl_relaxed(void *addr) {u32 v;memcpy(&v,addr,4);return v;}
static int sysfs_emit(char *buf,const char *fmt,...) {va_list args;va_start(args,fmt);int n=vsnprintf(buf,4096,fmt,args);va_end(args);return n;}
FUNCTIONS
int main(void) {
 char buf[4096];u32 mmio[1024];unsigned i,j;
 assert(pbl_cmac_show(0,0,buf)==-EFAULT);assert(apps_cmac_show(0,0,buf)==-EFAULT);
 for(i=0;i<1024;i++) { mmio[i]=0x12340000+i; }
 cmac_mem=mmio;
 assert(pbl_cmac_show(0,0,buf)==44);assert(!strcmp(buf,"0x12340004,0x12340005,0x12340006,0x12340007\n"));
 memset(buf,0xa5,sizeof(buf));assert(apps_cmac_show(0,0,buf)==48);
 for(j=0;j<3;j++)for(i=0;i<4;i++){u32 v;memcpy(&v,buf+(j*4+i)*4,4);assert(v==mmio[(3+2*j)*4+i]);}
 assert((unsigned char)buf[48]==0xa5);return 0;
}
"""
c=c.replace('FUNCTIONS',func('pbl_cmac_show')+'\n'+func('apps_cmac_show'))
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'test.c';f.write_text(c);exe=Path(d)/'test'
 subprocess.run(['cc','-Wall','-Wextra','-Wno-unused-parameter','-Wno-sign-compare',str(f),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
report={'actual_source_functions_exercised':True,'cases':['unmapped PBL returns EFAULT','unmapped apps returns EFAULT','PBL exact text format and offset','three apps exact binary format, interleaved saved slots skipped, no extra bytes'],'mmio_mocked':True,'runtime_validated':False}
(p/'spss-sysfs-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

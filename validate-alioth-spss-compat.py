#!/usr/bin/env python3
"""Test actual heap-13 flag resolver and Kona revision firmware selector."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).resolve().parent;k=p/'msm-kernel'
def extract(source,name):
 start=source.index(name+'(');start=source.rfind('\n',0,start)+1
 brace=source.index('{',start);depth=1;end=brace+1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]+'\n'
flags=extract((k/'drivers/dma-buf/alioth_ion_compat.c').read_text(),'alioth_spss_heap_name')
fw=extract((k/'drivers/soc/qcom/spss_utils.c').read_text(),'spss_kona_firmware_names')
c=r"""
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
typedef uint32_t u32;
#define ION_FLAG_CP_SPSS_HLOS_SHARED (1U<<30)
#define ION_FLAG_CP_HLOS (1U<<22)
#define ION_FLAG_SECURE (1U<<31)
#define ALIOTH_ION_CACHED 1U
#define EPROBE_DEFER 517
struct device_node {int unused;};
struct soc_device_attribute {const char *soc_id,*revision;};
static const char *dev_firmware_name,*test_firmware_name,*prod_firmware_name;
static int id=356,ready=1,prop_error,prop_calls;
static const char *revision="1.0";
static int socinfo_get_id(void) {return id;}
static const struct soc_device_attribute *soc_device_match(const struct soc_device_attribute *m) {
 if(!ready||id!=356)return 0;
 if(!m->revision || m->revision[0]==revision[0])return m;
 return 0;
}
static int of_property_read_string(struct device_node *n,const char *key,const char **out) {
 (void)n;prop_calls++;if(prop_error)return -5;
 if(!strcmp(key,"qcom,spss-v2-dev-firmware-name"))*out="spss2d";
 else if(!strcmp(key,"qcom,spss-v2-test-firmware-name"))*out="spss2t";
 else if(!strcmp(key,"qcom,spss-v2-prod-firmware-name"))*out="spss2p";
 else assert(0);
 return 0;
}
"""
tests=r"""
int main(void) {
 unsigned allowed=(1U<<30)|(1U<<22)|(1U<<31)|1U;unsigned mask,bit;struct device_node n;
 for(mask=0;mask<8;mask++) {
  unsigned f=(1U<<30)|((mask&1)?1U:0)|((mask&2)?1U<<22:0)|((mask&4)?1U<<31:0);
  const char *want=(mask&2)?((mask&1)?"qcom,alioth-spss-hlos":"qcom,alioth-spss-hlos-uncached"):((mask&1)?"qcom,alioth-spss":"qcom,alioth-spss-uncached");
  assert(!strcmp(alioth_spss_heap_name(f),want));assert(!alioth_spss_heap_name(f&~(1U<<30)));
  for(bit=0;bit<32;bit++)if(!(allowed&(1U<<bit)))assert(!alioth_spss_heap_name(f|(1U<<bit)));
 }
 id=0;assert(spss_kona_firmware_names(&n)==-517);id=356;ready=0;assert(spss_kona_firmware_names(&n)==-517);ready=1;
 dev_firmware_name="spss1d";test_firmware_name="spss1t";prod_firmware_name="spss1p";
 assert(!spss_kona_firmware_names(&n)&&!prop_calls&&!strcmp(prod_firmware_name,"spss1p"));
 revision="2.0";assert(!spss_kona_firmware_names(&n)&&prop_calls==3&&!strcmp(dev_firmware_name,"spss2d")&&!strcmp(test_firmware_name,"spss2t")&&!strcmp(prod_firmware_name,"spss2p"));
 revision="2.1";assert(!spss_kona_firmware_names(&n)&&prop_calls==6);
 revision="3.0";assert(spss_kona_firmware_names(&n)==-EOPNOTSUPP&&prop_calls==6);
 revision="2.1";prop_error=1;assert(spss_kona_firmware_names(&n)==-5);
 return 0;
}
"""
with tempfile.TemporaryDirectory(prefix='alioth-spss-compat-') as tmp:
 t=Path(tmp);(t/'test.c').write_text(c+flags+fw+tests)
 subprocess.run(['cc','-Wall','-Wextra','-Werror',str(t/'test.c'),'-o',str(t/'test')],check=True)
 subprocess.run([str(t/'test')],check=True)
report={'actual_helpers_extracted':True,'heap13_flag_cases_passed':240,'firmware_revision_cases_passed':7,'soc_and_dt_access_mocked':True,'runtime_tested':False}
(p/'spss-compat-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

#!/usr/bin/env python3
"""Validate the compiled Kona SPSS resources and reserved-memory bounds."""
from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent
dt=p/'out/alioth-config/arch/arm64/boot/dts/qcom/sm8250-xiaomi-alioth.dtb'
def val(node,key,typ='x'):
 return subprocess.check_output(['fdtget','-t',typ,str(dt),node,key],text=True).strip()
def cells(node,key): return [int(x,16) for x in val(node,key).split()]
base='/soc@0';sp=base+'/remoteproc@188101c';ut=base+'/spss-utils'
assert cells(sp,'reg')==[0,0x188101c,0,4,0,0x1881024,0,4,0,0x1881028,0,4,0,0x188103c,0,4,0,0x188200c,0,12]
assert cells(base+'/mailbox@188501c','reg')==[0,0x188501c,0,4]
assert cells(base+'/interrupt-controller-spss','interrupts')==[0,348,4,0,349,4]
assert cells(sp,'interrupts')==[0,352,1]
assert cells(sp,'qcom,spss-scsr-bits')==[24,25]
assert cells(ut,'qcom,spss-fuse1-addr')==cells(ut,'qcom,spss-fuse2-addr')==[0x780234]
assert cells(ut,'qcom,spss-fuse1-bit')==[27] and cells(ut,'qcom,spss-fuse2-bit')==[26]
assert [val(ut,'qcom,spss-'+x+'-firmware-name','s') for x in ['dev','test','prod']]==['spss1d','spss1t','spss1p']
assert cells(ut,'qcom,spss-debug-reg-addr')==[0x1886020]
assert cells(ut,'qcom,rproc-handle')==cells(sp,'phandle')
memph=cells(sp,'memory-region')
assert cells(ut,'pil-mem')==memph
nodes=subprocess.check_output(['fdtget','-l',str(dt),'/reserved-memory'],text=True).split()
mem=None
for node in nodes:
 path='/reserved-memory/'+node
 r=subprocess.run(['fdtget','-t','x',str(dt),path,'phandle'],capture_output=True,text=True)
 if r.returncode==0 and [int(x,16) for x in r.stdout.split()]==memph:mem=path
assert mem
reg=cells(mem,'reg');assert reg==[0,0x8e000000,0,0x100000]
pil=cells(ut,'qcom,pil-size')[0];assert pil==0xf0000 and pil+4096<=reg[3]
assert val(base+'/secure-buffer','compatible','s') == 'qcom,secure-buffer'
assert [val(ut,'qcom,spss-v2-'+x+'-firmware-name','s') for x in ['dev','test','prod']]==['spss2d','spss2t','spss2p']
shared='/reserved-memory/alioth-spss-cma'
assert val(shared,'compatible','s')=='shared-dma-pool'
assert cells(shared,'size')==[0,0x1000000]
assert cells(shared,'alignment')==[0,0x400000]
assert cells(shared,'alloc-ranges')==[0,0,0,0xffffffff]
for name,token,uncached in [('alioth-spss',0x40000000,False),('alioth-spss-uncached',0x40000000,True),('alioth-spss-hlos',0x40400000,False),('alioth-spss-hlos-uncached',0x40400000,True)]:
 node='/dma-heaps/'+name
 assert val(node,'qcom,dma-heap-name','s')=='qcom,'+name
 assert cells(node,'memory-region')==cells(shared,'phandle')
 assert cells(node,'qcom,token')==[token] and cells(node,'qcom,dma-heap-type')==[2]
 props=subprocess.check_output(['fdtget','-p',str(dt),node],text=True).split()
 assert ('qcom,uncached-heap' in props)==uncached
report={'compiled_dt_passed':True,'pil_region':[reg[1],reg[3]],'payload_size':pil,'iar_scratch':[reg[1]+pil,4096],'cmac_inside_reserved_region':True,'heap13_pool_and_four_exporters_passed':True,'secure_buffer_provider_present':True,'v2_firmware_properties_passed':True,'runtime_tested':False,'flashed':False}
(p/'spss-dt-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

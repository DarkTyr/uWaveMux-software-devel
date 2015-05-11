'''
Example script on how to use the dram class
'''
cd ~/Documents/uWaveMux-software-devel/examples/dram/
import time
from corr import katcp_wrapper

import tenGbEthernet
import dram
roach2 = katcp_wrapper.FpgaClient('192.168.0.136', 7147)
Dram = dram.DRAM(roach2)  

while (not roach2.is_connected()):
    time.sleep(1)

roach2.progdev('wip_dram.bof')

#initial simple write with readback
Dram.dac_I = range(2**8)
Dram.dac_Q = range(2**8)

lut_bin = []
lut_bin = Dram.createLUTs()
Dram.writeLUTs(lut_bin)

addr, reg8, reg7, reg6, reg5, reg4, reg3, reg2, reg1, reg0 = dram.regReadLUT(512)

for x in range(len(reg7)):
    print addr[x], '   ',
    print (reg8[x] & 0xFFFF0000) >> 16, (reg8[x] & 0x000FFFF) >> 00,'  ',
    print (reg7[x] & 0xFFFF0000) >> 16, (reg7[x] & 0x000FFFF) >> 00,'  ',
    print (reg6[x] & 0xFFFF0000) >> 16, (reg6[x] & 0x000FFFF) >> 00,'  ',
    print (reg5[x] & 0xFFFF0000) >> 16, (reg5[x] & 0x000FFFF) >> 00,'  ',
    print (reg4[x] & 0xFFFF0000) >> 16, (reg4[x] & 0x000FFFF) >> 00,'  ',
    print (reg3[x] & 0xFFFF0000) >> 16, (reg3[x] & 0x000FFFF) >> 00,'  ',
    print (reg2[x] & 0xFFFF0000) >> 16, (reg2[x] & 0x000FFFF) >> 00,'  ',
    print (reg1[x] & 0xFFFF0000) >> 16, (reg1[x] & 0x000FFFF) >> 00,'  ',
    print (reg0[x] & 0xFFFF0000) >> 16, (reg0[x] & 0x000FFFF) >> 00

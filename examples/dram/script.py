'''
Example script on how to use the dram class
'''
cd ~/Documents/uWaveMux-software-devel/examples/dram/
import time
from corr import katcp_wrapper

import tenGbEthernet
import dram
roach2 = katcp_wrapper.FpgaClient('192.168.0.136', 7147)
  
while (not roach2.is_connected()):
    time.sleep(1)

roach2.progdev('wip_dram.bof')



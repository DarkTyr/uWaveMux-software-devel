'''
Example script on how to use the dram class
'''

cd ~/Documents/uWaveMux-software-devel/examples/dram/
import time
from corr import katcp_wrapper
import if_board
import tenGbEthernet
import roach2NIST
roach2 = katcp_wrapper.FpgaClient('192.168.0.136', 7147)
  
while (not roach2.is_connected()):
    time.sleep(1)

roach2.progdev('if_board.rev1.bof')

ifBoard = if_board.IF_Board(roach2)
ifBoard.muxes(1,0,0,0,0)  #internal LO, Internal ADC/DAC clk
ifBoard.progAdcClock(512e6)



import time
from corr import katcp_wrapper
import if_board
roach2 = katcp_wrapper.FpgaClient('192.168.0.136', 7147)
status = roach2.is_connected()
#wait for the Roach2 to be ready
if(not status):
    time.sleep(5)

roach2.progdev('if_board.bof')
roach2.write_int('reset', 7)
roach2.write_int('reset', 0)
ifBoard = if_board.IF_Board(roach2)

#muxes(self, clock_int, bb_loop, lo_doubler, rf_loop, lo_ext)

#ifBoard.muxes(1,0,0,0,1)  #external LO needed
ifBoard.muxes(1,0,0,0,0)  #internal LO, Internal ADC/DAC clk

ifBoard.progAdcClock2(512e6)
#Works for LOs in the range of 3GHz to 6GHz give or take, 
#i run at 5.5GHz to 6GHz
ifBoard.progLO(5.5e9, 1,2)

#progLO2 has some issues in getting the right frequency if one at all
#ifBoard.progLO2(5.5e9)
ifBoard.progAttenuator(0, 0)
 

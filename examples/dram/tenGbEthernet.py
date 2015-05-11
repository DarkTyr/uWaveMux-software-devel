#!/bin/env ipython

'''

'''
import time
from corr import katcp_wrapper 
fpga = katcp_wrapper.FpgaClient

class TenGbEthernet:
    def __init__(self, fpga):
        self.fpga = fpga
        #Simulated data variables
        self.pkt_period = 8000
        self.pkt_length = 1024
        #Destination information
        self.dest_ip = 192*(2**24) + 168*(2**16) + 3*(2**8) + 1
        self.dest_port = 60000
        #Port Configuration Information
        self.mac_base = (2<<40) + (2<<32)
        self.source_ip = 192*(2**24) + 168*(2**16) + 3*(2**8) + 13
        self.source_port = 60000
        
    def configurePort(self):
        self.fpga.tap_start('tap3', 'tengbe_gbe0', self.mac_base + self.source_ip, self.source_ip, self.source_port)
        self.fpga.write_int('tengbe_dest_ip', self.dest_ip)
        self.fpga.write_int('tengbe_dest_port', self.dest_port)
        time.sleep(7) #sleep for a bit so it can build the routing table
        
    def configurePktSim(self):
        self.fpga.write_int('pkt_sim_enable', 0)
        self.fpga.write_int('pkt_sim_payload_len', self.pkt_length)
        self.fpga.write_int('pkt_sim_period', self.pkt_period)
        
    def configureAll(self):
        self.configurePort()
        self.configurePktSim()
    
    def pktSimEnable(self, enable):
        self.fpga.write_int('pkt_sim_enable', enable)
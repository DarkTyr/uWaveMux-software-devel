import struct	#Needed to build the data structure to give to socket class
import socket	#Needed to send data over 10Gbe
import time     #figure out how long it takes to write the LUT
from math import *
from numpy import *
from corr import katcp_wrapper 
fpga = katcp_wrapper.FpgaClient

class Roach2NIST:
    def __init__(self, fpga):
        self.fpga = fpga
        #DAC LUT variables
        self.sampleRate = 512e6
        self.dac_lut_offset = 0
        self.lutBuffer = 2**16
        self.offset = 0

    def dacFreqCombLUT(self, frequencies = [0.0], amplitude = [1.0], phase = [0.0]):
        dac_bit_range = 2**15 - 1 #15 bits plus the sign bit
        frequencyRes = self.sampleRate / self.lutBuffer
        size = int(self.sampleRate / frequencyRes)
        I, Q = array([0.0] * size), array([0.0] * size)
        single_I, single_Q = array([0.0] * size), array([0.0] * size)
        #generate table for each frequency and add to master table I and Q
        print len(frequencies), size, self.sampleRate, self.offset
        for n in range(len(frequencies)):
                x = [2 * pi * frequencies[n] * (t) / self.sampleRate + phase[n] for t in range(size)]
                y = [2 * pi * frequencies[n] * t / self.sampleRate + phase[n] for t in range(size)]
                single_I = amplitude[n] * cos(x)
                single_Q = amplitude[n] * sin(y)
                
                #Add current frequency LUT to the DAC LUT
                I = I + single_I
                Q = Q + single_Q
        #find absolute max value for each time step
        a = array([abs(I).max(), abs(Q).max()])
        
        #transform I and Q into maximum unity vectors
        self.dac_I = array([int(i * dac_bit_range / a.max()) for i in I])
        self.dac_Q = array([int(q * dac_bit_range / a.max()) for q in Q])

    def createLUTs(self):
        'createLUTs()'

        binaryData = ''
        padzero = struct.pack('>h', 0x0000)

        for n in range(len(self.dac_Q)/2):
            if(n < 10):
                print self.dac_I[2*n], self.dac_I[2*n+1]
                
            i_dac_0 = struct.pack('>h', self.dac_I[2*n])
            i_dac_1 = struct.pack('>h', self.dac_I[2*n+1])
            i_dac_2 = struct.pack('>h', self.dac_I[2*n])
            i_dac_3 = struct.pack('>h', self.dac_I[2*n+1])
            q_dac_0 = struct.pack('>h', self.dac_Q[2*n])
            q_dac_1 = struct.pack('>h', self.dac_Q[2*n+1])
            q_dac_2 = struct.pack('>h', self.dac_Q[2*n])
            q_dac_3 = struct.pack('>h', self.dac_Q[2*n+1])
            
            i_dds_0 = struct.pack('>h', 0x0000)
            i_dds_1 = struct.pack('>h', 0x0000)
            q_dds_0 = struct.pack('>h', 0x0000)
            q_dds_1 = struct.pack('>h', 0x0000)
             
            binaryData = binaryData + i_dds_1 + i_dds_0 + i_dds_1 + i_dds_0 \
                                    + i_dds_1 + i_dds_0 + i_dds_1 + i_dds_0 \
                                    + q_dds_1 + q_dds_0 + i_dds_1 + i_dds_0 \
                                    + i_dds_1 + i_dds_0 + q_dac_1 + q_dac_0 \
                                    + i_dac_1 + i_dac_0 + padzero + padzero 
            #binaryData = binaryData + padding + i_dac_1 + i_dac_0
            if(n == 16):
                print list(binaryData)
                
        return binaryData
    
    def createLUTsCount(self, number):
        binaryData = ''
        for x in range(number):
            temp = struct.pack('>h', x)
            binaryData = binaryData + temp
        return binaryData

	def writeLUTs(self,binaryData):
        self.fpga.write_int('dacEn', 0)   
        self.fpga.write_int('dram_sm_cmd_port', 60002)
        self.fpga.write_int('dram_sm_size', len(binaryData)/40 - 1)
        self.fpga.write_int('dram_wr_select', 1)
        self.fpga.write_int('dram_sm_arm', 1)
        self.fpga.write_int('dram_sm_arm', 0)
        #self.uploadBinaryData(binaryData, 1024, '192.168.3.13', 60000)
        self.uploadBinaryData(binaryData, 1280, '192.168.3.13', 60000)
        self.fpga.write_int('dram_sm_arm', 0)
        self.fpga.write_int('dram_wr_select', 0)

	def uploadLUTs(self):
        binary_data = self.createLUTs()
        self.uploadBinaryData(binary_data)
        

    def uploadBinaryData(self, binary_data, packet_len = 1024, dest_ip = '192.168.3.13', dest_port = 60000):
        data_len = len(binary_data)
        npkt = data_len/packet_len

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('',60002)) #source socket, note: you can put an ip in the ''
        for x in xrange(npkt):
            sock.sendto(binary_data[x*packet_len:(x+1)*packet_len], (dest_ip, dest_port))
            time.sleep(0.100)

    def regReadLUT(self, size, startAddr = 0):
        self.fpga.write_int('lut_cmd_valid', 0)
        self.fpga.write_int('lut_rd_ack', 0)
        array = []
        #I0 = []
        #Q0 = []
        #Idds = []
        #Qdds = []
        #sixtyfour = []
        
        reg0 = []
        reg1 = []
        reg2 = []
        reg3 = []
        reg4 = []
        reg5 = []
        reg6 = []
        reg7 = []
        reg8 = []
        addr = []

        for x in range(startAddr, startAddr + size, 1):
            self.fpga.write_int('lut_Read_notWrite', 1)
            self.fpga.write_int('lut_address', x)
            self.fpga.write_int('lut_cmd_valid', 1)
            self.fpga.write_int('lut_cmd_valid', 0)
            reg0.append(self.fpga.read_uint('lut_dataout0'))
            reg1.append(self.fpga.read_uint('lut_dataout1'))
            reg2.append(self.fpga.read_uint('lut_dataout2'))
            reg3.append(self.fpga.read_uint('lut_dataout3'))
            reg4.append(self.fpga.read_uint('lut_dataout4'))
            reg5.append(self.fpga.read_uint('lut_dataout5'))
            reg6.append(self.fpga.read_uint('lut_dataout6'))
            reg7.append(self.fpga.read_uint('lut_dataout7'))
            reg8.append(self.fpga.read_uint('lut_dataout8'))
            addr.append(x)          
            
            self.fpga.write_int('lut_rd_ack', 1)
            self.fpga.write_int('lut_rd_ack', 0)

        return addr, reg8, reg7, reg6, reg5, reg4, reg3, reg2, reg1, reg0
    
    def shortTwosComp(self, data):
        array = empty(len(data))
        for x in range(len(data)):
            if(data[x] & 0x8000):
                array[x] = ((~data[x] + 1) & 0xFFFF) * (-1)
            else:             
                array[x] = ((data[x]) & 0xFFFF)
        return array 


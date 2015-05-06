#!/bin/env ipython

'''

'''
import time, fractions, warnings
from corr import katcp_wrapper
fpga = katcp_wrapper.FpgaClient

class IF_Board:
    def __init__(self, fpga):
        self.fpga = fpga
        
    def fpgaCheck(self):
        if(self.fpga.is_connected() == True):
            if(any('if_board_start' in string for string in self.fpga.listdev())):
                return True
            else:
                print "Failed to find 'if_board_start' register."
                warnings.warn("Did you remember to program the FPGA on the ROACH2?!?!?!")
                return False
        else:
            warnings.warn("No FPGA connected. Is the ROACH2 turned on?!?!?!")
            return False
        
    def write_if_board(self, control, data):
        if(self.fpgaCheck() == False):
            return
        self.fpga.write_int('if_board_start', 0)
        self.fpga.write_int('if_board_control', control)
        self.fpga.write_int('if_board_data', data)
        self.fpga.write_int('if_board_start', 1)
        self.fpga.write_int('if_board_start', 0)
        time.sleep(0.5)
    
    #0b0  
    def muxes(self, clock_int, bb_loop, lo_doubler, rf_loop, lo_ext):
        if(self.fpgaCheck() == False):
            return
        data = int(clock_int) << 4 | int(bb_loop) << 3 | int(not(lo_doubler)) << 2 | int(not(rf_loop)) << 1 | int(lo_ext) << 0
        self.write_if_board(1, data)

    
    def progAdcClock(self, sampleRateMHz):
        if(self.fpgaCheck() == False):
            return
        ref_division_factor=8
        f_pfd = 10e6/ref_division_factor
        f = sampleRateMHz
    
        INT = int(f)/int(f_pfd)
        MOD = 2000
        FRAC = int(round(MOD*(f/f_pfd-INT)))
        if FRAC != 0:
            gcd = fractions.gcd(MOD,FRAC)
            if gcd != 1:
                MOD = MOD/gcd
            FRAC = int(FRAC/gcd)

        PHASE = 1
        R = 1
        power = 0
        aux_power = 0
        MUX = 5
        LOCK_DETECT = 1
        PRESCALAR = 1 #4/5 mode f<3GHz
        CHARGE_PUMP_CURRENT_SETTING=7
        LDP=1 # 6 ns
        POLARITY=1 #positive
        ENABLE_RF_OUTPUT = 1
        ENABLE_AUX_OUTPUT = 0
        BAND_SELECT_CLOCK_DIVIDER=80
        FEEDBACK_SELECT=1  #fundamental
        DIVIDER_SELECT=3  # div factor = 8
        CLOCK_DIVIDER_VALUE=150
        CTRL_BITS = [0,1,2,3,4,5]
        
        print 'INT = ' + repr(INT) + '   MOD = ' + repr(MOD) + '   FRAC = ' + repr(FRAC)
        reg5 = (LOCK_DETECT<<22) + CTRL_BITS[5]
        reg4 = (FEEDBACK_SELECT<<23) +(DIVIDER_SELECT<<20)+ (BAND_SELECT_CLOCK_DIVIDER<<12) + (ENABLE_AUX_OUTPUT<<8) + (aux_power<<6) + (ENABLE_RF_OUTPUT<<5) + (power<<3) + CTRL_BITS[4]
        reg3 = (CLOCK_DIVIDER_VALUE<<3) + CTRL_BITS[3]
        reg2 = (MUX<<26) + (R<<14) + (CHARGE_PUMP_CURRENT_SETTING<<9) + (LDP<<7) + (POLARITY<<6) + CTRL_BITS[2]
        reg1 = (PRESCALAR<<27) + (PHASE<<15) + (MOD<<3) + CTRL_BITS[1]
        reg0 = (INT<<15) + (FRAC<<3)+CTRL_BITS[0]
        
        print 'reg0 = ' + repr(reg0)
        print 'reg1 = ' + repr(reg1)
        print 'reg2 = ' + repr(reg2)
        print 'reg3 = ' + repr(reg3)
        print 'reg4 = ' + repr(reg4)
        print 'reg5 = ' + repr(reg5)
        
        self.write_if_board(4, reg5)
        self.write_if_board(4, reg4)
        self.write_if_board(4, reg3)
        self.write_if_board(4, reg2)
        self.write_if_board(4, reg1)
        self.write_if_board(4, reg0)
        self.write_if_board(4, reg0) #Double buffered register must be wrote to twice with the same thing to assert output
        
    def progLO(self,loFreq, outEn, powerOut):
        if(self.fpgaCheck() == False):
            return
        if (outEn == 1):
            rfEnable = 1
            auxEnable = 0
        elif (outEn == 2):
            rfEnable = 0
            auxEnable = 1
        else:
            rfEnable = 1
            auxEnable = 1

        #print "setting LO to = %1.4f Hz" % loFreq
        f_pfd = 10e6
        INT = int(loFreq)/int(f_pfd)
        MOD = 2000
        FRAC = int(round(MOD*(loFreq/f_pfd-INT)))
        if FRAC != 0:
            gcd = fractions.gcd(MOD,FRAC)
            if gcd != 1:
                MOD = MOD/gcd
                FRAC = int(FRAC/gcd)
        PHASE = 1
        R = 1
        power = powerOut
        aux_power = powerOut
        MUX = 3
        LOCK_DETECT = 1
        print 'INT = ' + repr(INT) + '   MOD = ' + repr(MOD) + '   FRAC = ' + repr(FRAC)
        reg5 = (LOCK_DETECT<<22) + (1<<2) + (1<<0)
        reg4 = (1<<23) + (1<<18) + (1<<16) + (auxEnable << 8) + (aux_power<<6) + (rfEnable << 5) + (power<<3) + (4)
        reg3 = (1<<10) + (1<<7) + (1<<5) + (1<<4) + (1<<1) + (1<<0)
        reg2 = (MUX<<26) + (R<<14) + (1<<11) + (1<<10) + (1<<9) + (1<<7) + (1<<6) + (1<<1)
        reg1 = (1<<27) + (PHASE<<15) + (MOD<<3) + (1<<0)
        reg0 = (INT<<15) + (FRAC<<3)
        print 'reg0 = ' + repr(reg0)
        print 'reg1 = ' + repr(reg1)
        print 'reg2 = ' + repr(reg2)
        print 'reg3 = ' + repr(reg3)
        print 'reg4 = ' + repr(reg4)
        print 'reg5 = ' + repr(reg5)        
        self.write_if_board(2, reg5)
        self.write_if_board(2, reg4)
        self.write_if_board(2, reg3)
        self.write_if_board(2, reg2)
        self.write_if_board(2, reg1)
        self.write_if_board(2, reg0)
        self.write_if_board(2, reg0) #Double buffered register must be wrote to twice with the same thing
        
    def progLOexample(self):
        if(self.fpgaCheck() == False):
            return

        #print "setting LO to = %1.4f Hz" % loFreq
        #freq = 2112.6e6 #(2.1126 GHz)
        
        intValue = 422
        frac = 13
        reg0 =(intValue << 15) + (frac << 3) + 0
        
        
        prescaler = 1
        phase = 1
        mod = 25
        reg1 = (prescaler << 27) + (phase << 15) + (mod << 3) + 1
        
        noise_spur = 0
        muxout = 0b101
        refx2 = 0
        refDiv2 = 0
        rCounter = 1
        doubleBuff = 0
        chargePump = 0b1111
        ldf = 0
        
        ldp = 0
        pdPolarity = 1
        
        power_down = 0
        cpThreeState = 0
        counterReset = 0
        reg2 =  (noise_spur << 29) + (muxout << 26) + (refx2 << 25) + (refDiv2 << 24) + \
                (rCounter << 14) + (doubleBuff << 13) + (chargePump << 9) + (ldf << 8) + \
                (ldp << 7) + (pdPolarity << 6) + (power_down << 5) + (cpThreeState << 4) + \
                (counterReset << 3) + 2
 
        csr = 0
        clkDivMode = 0
        clkDivValue = 0
        reg3 = (csr << 18) + (clkDivMode << 15) + (clkDivValue << 3) + 3
        
        feedbackSelect = 1
        rfDivSelect = 1
        rfBandSelectDiv = 1
        vcoPowerDown = 0
        mtld = 0
        auxOutSelect = 1
        auxOutEnable = 1
        auxPower = 0b11
        rfOutEnable = 1
        rfOutPower = 0b01
        reg4 =  (feedbackSelect << 23) + (rfDivSelect << 20) + (rfBandSelectDiv << 12) + (vcoPowerDown << 11) + \
                (mtld << 10) + (auxOutSelect << 9) + (auxOutEnable << 8) + (auxPower << 6) + \
                (rfOutEnable << 5) + (rfOutPower << 3) + 4
                
        LockDetectPin = 0b01
        reg5 = (LockDetectPin << 22) + 5
        
        self.write_if_board(2, reg5)
        self.write_if_board(2, reg4)
        self.write_if_board(2, reg3)
        self.write_if_board(2, reg2)
        self.write_if_board(2, reg1)
        self.write_if_board(2, reg0)
        self.write_if_board(2, reg0)#Double buffered register must be wrote to twice with the same thing
        
    def progAttenuator(self, attenuation_out, attenuation_in):
        if(self.fpgaCheck() == False):
            return
        #fixed 1 bit fixed point integer. 
        #bit 5   4  3  2  1   0
        #val 16  8  4  2  1  0.5
        #half a dB resolution
        attenuator1 = 0
        attenuator2 = 0
        attenuator3 = 0
        # xor with 0b111111 to invert the bits. 0 dB is 0b111111 31.5 dB is 0b000000 
        if attenuation_out > 31.5:
            attenuator1 = int(2 * 31.5) ^ 0b111111
            attenuator2 = int(2 * (attenuation_out - 31.5)) ^ 0b111111
        else:
            attenuator1 = int(2 * attenuation_out) ^ 0b111111
            attenuator2 = int(2 * 0) ^ 0b111111
            attenuator3 = int(2 * attenuation_in) ^ 0b111111

        reg0 = (attenuator3 << 12) + (attenuator2 << 6) + (attenuator1 << 0)
        self.write_if_board(8, reg0)
        
    def progAdcClock2(self, sampleRateHz):
        if(self.fpgaCheck() == False):
            return
        print 'Programming IF_Board ADC VCO for: ' + repr(sampleRateHz/1e6) + ' MHz'
        #Determine of the required frequency needs to be doubled or not externaly
        if (sampleRateHz > 550e9):
            print 'Requested Frequency is above the 550 MHz maximum for the ADC'
            warnings.warn("Failed to program ADC Clock, ADC clock limit exceeded")
        else:
            rfOutEnable = 1
            auxOutEnable = 0
            Freq = sampleRateHz * 8
        
        #Reference frequency source
        Fref = 10.0e6
        print 'Reference Frequency [Fref] = ' + repr(Fref/1e6) + ' MHz'
        #Multiple or divide the reference frequency and divide by home much
        refx2 = 0
        refDiv2 = 1
        rCounter = 1
        #Frequency of phase frequency detector to Fref relationship
        Fpfd = Fref * (1 + refx2)/(rCounter * (1 + refDiv2))
        #Calculate the multipliers and divisors to achieve Freq
        intValue = int(Freq/Fpfd)
        prescaler = 1
            
        x = fractions.Fraction(Freq/Fpfd - intValue).limit_denominator()
        frac = x.numerator
        mod = x.denominator
        
        print 'INT = ' + repr(intValue) + '   MOD = ' + repr(mod) + '   FRAC = ' + repr(frac)
        
        phase = 1
        #optimize for low phase noise = 0, spur = 1
        noise_spur = 0
        #Mux out Analog Lock detect
        muxout = 0b101
        doubleBuff = 0
        #The charge pump filter has been designed around a value of 7
        chargePump = 0b0111
        #modify what is considered locked
        ldf = 0  
        ldp = 0
        #phase detect polarity
        pdPolarity = 1
        #Power down the whole chip
        power_down = 0
        cpThreeState = 0
        counterReset = 0
        #Cycle slip reduction
        csr = 0
        
        clkDivMode = 0b00
        clkDivValue = 150
        
        feedbackSelect = 1
        rfDivSelect = 0b011
        rfBandSelectDiv = 80
        vcoPowerDown = 0
        mtld = 0
        auxOutSelect = 1
        auxPower = 0b01
        rfOutPower = 0b00     
        LockDetectPin = 0b01
        
        reg0 = (intValue << 15) + (frac << 3) + 0
        print 'reg0 = ' + repr(reg0)
        reg1 = (prescaler << 27) + (phase << 15) + (mod << 3) + 1
        print 'reg1 = ' + repr(reg1)
        reg2 =  (noise_spur << 29) + (muxout << 26) + (refx2 << 25) + (refDiv2 << 24) + \
                (rCounter << 14) + (doubleBuff << 13) + (chargePump << 9) + (ldf << 8) + \
                (ldp << 7) + (pdPolarity << 6) + (power_down << 5) + (cpThreeState << 4) + \
                (counterReset << 3) + 2
        print 'reg2 = ' + repr(reg2)
        reg3 = (csr << 18) + (clkDivMode << 15) + (clkDivValue << 3) + 3
        print 'reg3 = ' + repr(reg3)
        reg4 =  (feedbackSelect << 23) + (rfDivSelect << 20) + (rfBandSelectDiv << 12) + (vcoPowerDown << 11) + \
                (mtld << 10) + (auxOutSelect << 9) + (auxOutEnable << 8) + (auxPower << 6) + \
                (rfOutEnable << 5) + (rfOutPower << 3) + 4
        print 'reg4 = ' + repr(reg4)
        reg5 = (LockDetectPin << 22) + 5
        print 'reg5 = ' + repr(reg5)
        print 'Programming the ADC VCO for ' + repr(Fpfd * (intValue + frac/mod)/1e6) + ' MHz  with an RF divide of ' + repr(int(rfDivSelect))
        self.write_if_board(4, reg5)
        self.write_if_board(4, reg4)
        self.write_if_board(4, reg3)
        self.write_if_board(4, reg2)
        self.write_if_board(4, reg1)
        self.write_if_board(4, reg0)
        self.write_if_board(4, reg0)#Double buffered register must be wrote to twice with the same thing
        
    def progLO2(self, frequency):
        if(self.fpgaCheck() == False):
            return
        print 'Programming IF_Board LO VCO for: ' + repr(frequency/1e6) + ' MHz'
        #Determine of the required frequency needs to be doubled or not externaly
        if (frequency > 4.4e9):
            rfOutEnable = 0
            auxOutEnable = 1
            Freq = frequency/2
            print 'LO Frequency is above 4.4GHz, Remember to Enable doubler in muxes'
        else:
            rfOutEnable = 1
            auxOutEnable = 0
            Freq = frequency
        
        #Reference frequency source
        Fref = 10.0e6
        print 'Reference Frequency [Fref] = ' + repr(Fref/1e6) + ' MHz'
        #Multiple or divide the reference frequency and divide by home much
        refx2 = 0
        refDiv2 = 1
        rCounter = 1
        #Frequency of phase frequency detector to Fref relationship
        Fpfd = Fref * (1 + refx2)/(rCounter * (1 + refDiv2))
        #Calculate the multipliers and divisors to achieve Freq
        intValue = int(Freq/Fpfd)
        #Ensure that the frequency
        if(intValue < 75):
            prescaler = 0
        else:
            prescaler = 1
            
        x = fractions.Fraction(Freq/Fpfd - intValue).limit_denominator()
        frac = x.numerator
        mod = x.denominator
        
        print 'INT = ' + repr(intValue) + '   MOD = ' + repr(mod) + '   FRAC = ' + repr(frac)
        
        phase = 1
        #optimize for low phase noise = 0, spur = 1
        noise_spur = 0
        #Mux out Analog Lock detect
        muxout = 0b101
        doubleBuff = 0
        #The charge pump has been designed around a value of 7
        chargePump = 0b0111
        #modify what is considered locked
        ldf = 0  
        ldp = 0
        #phase detect polarity
        pdPolarity = 1
        #Power down the whole chip
        power_down = 0
        cpThreeState = 0
        counterReset = 0
        #Cycle slip reduction
        csr = 0
        
        clkDivMode = 0b00
        clkDivValue = 150
        
        feedbackSelect = 1
        rfDivSelect = 1
        rfBandSelectDiv = 1
        vcoPowerDown = 0
        mtld = 1
        auxOutSelect = 1
        auxPower = 0b01
        rfOutPower = 0b01     
        LockDetectPin = 0b01
        
        reg0 = (intValue << 15) + (frac << 3) + 0
        reg1 = (prescaler << 27) + (phase << 15) + (mod << 3) + 1
        reg2 =  (noise_spur << 29) + (muxout << 26) + (refx2 << 25) + (refDiv2 << 24) + \
                (rCounter << 14) + (doubleBuff << 13) + (chargePump << 9) + (ldf << 8) + \
                (ldp << 7) + (pdPolarity << 6) + (power_down << 5) + (cpThreeState << 4) + \
                (counterReset << 3) + 2
        reg3 = (csr << 18) + (clkDivMode << 15) + (clkDivValue << 3) + 3
        reg4 =  (feedbackSelect << 23) + (rfDivSelect << 20) + (rfBandSelectDiv << 12) + (vcoPowerDown << 11) + \
                (mtld << 10) + (auxOutSelect << 9) + (auxOutEnable << 8) + (auxPower << 6) + \
                (rfOutEnable << 5) + (rfOutPower << 3) + 4
        reg5 = (LockDetectPin << 22) + 5
        print 'Programming the LO VCO for ' + repr(Fpfd * (intValue + frac/mod)/1e6) + ' MHz'
        self.write_if_board(2, reg5)
        self.write_if_board(2, reg4)
        self.write_if_board(2, reg3)
        self.write_if_board(2, reg2)
        self.write_if_board(2, reg1)
        self.write_if_board(2, reg0)
        self.write_if_board(2, reg0)#Double buffered register must be wrote to twice with the same thing
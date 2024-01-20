#!/usr/bin/env python33

import string
import copy
import time

class FE_ASIC_REG_MAPPING:

####sec_chn_reg only sets a channel register, the other registers remains as before
    def set_fechn_reg(self, chip=0, chn=0, sts=0, snc=0, sg0=0, sg1=0, st0=0, st1=0, smn=0, sdf=0 ):
        chn_reg = ((sts&0x01)<<7) + ((snc&0x01)<<6) + ((sg0&0x01)<<5)+ ((sg1&0x01)<<4) + ((st0&0x01)<<3)+ ((st1&0x01)<<2)  + ((smn&0x01)<<1) + ((sdf&0x01)<<0) 
        chn_reg_bool = []
        for j in range(8):
            chn_reg_bool.append ( bool( (chn_reg>>j)%2 ) )
        start_pos = (8*16+16)*chip + (16-chn)*8
        self.REGS[start_pos-8 : start_pos] =  chn_reg_bool
#        self.set_fe_sync()


####sec_chip_global only sets a chip global register, the other registers remains as before
    def set_fechip_global(self, chip=0, slk0 = 0, stb1 = 0, stb = 0, s16=1, slk1=0, sdc = 0, sdd=0, sgp=0, swdac=0, dac=0):
        global_reg = ((slk0&0x01)<<0) + ((stb1&0x01)<<1) + ((stb&0x01)<<2)+ ((s16&0x01)<<3) + ((slk1&0x01)<<4) + ((sdc&0x01)<<5) +((sdd&0x01)<<6) +((sgp&0x01)<<7)
        dac_reg = (((dac&0x01)//0x01)<<7)+(((dac&0x02)//0x02)<<6)+\
                  (((dac&0x04)//0x04)<<5)+(((dac&0x08)//0x08)<<4)+\
                  (((dac&0x10)//0x10)<<3)+(((dac&0x20)//0x20)<<2)+\
                  (((swdac&0x03))<<0) 

        global_reg_bool = []
        for j in range(8):
            global_reg_bool.append ( bool( (global_reg>>j)%2 ) )
        for j in range(8):
            global_reg_bool.append ( bool( (dac_reg>>j)%2 ) )

        start_pos = (8*16+16)*chip + 16*8
        self.REGS[start_pos : start_pos+16] = global_reg_bool
#        self.set_fe_sync()


####sec_chip sets registers of a whole chip, registers of the other chips remains as before
    def set_fechip(self, chip=0,
                 sts=0, snc=0, sg0=0, sg1=0, st0=0, st1=0, smn=0, sdf=0,
                 slk0=0, stb1=0, stb=0, s16=1, slk1=0, sdc=0, sdd=0, sgp=0, swdac=0, dac=0):
        for chn in range(16):
            self.set_fechn_reg(chip, chn, sts, snc, sg0, sg1, st0, st1, smn, sdf)     
        self.set_fechip_global (chip, slk0, stb1, stb, s16, slk1, sdc, sdd, sgp, swdac, dac)
#        self.set_fe_sync()

####sec_board sets registers of a whole board 
    def set_fe_board(self, sts=0, snc=0, sg0=0, sg1=0, st0=0, st1=0, smn=0, sdf=0, 
                       slk0 = 0, stb1 = 0, stb = 0, s16=1, slk1=0, sdc=0, sdd=0, sgp=0, swdac=0, dac=0):
        self.set_fe_reset()
        for chip in range(8):
            self.set_fechip( chip, sts, snc, sg0, sg1, st0, st1, smn, sdf, slk0, stb1, stb, s16, slk1, sdc, sdd, sgp, swdac, dac)
        self.set_fe_sync()

    def set_fe_sync(self):
        for chip in range(8):
            for i in range(18):
                bits8 = self.REGS[(chip*18+i)*8: (chip*18+i+1)*8]
                self.regs_int8[chip][i ] = sum(v<<j for j, v in enumerate(bits8))

    def set_fe_reset(self):
        self.REGS = [False]*(8*16+16)*8 
        self.regs_int8 =[[0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2),[0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2)] 

    #__INIT__#
    def __init__(self):
        super().__init__()
	#declare board specific registers
        self.REGS = [False]*(8*16+16)*8 
        self.regs_int8 =[[0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2),[0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2), [0x00]*(16+2)] 
        self.set_fe_board()
        self.CREGS = copy.deepcopy(self.REGS) 
        self.Cregs_int8 = copy.deepcopy(self.regs_int8)

#fe = FE_ASIC_REG_MAPPING () 
#fe.set_fechip(chip=1, snc=1)
#fe.regs_int8[1][2] = 3
#print (fe.regs_int8)
#fe.set_fe_board()
#print (fe.regs_int8)
#regs_int8 =[0x00]*(16+2)
#for i in range(18):
#    bits8 = fe.REGS[i*8: (i+1)*8]
#    regs_int8[i ] = (sum(v<<j for j, v in enumerate(bits8)))


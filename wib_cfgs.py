from llc import LLC
from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
import copy

import sys, time, random

class WIB_CFGS(LLC, FE_ASIC_REG_MAPPING):
    def __init__(self):
        super().__init__()
        self.i2cerror = False 
        self.adcs_paras_init = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                          ]
        self.adcs_paras = self.adcs_paras_init
        self.adac_cali_quo = False

    def wib_rst_tp(self):
        print ("Configuring PLL")
        #self.script_fp(fp=bytes("scripts/conf_pll_timing", 'utf-8'))
        #self.script_fp(fp="/scripts/conf_pll_timing")
        self.script_exe(script="conf_pll_timing")
        #self.script_exe(script="startup")
        bp = self.peek(0xA00C008C)
        bp_slot_addr = bp&0x0f
        bp_crate_addr = (bp>>4)&0x0f
        timing_addr = (bp_crate_addr<<3) + bp_slot_addr&0x07
        self.poke(0xA00C0000, timing_addr + (1<<28))
        self.poke(0xA00C0000, timing_addr + (1<<28))
        time.sleep(2)
        self.poke(0xA00C0000, timing_addr + (0<<28))
        self.poke(0xA00C0000, timing_addr + (0<<28))

    def wib_fw(self):
        val = self.peek(regaddr = 0xA00C0088)
        fw_second = val&0x3f
        fw_minute = (val>>6)&0x3f
        fw_hour   = (val>>12)&0x3f
        fw_year   =2000 + ((val>>17)&0x3f)
        fw_month  = (val>>23)&0xf
        fw_day    = (val>>27)&0x1f
        print (f"WIB FW generated at {fw_year}-{fw_month}-{fw_day} {fw_hour}:{fw_minute}:{fw_second}")

    def wib_i2c_adj(self, n = 300):
        rdreg = self.peek(0xA00C0004)
        for i in range(n):
            self.poke(0xA00C0004 , rdreg|0x00040000) 
            rdreg = self.peek(0xA00C0004)
            self.poke(0xA00C0004 , rdreg&0xfffBffff) 

    def wib_timing(self, pll=False, fp1_ptc0_sel=0, cmd_stamp_sync = 0x7fff):
        #See WIB_firmware.docx table 4.9.1 ts_clk_sel
        # 0[pll=False]  = CDR recovered clock(default)
        # 1[pll=True]   = PLL clock synchronized with CDR or running independently if CDR clock is 
        # missing. PLL clock should only be used on test stand when timing master 
        # is not available.            
        reg_read = self.peek(0xA00C0004)
        val = (reg_read&0xFFFEFFFF) | (int(pll) << 16)
        self.poke(0xA00C0004, val)    
        if pll == True:
            print ("PLL clock synchronized with CDR or running independently if CDR clock is missing")
            print ("PLL clock should only be used on test stand when timing master is not available.")
            print ("Enable fake timing system")
            rdreg = self.peek(0xA00c000C)
            #disable fake time stamp
            self.poke(0xA00c000C, (rdreg&0xFFFFFFF1))
            #set the init time stamp
            self.poke(0xA00c0018, 0x00000000)
            self.poke(0xA00c001C, 0x00000000)
            #enable fake time stamp
            self.poke(0xA00c000C, (rdreg|0x0e))
        else:
            #timing point reset
            addr = 0xA00c0000
            self.poke(addr, 0x10000000)
            time.sleep(1)
            self.poke(addr, 0x00000000)
            time.sleep(1)
            rdreg = self.peek(0xA00c0090)
            print ("timing point status(addr 0x%08x) = 0x%08x"%(addr, rdreg))
        
            rdreg = self.peek(0xA00c0004)
            if fp1_ptc0_sel == 0:
                print ("timing master is available through backplane (PTC)")
                self.poke(0xA00c0004, (rdreg&0xFFFFFFDF)) #backplane
            else:
                print ("timing master is available through front_panel")
                self.poke(0xA00c0004, (rdreg&0xFFFFFFFF)|0x20) #front_panel
            time.sleep(1)
            rdreg = self.peek(0xA00c0090)
            print ("External timing is selected, wib reg addr 0xA00c0090=%x"%rdreg)

            rdreg = self.peek(0xA00c000C)
            #disable fake time stamp
            #print (hex(rdreg), hex(rdreg&0xFFFFFFF1))
            self.poke(0xA00c000C, (rdreg&0xFFFFFFF1))
            #time.sleep(0.1)
            rdreg = self.peek(0xA00c000C)
            #set the init time stamp
            #align_en = 1, cmd_stamp_sync_en = 1
            #self.poke(wib, 0xA00c000C, (rdreg|0x0C))
            #time.sleep(0.1)
            #send SYNC_FAST command when cmd_stamp_syn match the DTS time stamp
            self.poke(0xA00c000C, (cmd_stamp_sync<<16) + ((rdreg&0x8000FFFF)|0x0C) )
            time.sleep(0.1)
            rdreg = self.peek(0xA00c000C)

        #set edge_to_act_delay
        rdreg = self.peek(0xA0030004)
        #print ("edge_to_act_delay = 0x%08x"%rdreg)
        self.poke(0xA0030004, 19)
        rdreg = self.peek(0xA0030004)
        #print ("edge_to_act_delay = 0x%08x"%rdreg)

        #reset COLDATA RX to clear buffers
        rdreg = self.peek(0xA00C0004)
        #print ("coldata_rx_reset = 0x%08x"%rdreg)
        self.poke(0xA00C0004, rdreg&0xffffdfff)
        self.poke(0xA00C0004, rdreg|0x00002000)
        self.poke(0xA00C0004, rdreg&0xffffdfff)
        rdreg = self.peek(0xA00C0004)
        #print ("coldata_rx_reset = 0x%08x"%rdreg)

        #reset FELIX TX and loopback RX
        rdreg = self.peek(0xA00C0038)
        #print ("felix_rx_reset = 0x%08x"%rdreg)
        self.poke(0xA00C0038, rdreg&0xffffffdf)
        self.poke(0xA00C0038, rdreg|0x00000020)
        self.poke(0xA00C0038, rdreg&0xffffffdf)
        rdreg = self.peek(0xA00C0038)
        #print ("felix_rx_reset = 0x%08x"%rdreg)

        return self.peek(0xA00C0004)


    def fembs_vol_set(self, vfe=3.0, vcd=3.0, vadc=3.5):
        #self.femb_power_set(0, 0, vfe, vcd, vadc)
        #self.femb_power_set(1, 0, vfe, vcd, vadc)
        #self.femb_power_set(2, 0, vfe, vcd, vadc)
        #self.femb_power_set(3, 0, vfe, vcd, vadc)
        self.femb_power_config(0,  vfe, vcd, vadc)
        self.femb_power_config(1,  vfe, vcd, vadc)
        self.femb_power_config(2,  vfe, vcd, vadc)
        self.femb_power_config(3,  vfe, vcd, vadc)

    def femb_powering(self, fembs = []):
        if len(fembs) > 0:
            self.all_femb_bias_ctrl(enable=1 )
            if 0 in fembs: 
                self.femb_power_en_ctrl(femb_id=0, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
            else: 
                self.femb_power_en_ctrl(femb_id=0, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
            if 1 in fembs: 
                self.femb_power_en_ctrl(femb_id=1, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
            else: 
                self.femb_power_en_ctrl(femb_id=1, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
            if 2 in fembs: 
                self.femb_power_en_ctrl(femb_id=2, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
            else: 
                self.femb_power_en_ctrl(femb_id=2, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
            if 3 in fembs: 
                self.femb_power_en_ctrl(femb_id=3, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
            else: 
                self.femb_power_en_ctrl(femb_id=3, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
        else:
            self.all_femb_bias_ctrl(enable=0 )

#    def get_sensors(self):
        #print ("Power configuration measurement is not ready yet...")
        #return None

    def en_ref10MHz(self, ref_en = False):
        if ref_en:
            self.poke(0xff5e00c4, 0x1033200)
            print ("P12 outputs 10MHz reference clock for signal generator")
        else:
            self.poke(0xff5e00c4, 0x52000)

    def wib_mon_switches(self, dac0_sel=0, dac1_sel=0, dac2_sel=0, dac3_sel=0, mon_vs_pulse_sel=0, inj_cal_pulse=0):
        reg_value = (dac0_sel&0x01) + ((dac1_sel&0x01)<<1) + ((dac2_sel&0x01)<<2) + ((dac2_sel&0x01)<<3) + ((mon_vs_pulse_sel&0x01)<<4)+ ((inj_cal_pulse&0x01)<<5)
        rdreg = self.peek(0xA00C003C)
        self.poke(0xA00C003C, (rdreg&0xffffffC0)|reg_value)

    def wib_mon_adcs(self):
        rdreg = self.peek(0xA00C0004)
        #set bit19(mon_adc_start) to 1 and then to 0 to start monitring ADC conversion
        self.poke(0xA00C0004,(rdreg&0xfff7ffff)|0x80000) #Set bit19 to 1
        self.poke(0xA00C0004,rdreg&0xfff7ffff) #set bit19 to 0
        time.sleep(0.001)
        while True:
            rdreg = self.peek(0xA00C0090)
            mon_adc_busy = (rdreg>>19)&0x01 
            if mon_adc_busy == 0:
                break
            else:
                time.sleep(0.001)
        rdadc01 = self.peek(0xA00C00C4)
        rdadc23 = self.peek(0xA00C00C8)
        adc0 = rdadc01&0xffff
        adc1 = (rdadc01>>16)&0xffff
        adc2 = rdadc23&0xffff
        adc3 = (rdadc23>>16)&0xffff
        return adc0, adc1, adc2, adc3

    def femb_cd_rst(self):
    #Reset COLDATA
    #This fixes the problem where some COLDATAs don't toggle the pulse when they're told to
        print ("Sending Fast command reset")
        self.adcs_paras = self.adcs_paras_init
        self.fastcmd(cmd= 'reset')
        self.adac_cali_quo = False
        time.sleep(0.05)
    #note: later all registers should be read and stored (to do)

    def femb_cd_sync(self):
        print ("Sending Fast command sync")
        self.fastcmd(cmd= 'sync')

    def femb_cd_edge(self):
        print ("Sending Fast command edge")
        self.fastcmd(cmd= 'edge')

    def femb_cd_edge_act(self, fembs):
        wrdata = 0x05
        for femb_id in fembs:
            self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=wrdata)
            self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=wrdata)
        self.fastcmd(cmd= 'edge_act')
        wrdata = 0x00
        for femb_id in fembs:
            self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=wrdata)
            self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=wrdata)

    def femb_i2c_wr(self, femb_id, chip_addr, reg_page, reg_addr, wrdata):
        self.cdpoke(femb_id, chip_addr=chip_addr, reg_page=reg_page, reg_addr=reg_addr, data=wrdata)

    def femb_i2c_rd(self, femb_id, chip_addr, reg_page, reg_addr):
        rddata = self.cdpeek(femb_id, chip_addr=chip_addr, reg_page=reg_page, reg_addr=reg_addr )
        return rddata

    def femb_i2c_wrchk(self, femb_id, chip_addr, reg_page, reg_addr, wrdata):
        i = 0 
        self.femb_i2c_wr(femb_id, chip_addr, reg_page, reg_addr, wrdata)
        rddata = self.femb_i2c_rd(femb_id, chip_addr, reg_page, reg_addr)
        i = i + 1
        if wrdata != rddata:
            print ("Error, I2C: femb_id=%x, chip_addr=%x, reg_page=%x, reg_addr=%x, wrdata=%x, rddata=%x, retry!"%(femb_id, chip_addr, reg_page, reg_addr, wrdata, rddata))
            self.i2cerror = True

    def data_cable_latency(self, femb_id):
        print ("data_cable_latency measurement is not verified yet")
        if False:
            # set WIB_FEEDBACK_CODE registers to B2
            self.femb_i2c_wr(femb_id, chip_addr=3, reg_page=0, reg_addr=0x2B, wrdata=0xB2)
            self.femb_i2c_wr(femb_id, chip_addr=3, reg_page=0, reg_addr=0x2C, wrdata=0xB2)
            self.femb_i2c_wr(femb_id, chip_addr=3, reg_page=0, reg_addr=0x2D, wrdata=0xB2)
            # set ACTCOMMANDREG register to 9
            self.femb_i2c_wr(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=0x09)
            #issue FAST ACT command to enable loopback
            self.fastcmd(cmd= 'act')
            for i in range(6):
                if femb_id == 0:
                    btr = 0xA0010000
                elif femb_id == 1:
                    btr = 0xA0050000
                elif femb_id == 2:
                    btr = 0xA0070000
                elif femb_id == 3:
                    btr = 0xA0090000
                self.poke(btr + 0x8, 0) #dummy writes
            self.poke(btr + 0x8, 1) #issue stimulus
            time.sleep(0.01)
            rdreg = self.peek(btr + 0x8) #read measured latency
            print (hex(rdreg))
            self.poke(btr + 0x8, 0) #dummy writes
            self.femb_i2c_wr(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=0x00)

    def femb_cd_cfg(self, femb_id):
#set coldata 8b10 
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x03, wrdata=0x3c)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x03, wrdata=0x3c)
#set LVDS current strength
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x11, wrdata=0x07)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x11, wrdata=0x07)
#Lengthen SCK time during SPI write for more stability
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x25, wrdata=0x40)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x25, wrdata=0x40)
#FE power on
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x27, wrdata=0x1f)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x27, wrdata=0x1f)
#tie LArASIC test pin to ground
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x26, wrdata=0x02)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x26, wrdata=0x00)
#Frame14
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x01, wrdata=0x01)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x01, wrdata=0x01)

    def femb_cd_gpio(self, femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f):
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x27, wrdata=cd1_0x27)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x27, wrdata=cd2_0x27)
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x26, wrdata=cd1_0x26)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x26, wrdata=cd2_0x26)

    def femb_cd_fc_act(self, femb_id, act_cmd="idle"):
        if act_cmd == "idle":
            wrdata = 0
        elif act_cmd == "larasic_pls":
            wrdata = 0x01
        elif act_cmd == "save_timestamp":
            wrdata = 0x02
        elif act_cmd == "save_status":
            wrdata = 0x03
        elif act_cmd == "clr_saves":
            wrdata = 0x04
        elif act_cmd == "rst_adcs":
            wrdata = 0x05
        elif act_cmd == "rst_larasics":
            wrdata = 0x06
        elif act_cmd == "rst_larasic_spi":
            wrdata = 0x07
        elif act_cmd == "prm_larasics":
            wrdata = 0x08
        elif act_cmd == "relay_i2c_sda":
            wrdata = 0x09
        else:
            wrdata = 0

        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=wrdata)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=wrdata)
        self.fastcmd(cmd= 'act')
#return to "idle" in case other FEMB runs FC 
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=0)
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=0)
        
    def data_align(self, fembs=[0, 1, 2,3]):
        self.femb_cd_sync() #sync should be sent before edge
        time.sleep(0.01)
        self.femb_cd_edge()
        time.sleep(0.5)
        
        rdaddr = 0xA00C0010
        rdreg = self.peek(rdaddr)
        wrvalue = 0x10 #cmd_code_edge = 0x10
        wrreg = (rdreg & 0xffff00ff) + ((wrvalue&0xff)<<8)
        self.poke(rdaddr, wrreg) 
        
        rdaddr = 0xA00C000C
        rdreg = self.peek(rdaddr)
        wrvalue = 0x7fec #cmd_stamp_sync = 0x7fec
        wrreg = (rdreg & 0x0000ffff) + ((wrvalue&0xffff)<<16)
        self.poke(rdaddr, wrreg) 
        
        rdaddr = 0xA00C000C
        rdreg = self.peek(rdaddr)
        wrvalue = 0x1 #cmd_stamp_sync_en = 1
        wrreg = (rdreg & 0xfffffffb) + ((wrvalue&0x1)<<2)
        self.poke(rdaddr, wrreg) 
            
        for dts_time_delay in  range(0x58, 0x70,1):
            rdaddr = 0xA00C000C
            rdreg = self.peek(rdaddr)
            wrvalue = dts_time_delay #0x58 #dts_time_delay = 1
            wrreg = (rdreg & 0xffff00ff) + ((wrvalue&0xff)<<8)
            self.poke(rdaddr, wrreg) 
            rdaddr = 0xA00C000C
            rdreg = self.peek(rdaddr)
            wrvalue = 0x1 #align_en = 1
            wrreg = (rdreg & 0xfffffff7) + ((wrvalue&0x1)<<3)
            self.poke(rdaddr, wrreg) 
            time.sleep(0.2)
            if 0 in fembs:
                link0to3 = self.peek(0xA00C00A8)
            else:
                link0to3 = 0x0
            if 1 in fembs:
                link4to7 = self.peek(0xA00C00AC)
            else:
                link4to7 = 0x0
            if 2 in fembs:
                link8tob = self.peek(0xA00C00B0)
            else:
                link8tob = 0x0
            if 3 in fembs:
                linkctof = self.peek(0xA00C00B4)
            else:
                linkctof = 0x0

            if ((link0to3 & 0xe0e0e0e0) == 0) and ((link4to7 & 0xe0e0e0e0) == 0)and ((link8tob & 0xe0e0e0e0) == 0) and ((linkctof & 0xe0e0e0e0) == 0):
                print ("Data is aligned when dts_time_delay = 0x%x"%dts_time_delay )
                break
            if dts_time_delay >= 0x6f:
                print ("Error: data can't be aligned, exit anyway")
                exit()

    def femb_adc_cfg(self, femb_id):
        self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")

        for adc_no in range(8):
            c_id    = self.adcs_paras[adc_no][0]
            data_fmt= self.adcs_paras[adc_no][1] 
            diff_en = self.adcs_paras[adc_no][2] 
            sdc_en  = self.adcs_paras[adc_no][3] 
            vrefp   = self.adcs_paras[adc_no][4] 
            vrefn   = self.adcs_paras[adc_no][5]  
            vcmo    = self.adcs_paras[adc_no][6] 
            vcmi    = self.adcs_paras[adc_no][7] 
            autocali= self.adcs_paras[adc_no][8] 
            #start_data
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=2, reg_addr=0x01, wrdata=0x0c)
            #offset_binary_output_data_format
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x89, wrdata=data_fmt)
            #diff or se
            if diff_en == 0:
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x84, wrdata=0x3b)
            if sdc_en == 0:
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x80, wrdata=0x23) #SDC bypassed
            else:
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x80, wrdata=0x62) #SDC on
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x98, wrdata=vrefp)
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x99, wrdata=vrefn)
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9a, wrdata=vcmo)
            self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9b, wrdata=vcmi)

            if autocali:
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9f, wrdata=0)
                time.sleep(0.01)
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9f, wrdata=0x03)
        if autocali&0x01:
            time.sleep(0.5) #wait for ADC automatic calbiraiton process to complete
            for adc_no in range(8):
                c_id    = self.adcs_paras[adc_no][0]
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9f, wrdata=0x00)
        if autocali&0x02: #output ADC back-end data pattern
            for adc_no in range(8):
                c_id    = self.adcs_paras[adc_no][0]
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0xB2, wrdata=0x20)
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0xB3, wrdata=0xCD)
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0xB4, wrdata=0xAB)
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0xB5, wrdata=0x34)
                self.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0xB6, wrdata=0x12)

    def femb_fe_cfg(self, femb_id):
        #reset LARASIC chips
        self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
        time.sleep(0.01)
        self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
        #program LARASIC chips
        time.sleep(0.01)
        for chip in range(8):
            for reg_id in range(16+2):
                if (chip < 4):
                    self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
                else:
                    self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
        i = 0
        while True:
            self.femb_cd_fc_act(femb_id, act_cmd="clr_saves")
            time.sleep(0.01)
            self.femb_cd_fc_act(femb_id, act_cmd="prm_larasics")
            time.sleep(0.05)
            self.femb_cd_fc_act(femb_id, act_cmd="save_status")
            time.sleep(0.005)

            sts_cd1 = self.femb_i2c_rd(femb_id, chip_addr=3, reg_page=0, reg_addr=0x24)
            sts_cd2 = self.femb_i2c_rd(femb_id, chip_addr=2, reg_page=0, reg_addr=0x24)

            if (sts_cd1&0xff == 0xff) and (sts_cd2&0xff == 0xff):
                break
            else:
                print ("LArASIC readback status is {}, {} diffrent from 0xFF".format(sts_cd1, sts_cd2))
                if i > 10:
                    print ("exit anyway")
                    exit()
                else:
                    time.sleep(0.1)
            i = i + 1

    def femb_adac_cali(self, femb_id, phase0x07=[0,0,0,0,0,0,0,0]):
        for chip in range(8):
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x6, wrdata=0x30        )
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x7, wrdata=phase0x07[chip])
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x8, wrdata=0x38        )
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x9, wrdata=0x80        )

        self.adac_cali_quo = not self.adac_cali_quo
        self.femb_cd_fc_act(femb_id, act_cmd="larasic_pls")
        return self.adac_cali_quo

    def femb_cfg(self, femb_id, adac_pls_en = False):
        refi= 0
        while True:
            self.femb_cd_cfg(femb_id)
            self.femb_adc_cfg(femb_id)
            self.femb_fe_cfg(femb_id)
            if adac_pls_en:
                self.femb_adac_cali(femb_id)
            link_mask = 0xffff
            if femb_id == 0:
                link_mask = link_mask&0xfff0
            if femb_id == 1:
                link_mask = link_mask&0xff0f
            if femb_id == 2:
                link_mask = link_mask&0xf0ff
            if femb_id == 3:
                link_mask = link_mask&0x0fff
            self.poke(0xA00C0008, link_mask)
            #self.femb_cd_sync()
            if self.i2cerror:
                print ("Reconfigure due to i2c error!")
                self.i2cerror = False
                refi += 1
                if refi > 5:
                    print ("I2C failed! exit anyway")
                    exit()
            else:
                print (f"FEMB{femb_id} is configurated")
                break

    def femb_fe_mon(self, femb_id, adac_pls_en = 0, rst_fe=0, mon_type=2, mon_chip=0, mon_chipchn=0, snc=0,sg0=0, sg1=0 ):
        if (rst_fe != 0):
            self.set_fe_reset()

        if (mon_type==2): #monitor bandgap 
            stb0=1
            stb1=1
            chn=0
        elif (mon_type==1): #monitor temperature
            stb0=1
            stb1=0
            chn=0
        else: #monitor analog
            stb0=0
            stb1=0
            chn=mon_chipchn

        self.set_fe_reset()
        #ONlY one channel of a FEMB can set smn to 1 at a time
        self.set_fechn_reg(chip=mon_chip&0x07, chn=chn, snc=snc, sg0=sg0, sg1=sg1, smn=1, sdf=1) 
        self.set_fechip_global(chip=mon_chip&0x07, stb1=stb1, stb=stb0)
        self.set_fe_sync()

        #self.femb_cfg(femb_id )
        self.femb_fe_cfg(femb_id)

        self.femb_cd_gpio(femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)


    def wib_fe_mon(self, femb_ids, adac_pls_en = 0, rst_fe=0, mon_type=2, mon_chip=0, mon_chipchn=0, snc=0,sg0=0, sg1=0, sps=10 ):
        #step 1
        #reset all FEMBs on WIB
        self.femb_cd_rst()
        
        #step 2
        for femb_id in femb_ids:
            self.femb_fe_mon(femb_id, adac_pls_en, rst_fe, mon_type, mon_chip, mon_chipchn, snc,sg0, sg1 )
            print (f"FEMB{femb_id} is configurated")

        #step4
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0) 
        time.sleep(1)
        adcss = []
        self.wib_mon_adcs() #get rid of previous result
        for i in range(sps):
            adcs = self.wib_mon_adcs()
            adcss.append(adcs)
        return adcss

    def femb_fe_dac_mon(self, femb_id, mon_chip=0,sgp=False, sg0=0, sg1=0, vdac=0  ):
        self.set_fe_reset()
        self.set_fe_board(sg0=sg0, sg1=sg1)
        self.set_fechip_global(chip=mon_chip&0x07, swdac=3, dac=vdac, sgp=sgp)
        self.set_fe_sync()
        #self.femb_cfg(femb_id )
        self.femb_fe_cfg(femb_id)
        self.femb_cd_gpio(femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)

    def wib_fe_dac_mon(self, femb_ids, mon_chip=0,sgp=False, sg0=0, sg1=0, vdac=0, sps = 10 ): 
        #step 1
        #reset all FEMBs on WIB
        self.femb_cd_rst()
        
        #step 2
        for femb_id in femb_ids:
            self.femb_fe_dac_mon(femb_id, mon_chip,sgp=sgp, sg0=sg0, sg1=sg1, vdac=vdac  )
            print (f"FEMB{femb_id} is configurated")

        #step4
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0) 
        time.sleep(1)
        adcss = []
        self.wib_mon_adcs() #get rid of previous result
        for i in range(sps):
            adcs = self.wib_mon_adcs()
            adcss.append(adcs)
        return adcss

    def femb_adc_mon(self, femb_id, mon_chip=0, mon_i=0  ):
        adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07]  
        cd2_iobit432 = [6,4,5,7,3,1,0,2]
        self.femb_cd_gpio(femb_id, cd1_0x26 = 0x04,cd1_0x27 = 0x1f, cd2_0x26 = cd2_iobit432[mon_chip]<<2,cd2_0x27 = 0x1f)
        vrefp   = self.adcs_paras[mon_chip][4] 
        vrefn   = self.adcs_paras[mon_chip][5]  
        vcmo    = self.adcs_paras[mon_chip][6] 
        vcmi    = self.adcs_paras[mon_chip][7] 
        #    self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x9, wrdata=0x80        )
        self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=adcs_addr[mon_chip], reg_page=1, reg_addr=0x98, wrdata=vrefp) #vrefp
        self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=adcs_addr[mon_chip], reg_page=1, reg_addr=0x99, wrdata=vrefn) #vrefn
        self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=adcs_addr[mon_chip], reg_page=1, reg_addr=0x9a, wrdata=vcmo) #vcmo
        self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=adcs_addr[mon_chip], reg_page=1, reg_addr=0x9b, wrdata=vcmi) #vcmi
        self.femb_i2c_wr(femb_id=femb_id,    chip_addr=adcs_addr[mon_chip], reg_page=1, reg_addr=0xaf, wrdata=(mon_i<<2)|0x01)

    def wib_adc_mon(self, femb_ids, sps=10  ): 
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0) 
        #step 1
        #reset all FEMBs on WIB
        self.femb_cd_rst()
        
        #step 2
        mon_items = []
        mons = ["VBGR", "VCMI", "VCMO", "VREFP", "VREFN", "VBGR", "VSSA", "VSSA"]
        for mon_i in range(8):
            print (f"Monitor ADC {mons[mon_i]}")
            mon_dict = {}
            for mon_chip in range(8):
            #for mon_chip in range(1):
                for femb_id in femb_ids:
                    self.femb_adc_cfg(femb_id)
                    self.femb_adc_mon(femb_id, mon_chip=mon_chip, mon_i=mon_i  )
                    print (f"FEMB{femb_id} is configurated")
                adcss = []
                time.sleep(1)
                self.wib_mon_adcs() #get rid of previous result
                self.wib_mon_adcs() #get rid of previous result
                for i in range(sps):
                    adcs = self.wib_mon_adcs()
                    adcss.append(adcs)
                mon_dict[f"chip{mon_chip}"] = [mon_chip, mons[mon_i], self.adcs_paras[mon_chip], adcss]
                print (mon_dict[f"chip{mon_chip}"])
            mon_items.append(mon_dict)

    def wib_adc_mon_chip(self, femb_ids, mon_chip=0, sps=10):
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0)
        #reset all FEMBs on WIB
        self.femb_cd_rst()

        mon_dict = {}
        mons = ["VBGR", "VCMI", "VCMO", "VREFP", "VREFN", "VSSA"]
        for mon_i in range(len(mons)):
            print (f"Monitor ADC {mons[mon_i]}")
            for femb_id in femb_ids:
                self.femb_adc_cfg(femb_id)
                self.femb_adc_mon(femb_id, mon_chip=mon_chip, mon_i=mon_i  )
                print (f"FEMB{femb_id} is configurated")
            adcss = []
            time.sleep(1)
            self.wib_mon_adcs() #get rid of previous result
            self.wib_mon_adcs() #get rid of previous result
            for i in range(sps):
                adcs = self.wib_mon_adcs()
                adcss.append(adcs)
            mon_dict[mons[mon_i]] = [self.adcs_paras[mon_chip], adcss]
        return mon_dict


    def spybuf_trig(self, fembs,  num_samples=1, trig_cmd=0x04, spy_rec_ticks=0x3f00): 
        if trig_cmd == 0x00:
            print (f"Data collection for FEMB {fembs} with software trigger")
        else:
            print (f"Data collection for FEMB {fembs} with trigger operations")

        data = []
        for i in range(num_samples):
            if trig_cmd == 0x00:
                rdreg = self.peek(0xA00C0004)
                wrreg = (rdreg&0xffffff3f)|0xC0
                self.poke(0xA00C0004, wrreg) #reset spy buffer
                wrreg = (rdreg&0xffffff3f)|0x00
                self.poke(0xA00C0004, wrreg) #release spy buffer
                time.sleep(0.002)
                rdreg = self.peek(0xA00C0004)
                wrreg = (rdreg&0xffffff3f)|0xC0
                self.poke(0xA00C0004, wrreg) #reset spy buffer
                rawdata = self.spybuf(fembs)
                data.append((rawdata, 0, 0x3ffff, 0x00))
            else:
                rdreg = self.peek(0xA00C0004)
                wrreg = (rdreg&0xffffff3f)|0xC0
                self.poke(0xA00C0004, wrreg) #reset spy buffer
                wrreg = (rdreg&0xffffff3f)|0x00
                self.poke(0xA00C0004, wrreg) #release spy buffer
                
                self.poke(0xA00C0024, trigger_rec_ticks) #spy rec time
                rdreg = self.peek(0xA00C0014)
                wrreg = (rdreg&0xff00ffff)|(trigger_command<<16)
                self.poke(0xA00C0014, wrreg) #program cmd_code_trigger

                while True:
                    spy_full_flgs = False
                    rdreg = self.peek(0xA00C0080)
                    if rdreg&0x03 == 0x03:
                        spy_full_flgs = True
                        buf0_end_addr = self.peek(0xA00C0094)
                        buf1_end_addr = self.peek(0xA00C0098)
                        if buf0_end_addr == buf1_end_addr:
                            spy_full_flgs = True
                        else:
                            spy_full_flgs = False
                        rawdata = self.spybuf(fembs)
                        data = (rawdata, buf0_end_addr, trigger_rec_ticks, trigger_command)
                    else:
                        spy_full_flgs = False
                        break
                    if spy_full_flgs:
                        break
                    else:
                        print ("No external trigger received, Wait a second ")
                        time.sleep(1)
                data.append(data)
        return data
  
#wib = WIB_CFGS()
#wib.wib_fw()


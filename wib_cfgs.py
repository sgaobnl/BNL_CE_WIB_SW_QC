from llc import LLC
from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
import copy
from datetime import datetime
import sys, time, random
from spymemory_decode import wib_dec

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
        self.adac_cali_quo = [False,False,False,False]
        self.longcable = False #>7m
        self.cd_flg=[True, True, True, True]
        self.adc_flg=[True, True, True, True]
        self.fe_flg=[True, True, True, True]
        self.align_flg=True

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

    def wib_zynq_mon(self):
        t_mult=509.3140064
        t_sub=280.23087870
        two_b=2**16
        rdreg = self.peek(0xA00C00D4) #temp
        sm_temp = (rdreg&0xffff)*t_mult/two_b - t_sub
        sm_vccint = ((rdreg>>16)&0xffff)*3.0/65536
        rdreg = self.peek(0xA00C00D8) #temp
        sm_vccaux = (rdreg&0xffff)*3.0/65536
        sm_vccbram = ((rdreg>>16)&0xffff)*3.0/65536
        return sm_temp, sm_vccint, sm_vccaux, sm_vccbram

    def wib_i2c_adj(self, n = 300):
        rdreg = self.peek(0xA00C0004)
        for i in range(n):
            self.poke(0xA00C0004 , rdreg|0x00040000) 
            rdreg = self.peek(0xA00C0004)
            time.sleep(0.001)
            self.poke(0xA00C0004 , rdreg&0xfffBffff) 

    def wib_femb_link_en(self, fembs):
        link_mask=self.peek(0xA00C0008) 
        self.poke(0xA00C0008, link_mask&0xffff0000)
        time.sleep(0.1)
        link_mask=self.peek(0xA00C0008) 
        link_mask=link_mask|0xffff 
        time.sleep(0.1)
        if 0 in fembs: 
            link_mask = link_mask&0xfffffff0
        if 1 in fembs: 
            link_mask = link_mask&0xffffff0f
        if 2 in fembs: 
            link_mask = link_mask&0xfffff0ff
        if 3 in fembs: 
            link_mask = link_mask&0xffff0fff
        self.poke(0xA00C0008, link_mask)
        link_mask = self.peek(0xA00C0008)
        print ("WIB FEMB LINK = %x"%link_mask)
        return link_mask
 

    def wib_fake_ts_en(self):
        print ("Enable fake timing system")
        rdreg = self.peek(0xA00c000C)
        #disable fake time stamp
        self.poke(0xA00c000C, (rdreg&0xFFFFFFF1))
        #set the init time stamp
        #self.poke(0xA00c0018, 0x00000000)
        #self.poke(0xA00c001C, 0x00000000)
        now = datetime.now()
        init_ts = int(datetime.timestamp(now) * 1e9)
        init_ts = time.time_ns()
        init_ts = init_ts//16 #WIB system clock is 62.5MHz

        self.poke(0xA00C0018, init_ts&0xffffffff)
        self.poke(0xA00C001c, (init_ts>>32)&0xffffffff)

        #enable fake time stamp
        self.poke(0xA00c000C, (rdreg|0x02))

    def wib_timing(self, ts_clk_sel=False, fp1_ptc0_sel=0, cmd_stamp_sync = 0x7fff):
        #See WIB_firmware.docx table 4.9.1 ts_clk_sel
        # 0[ts_clk_sel=False]  = CDR recovered clock(default)
        # 1[ts_clk_sel=True]   = PLL clock synchronized with CDR or running independently if CDR clock is 
        # missing. PLL clock should only be used on test stand when timing master 
        # is not available.            
        if ts_clk_sel == True:
            reg_read = self.peek(0xA00C0004)
            val = (reg_read&0xFFFEFFFF) | (int(ts_clk_sel) << 16)
            self.poke(0xA00C0004, val)    
            self.poke(0xA00C0004, val)    

            print ("PLL clock synchronized with CDR or running independently if CDR clock is missing")
            print ("PLL clock should only be used on test stand when timing master is not available.")
            self.wib_fake_ts_en()
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
            rdreg = rdreg & 0xFFFEFFFF #external clock from DTS is chosen
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
            self.poke(0xA00c000C, (rdreg&0xFFFFFFF1))
            rdreg = self.peek(0xA00c000C)
            #set the init time stamp
            #align_en = 1, cmd_stamp_sync_en = 1
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
        self.poke(0xA00C0004, rdreg&0xffffcfff)
        self.poke(0xA00C0004, rdreg|0x00003000)
        self.poke(0xA00C0004, rdreg&0xffffcfff)
        rdreg = self.peek(0xA00C0004)
        #print ("coldata_rx_reset = 0x%08x"%rdreg)
        time.sleep(0.1)

        #reset FELIX TX and loopback RX
        rdreg = self.peek(0xA00C0038)
        #print ("felix_rx_reset = 0x%08x"%rdreg)
        self.poke(0xA00C0038, rdreg&0xffffffdf)
        self.poke(0xA00C0038, rdreg|0x00000040)
        self.poke(0xA00C0038, rdreg&0xffffffdf)
        rdreg = self.peek(0xA00C0038)
        #print ("felix_rx_reset = 0x%08x"%rdreg)
        time.sleep(0.1)

        return self.peek(0xA00C0004)

    def wib_timing_wrap(self ):
        with open("./timing.cfg", "r") as fp:
            rd = fp.readline()
            rds = rd.split(",")
            ts_clk_sel=int(rds[0])
            fp1_ptc0_sel = int(rds[1])
            cmd_stamp_sync = int(rds[2])
        self.wib_timing(ts_clk_sel=ts_clk_sel, fp1_ptc0_sel=fp1_ptc0_sel, cmd_stamp_sync= cmd_stamp_sync)

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

            for femb_id in fembs:
                self.femb_power_en_ctrl(femb_id=femb_id, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
                print ("FEMB%d is on"%femb_id)
                time.sleep(1)
            fembs_off = []
            for i in range(4):
                if i not in fembs:
                    fembs_off.append(i)

            for femb_off_id in fembs_off:
                self.femb_power_en_ctrl(femb_id=femb_off_id, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=1 )
                print ("FEMB%d is off"%femb_off_id)
            if len(fembs_off) > 0 :
                time.sleep(2)
            for femb_off_id in fembs_off:
                self.femb_power_en_ctrl(femb_id=femb_off_id, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
           
            #enable WIB data link
            self.wib_femb_link_en(fembs)
            time.sleep(0.1)
            self.wib_timing_wrap()

            self.femb_cd_rst()
#            for femb_id in fembs:
#                self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
#                self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
#                self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")

        else:
            for femb_off_id in range(4):
                self.femb_power_en_ctrl(femb_id=femb_off_id, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
                print ("FEMB%d is off"%femb_off_id)
            time.sleep(3)
           # for femb_off_id in range(4):
           #     self.femb_power_en_ctrl(femb_id=femb_off_id, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
           # time.sleep(1)
            self.all_femb_bias_ctrl(enable=0 )

#    def get_sensors(self):
        #print ("Power configuration measurement is not ready yet...")
        #return None

    def femb_powering_single(self, femb_id, act):
        if act=='on':
            self.all_femb_bias_ctrl(enable=1 )

            self.femb_power_en_ctrl(femb_id=femb_id, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1 )
            time.sleep(1)
            print ("FEMB%d is on"%femb_id)
            
            #enable WIB data link
            #fembs=[femb_id]
            #self.wib_femb_link_en(fembs)
            #time.sleep(0.1)
            #self.wib_timing_wrap()

            #self.femb_cd_rst()

        if act=='off':
            self.femb_power_en_ctrl(femb_id=femb_id, vfe_en=0, vcd_en=0, vadc_en=1, bias_en=0 )
            time.sleep(2)
            self.femb_power_en_ctrl(femb_id=femb_id, vfe_en=0, vcd_en=0, vadc_en=0, bias_en=0 )
            print ("FEMB%d is off"%femb_id)
            time.sleep(1)

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

    def wib_cali_dac(self, dacvol= 0, ref=2.048):
        dacbit = int((dacvol/ref)*2**16)
        dacv = (dacbit&0xffff)<<16
        rdreg = self.peek(0xA00C003C)
        wrreg = (rdreg&0x0000ffff) + dacv
        self.poke(0xA00C003C, wrreg)
        time.sleep(0.001)
        while True:
            rdreg = self.peek(0xA00C0090)
            cal_dac_busy = (rdreg>>20)&0x01 
            if cal_dac_busy == 0:
                break
            else:
                time.sleep(0.001)
        rdreg = self.peek(0xA00C0004)
        #set bit22(cal_dac) to 1 and then to 0 to start monitring ADC conversion
        self.poke(0xA00C0004,(rdreg&0xffBfffff)|0x400000) #Set bit22 to 1
        self.poke(0xA00C0004,rdreg&0xfffBffff) #set bit22 to 0
        time.sleep(0.001)

    def wib_pls_gen(self, fembs=[0,1,2,3], cp_period=500, cp_phase=0, cp_high_time=500*16/2):
        if cp_period <= 1:
            cp_period = 1
        cp_period = cp_period - 1
        cp_period_regaddr = 0xA00C0040
        rdreg = self.peek(cp_period_regaddr)
        wrreg = (rdreg&0xffe00000) + (cp_period&0x1fffff)
        self.poke(cp_period_regaddr, wrreg) 

        cp_high_time_regaddr = 0xA00C0044
        rdreg = self.peek(cp_high_time_regaddr)
        wrreg = (rdreg&0xfC000000) + (int(cp_high_time)&0x3ffffff)
        self.poke(cp_high_time_regaddr, wrreg) 
        
        rdreg = self.peek(0xA00C003C)
        wrreg = (rdreg&0xffff803f)
        for fembid in fembs:
            if fembid == 0:
                wrreg = wrreg | 0x800
            if fembid == 1:
                wrreg = wrreg | 0x1000
            if fembid == 2:
                wrreg = wrreg | 0x2000
            if fembid == 3:
                wrreg = wrreg | 0x4000
        wrreg = wrreg|((cp_phase&0x1f)<<6)
        self.poke(0xA00C003C, wrreg)
        for fembid in fembs:
            self.femb_cd_gpio(femb_id=fembid, cd1_0x26 = 0x01,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)
        time.sleep(0.05)


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
        self.adac_cali_quo = [False,False,False,False]
        time.sleep(0.05)
        self.cd_flg=[True, True, True, True]
        self.adc_flg=[True, True, True, True]
        self.fe_flg=[True, True, True, True]
        self.align_flg = True 

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

    def femb_cd_chkreg(self, femb_id):

        print("Check femb%d COLDATA default registers' value"%femb_id)
        reg_pages=range(0,6)
        # page 0 registers
        reg_addr0=[0x01,0x03,0x11,0x1f,0x20,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x18,0x19,0x1a,0x1b,0x21,0x22,0x23]
        # page 0 registers default value
        reg_dval0=[0x00,0x28,0x02,0x00,0x00,0x20,0x00,0x00,0x20,0x20,0xff,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        # page 5 registers
        reg_addr5=range(0x40,0x55)
        # page 5 registers default value
        reg_dval5=[0x03,0x20,0x02,0x02,0x00,0x00,0x01,0x00,0x03,0x07,0x00,0x02,0x00,0x00,0x01,0x00,0x00,0x0f,0x00,0x01,0x01]
        # page 5 registers value bits
        reg_nbit5=[0x07,0x3f,0x03,0x03,0x01,0x01,0x01,0x01,0x07,0x07,0x0f,0x0f,0x07,0x0f,0x01,0x01,0x07,0x0f,0x01,0x01,0x01]
        # page 1-4 registers
        reg_addr1=[0x06,0x07,0x08,0x09,0x0b,0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,0x90,0x91]
        # page 1-4 registers default value
        reg_dval1=[0]*len(reg_addr1)

        hasERROR = False
        for chip_addr in [2,3]:
            for reg_page in reg_pages:
                nreg=0
                if reg_page==0:
                   for reg_addr in reg_addr0:
                       rdreg = self.femb_i2c_rd(femb_id, chip_addr, reg_page, reg_addr)
                       defreg = reg_dval0[nreg]
                       if rdreg!=defreg:
                          print("ERROR: femb {} chip {} CD page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, chip_addr, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                          hasERROR = True
                       nreg = nreg+1 

                if reg_page==5:
                   for reg_addr in reg_addr5:
                       rdreg = self.femb_i2c_rd(femb_id, chip_addr, reg_page, reg_addr)
                       rdreg = rdreg & reg_nbit5[nreg]
                       defreg = reg_dval5[nreg]
                       if rdreg!=defreg:
                          print("ERROR: femb {} chip {} CD page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, chip_addr, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                          hasERROR = True
                       nreg = nreg+1 

                if reg_page>0 and reg_page<5:
                   for reg_addr in reg_addr1:
                       rdreg = self.femb_i2c_rd(femb_id, chip_addr, reg_page, reg_addr)
                       defreg = reg_dval1[nreg]
                       if rdreg!=defreg:
                          print("ERROR: femb {} chip {} CD page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, chip_addr, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                          hasERROR = True
                       nreg = nreg+1 

        return hasERROR

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
        self.cd_flg[femb_id]=False

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
        align_sts = True
        while align_sts:
            #note032123: to be optimized 
            link_mask=self.peek(0xA00C0008) 
            if 0 in fembs:
                link_mask = link_mask&0xfffffff0
            if 1 in fembs:
                link_mask = link_mask&0xffffff0f
            if 2 in fembs:
                link_mask = link_mask&0xfffff0ff
            if 3 in fembs:
                link_mask = link_mask&0xffff0fff
            self.poke(0xA00C0008, link_mask)
            link_mask = self.peek(0xA00C0008 )
            time.sleep(0.01)

            self.femb_cd_sync() #sync should be sent before edge
            time.sleep(0.01)
            self.femb_cd_edge()
            time.sleep(0.1)

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
                
            for dts_time_delay in  range(0x47, 0x80,1):
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

                if ((link0to3 & 0xe0e0e0e0) == 0) and ((link4to7 & 0xe0e0e0e0) == 0)and ((link8tob & 0xe0e0e0e0) == 0) and ((linkctof & 0xe0e0e0e0) == 0) and (dts_time_delay >= 0x48):
                    print ("Data is aligned when dts_time_delay = 0x%x"%dts_time_delay )
                    rdaddr = 0xA00C000C
                    rdreg = self.peek(rdaddr)
                    wrvalue = 0x0 #cmd_stamp_sync_en = 1 disable SYNC
                    wrreg = (rdreg & 0xfffffffb) + ((wrvalue&0x1)<<2)
                    self.poke(rdaddr, wrreg) 
                    self.poke(rdaddr, wrreg) 
                    align_sts = False
                    break
                if dts_time_delay >= 0x7f:
                    #self.femb_powering(fembs =[])
                    print ("\033[91m" + "Error: data can't be aligned, re-initilize the clock again." + "\033[0m")
                    #self.wib_timing(ts_clk_sel=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)
                    self.wib_timing_wrap()
                    time.sleep(0.1)
                    #exit()


    def femb_adc_chkreg(self, femb_id):

        print("Check femb%d COLDADC default registers' value"%femb_id)

        # page 1 registers
        #reg_addr1=range(0x80,0xB7)
        reg_addr1=range(0x80,0xB3) #ignore B3, B4, B5, B6
        # page 1 registers default value
        #reg_dval1=[0xA3,0x00,0x00,0x00,0x33,0x33,0x33,0x33,0x0B,0x00,0xF1,0x29,0x8D,0x65,0x55,0xFF,0xFF,0xFF,0xFF,0x04,0x00,0x00,0xFF,0x2F,0xDF,0x33,0x89,0x67,0x15,0xFF,0xFF,0x00,0x7F,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x10,0x00,0xCD,0xAB,0x34,0x12]
        reg_dval1=[0xA3,0x00,0x00,0x00,0x33,0x33,0x33,0x33,0x0B,0x00,0xF1,0x29,0x8D,0x65,0x55,0xFF,0xFF,0xFF,0xFF,0x04,0x00,0x00,0xFF,0x2F,0xDF,0x33,0x89,0x67,0x15,0xFF,0xFF,0x00,0x7F,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x10,0x00]
        
        # page 2 registers
        reg_addr2=range(1,5)
        # page 2 registers default value
        reg_dval2=[0x10,0x04,0x00,0x00]
       
        hasERROR = False 
        for adc_no in range(8):
            c_id = self.adcs_paras[adc_no][0]

            reg_page=1
            nreg=0
            for reg_addr in reg_addr1:
                rdreg = self.femb_i2c_rd(femb_id, c_id, reg_page, reg_addr)
                defreg = reg_dval1[nreg]
                nreg = nreg+1
                if rdreg!=defreg:
                   print("ERROR: femb {} chip {} ADC page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, c_id, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                   hasERROR = True

            reg_page=2
            nreg=0
            for reg_addr in reg_addr2:
                rdreg = self.femb_i2c_rd(femb_id, c_id, reg_page, reg_addr)
                defreg = reg_dval2[nreg]
                nreg = nreg+1
                if rdreg!=defreg:
                   print("ERROR: femb {} chip {} ADC page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, c_id, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                   hasERROR = True

        return hasERROR

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
        self.adc_flg[femb_id]=False

    def fembs_fe_cfg(self, fembs):
        fe_adac_ens = [False, False, False, False]
        for femb_id in fembs:
            if self.adac_cali_quo[femb_id]:
                self.femb_cd_fc_act(femb_id, act_cmd="larasic_pls")
                self.adac_cali_quo[femb_id]=False
                fe_adac_ens[femb_id] = True

        #reset LARASIC chips
        for femb_id in fembs:
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
        time.sleep(0.001)
        for femb_id in fembs:
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
        time.sleep(0.001)
        for femb_id in fembs:
            #program LARASIC chips
            for chip in range(8):
                for reg_id in range(16+2):
                    if (chip < 4):
                        rdreg = self.femb_i2c_rd(femb_id, chip_addr=3, reg_page=(chip%4+1), reg_addr=(0x91-reg_id))
                        if rdreg != self.regs_int8[chip][reg_id]:
                            self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
                    else:
                        rdreg = self.femb_i2c_rd(femb_id, chip_addr=2, reg_page=(chip%4+1), reg_addr=(0x91-reg_id))
                        if rdreg != self.regs_int8[chip][reg_id]:
                            self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
        i = 0
        prg_flg = True
        while prg_flg:
            for femb_id in fembs:
                self.femb_cd_fc_act(femb_id, act_cmd="clr_saves")
            time.sleep(0.001)
            for femb_id in fembs:
                self.femb_cd_fc_act(femb_id, act_cmd="prm_larasics")
            time.sleep(0.005)
            for femb_id in fembs:
                self.femb_cd_fc_act(femb_id, act_cmd="save_status")
            time.sleep(0.002)

            for femb_id in fembs:
                sts_cd1 = self.femb_i2c_rd(femb_id, chip_addr=3, reg_page=0, reg_addr=0x24)
                sts_cd2 = self.femb_i2c_rd(femb_id, chip_addr=2, reg_page=0, reg_addr=0x24)

                if (sts_cd1&0xff == 0xff) and (sts_cd2&0xff == 0xff):
                    prg_flg = False
                else:
                    prg_flg = True
                    print ("\033[91m" + "FEMB{}, LArASIC readback status is {}, {} diffrent from 0xFF".format(femb_id, sts_cd1, sts_cd2) + "\033[0m")
                    if i > 10:
                        #self.femb_powering(fembs =[])
                        #print ("Turn all FEMBs off, exit anyway")
                        print ("exit anyway")
                        exit()
                    else:
                        time.sleep(0.01)
            i = i + 1
        self.fe_flg[femb_id]=False
        for femb_id in fembs:
            if fe_adac_ens[femb_id]:
                self.femb_adac_cali(femb_id)
                fe_adac_ens[femb_id] = False


    def femb_fe_cfg(self, femb_id):
        fe_adac_en = False
        if self.adac_cali_quo[femb_id]:
            self.femb_cd_fc_act(femb_id, act_cmd="larasic_pls")
            self.adac_cali_quo[femb_id]=False
            fe_adac_en = True
 
        #reset LARASIC chips
        self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
        time.sleep(0.001)
        self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
        #program LARASIC chips
        time.sleep(0.001)
        for chip in range(8):
            for reg_id in range(16+2):
                if (chip < 4):
                    rdreg = self.femb_i2c_rd(femb_id, chip_addr=3, reg_page=(chip%4+1), reg_addr=(0x91-reg_id))
                    if rdreg != self.regs_int8[chip][reg_id]:
                        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
                else:
                    rdreg = self.femb_i2c_rd(femb_id, chip_addr=2, reg_page=(chip%4+1), reg_addr=(0x91-reg_id))
                    if rdreg != self.regs_int8[chip][reg_id]:
                        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=(chip%4+1), reg_addr=(0x91-reg_id), wrdata=self.regs_int8[chip][reg_id])
        i = 0
        while True:
            self.femb_cd_fc_act(femb_id, act_cmd="clr_saves")
            time.sleep(0.001)
            self.femb_cd_fc_act(femb_id, act_cmd="prm_larasics")
            time.sleep(0.005)
            self.femb_cd_fc_act(femb_id, act_cmd="save_status")
            time.sleep(0.002)

            sts_cd1 = self.femb_i2c_rd(femb_id, chip_addr=3, reg_page=0, reg_addr=0x24)
            sts_cd2 = self.femb_i2c_rd(femb_id, chip_addr=2, reg_page=0, reg_addr=0x24)

            if (sts_cd1&0xff == 0xff) and (sts_cd2&0xff == 0xff):
                break
            else:
                print ("\033[91m" + "LArASIC readback status is {}, {} diffrent from 0xFF".format(sts_cd1, sts_cd2) + "\033[0m")
                if i > 10:
                    #self.femb_powering(fembs =[])
                    #print ("Turn all FEMBs off, exit anyway")
                    print ("exit anyway")
                    exit()
                else:
                    time.sleep(0.01)
            i = i + 1
        self.fe_flg[femb_id]=False
        if fe_adac_en:
            self.femb_adac_cali(femb_id)
            fe_adac_en = False

    def femb_adac_cali(self, femb_id, phase0x07=[0,0,0,0,0,0,0,0]):
        for chip in range(8):
            #period (how many samples per pls) = value(addr 0x6) + (((v(0x08)<<8)+v(0x09))//32)
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x6, wrdata=0x30        )
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x7, wrdata=phase0x07[chip])
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x8, wrdata=0x38        )
            self.femb_i2c_wrchk(femb_id, chip_addr=3-(chip//4), reg_page=(chip%4+1), reg_addr=0x9, wrdata=0x80        )
        self.femb_cd_fc_act(femb_id, act_cmd="larasic_pls")
        self.adac_cali_quo[femb_id] = not self.adac_cali_quo[femb_id] 


    def femb_cfg(self, femb_id, adac_pls_en = False):
        refi= 0
        while True:
            #note032123: to be optimized 
            #link_mask=self.peek(0xA00C0008) 
            #if femb_id == 0:
            #    link_mask = link_mask&0xfffffff0
            #if femb_id == 1:
            #    link_mask = link_mask&0xffffff0f
            #if femb_id == 2:
            #    link_mask = link_mask&0xfffff0ff
            #if femb_id == 3:
            #    link_mask = link_mask&0xffff0fff
            #self.poke(0xA00C0008, link_mask)
            #link_mask = self.peek(0xA00C0008 )
            #time.sleep(0.01)

            if self.cd_flg[femb_id]:
                self.femb_cd_cfg(femb_id)
            if self.adc_flg[femb_id]:
                self.femb_adc_cfg(femb_id)
            if self.fe_flg[femb_id]:
                self.femb_fe_cfg(femb_id)
            if adac_pls_en and (not (self.adac_cali_quo[femb_id])) :
                self.femb_adac_cali(femb_id)
            time.sleep(0.005)

            #self.femb_cd_sync()
            if self.i2cerror:
                self.cd_flg[femb_id] = True
                self.adc_flg[femb_id] =True
                self.fe_flg[femb_id] =True
                self.i2cerror = False
                refi += 1
                print ("add i2c phase 50 steps")
                if refi > 3:
                    self.wib_i2c_adj(n=50)
                    print ("Reconfigure FEMB due to i2c error!")
                if refi > 25:
                    #self.femb_powering(fembs =[])
                    print ( "\033[91m" + "I2C failed! exit anyway, please check connection!" + "\033[0m")
                    exit()
            else:
                print (f"FEMB{femb_id} is configurated")
                break

    def femb_fe_mon(self, femb_id=0, adac_pls_en = 0, rst_fe=0, mon_type=2, mon_chip=0, mon_chipchn=0, snc=0,sg0=0, sg1=0, sdf=1 ):
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
        self.set_fechn_reg(chip=mon_chip&0x07, chn=chn, snc=snc, sg0=sg0, sg1=sg1, smn=1, sdf=sdf) 
        self.set_fechip_global(chip=mon_chip&0x07, stb1=stb1, stb=stb0)
        self.set_fe_sync()

        self.femb_fe_cfg(femb_id)
        self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)

    def fembs_fe_mon(self, fembs=[0,1,2,3], adac_pls_en = 0, rst_fe=0, mon_type=2, mon_chip=0, mon_chipchn=0, snc=0,sg0=0, sg1=0, sdf=1 ):
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
        self.set_fechn_reg(chip=mon_chip&0x07, chn=chn, snc=snc, sg0=sg0, sg1=sg1, smn=1, sdf=sdf) 
        self.set_fechip_global(chip=mon_chip&0x07, stb1=stb1, stb=stb0)
        self.set_fe_sync()

        self.fembs_fe_cfg(fembs)
        for femb_id in fembs:
            self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)

    def wib_fe_mon(self, femb_ids=[0,1,2,3], adac_pls_en = 0, rst_fe=0, mon_type=2, mon_chip=0, mon_chipchn=0, snc=0,sg0=0, sg1=0, sdf=1, sps=10 ):
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0) 
        #step 1
        #reset all FEMBs on WIB
        self.femb_cd_rst()
        
        #step 2
        #for femb_id in femb_ids:
        #    self.femb_fe_mon(femb_id, adac_pls_en, rst_fe, mon_type, mon_chip, mon_chipchn, snc,sg0, sg1, sdf )
        self.fembs_fe_mon(femb_ids, adac_pls_en, rst_fe, mon_type, mon_chip, mon_chipchn, snc,sg0, sg1, sdf )
        #step4
        if self.longcable:
            time.sleep(0.5)
        else:
            time.sleep(0.05)
        adcss = []
        self.wib_mon_adcs() #get rid of previous result
        for i in range(sps):
            adcs = self.wib_mon_adcs()
            adcss.append(adcs)
        if mon_type == 2:
            mon_str = "VBGR"
        elif mon_type == 1:
            mon_str = "Temperature"
        else:
            mon_str = "Channel"
        mon_paras = [mon_str, mon_chip, mon_chipchn, snc, sg0, sg1, sps, adcss]
        self.wib_mon_switches()
        return mon_paras

    def wib_fe_dac_mon(self, femb_ids, mon_chip=0,sgp=False, sg0=0, sg1=0, vdacs=range(64), sps = 3 ): 
        self.wib_mon_switches(dac0_sel=1,dac1_sel=1,dac2_sel=1,dac3_sel=1, mon_vs_pulse_sel=0, inj_cal_pulse=0) 
        self.set_fe_reset()
        self.set_fe_board(sg0=sg0, sg1=sg1)
        #step 1
        #reset all FEMBs on WIB
        self.femb_cd_rst()
        #step 2
        vdac_mons = []

        for vdac in vdacs:
            self.set_fechip_global(chip=mon_chip&0x07, swdac=3, dac=vdac, sgp=sgp)
            self.set_fe_sync()

            self.fembs_fe_cfg(femb_ids)
            for femb_id in femb_ids:
           #     self.femb_fe_cfg(femb_id)
                self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)
            #step4

            if self.longcable:
                time.sleep(0.5)
            else:
                time.sleep(0.05)
                pass
            adcss = []
            self.wib_mon_adcs() #get rid of previous result
            for i in range(sps):
                adcs = self.wib_mon_adcs()
                adcss.append(adcs)
            vdac_mons.append(["ASICDAC", mon_chip, vdac, sps, adcss])
        self.wib_mon_switches()
        return vdac_mons

    def femb_adc_mon(self, femb_id, mon_chip=0, mon_i=0  ):
        adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07]  
        cd2_iobit432 = [6,4,5,7,3,1,0,2]
        self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x04,cd1_0x27 = 0x1f, cd2_0x26 = cd2_iobit432[mon_chip]<<2,cd2_0x27 = 0x1f)
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

    def wib_vol_mon(self, femb_ids, sps=10 ):
        vms = ["CDVDDA", "CDVDDIO_HALF", "ADCRVDDD1P2", "ADCLVDDD1P2", "FERVDDP", "FELVDDP", "ADCRP25V_HALF", "ADCLP25V_HALF", "GND"]
        vols=[0x01, 0x03, 0x09, 0x0b, 0x11, 0x13, 0x19, 0x1b]
        vms_dict = {}
        for volcs in range (len(vms)):
            print (f"Monitor Power Rail of {vms[volcs]}")
            for femb_id in femb_ids:
                if "GND" in vms[volcs]:
                    self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x02,cd1_0x27 = 0x1f, cd2_0x26 =0x00 ,cd2_0x27 = 0x1f)
                else:
                    self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x04,cd1_0x27 = 0x1f, cd2_0x26 =vols[volcs] ,cd2_0x27 = 0x1f)

            if self.longcable:
                time.sleep(0.5)
            else:
                time.sleep(0.05)
            self.wib_mon_adcs() #get rid of previous result
            adcss = []
            for i in range(sps):
                adcs = self.wib_mon_adcs()
                adcss.append(adcs)
            vms_dict[f"{vms[volcs]}"] = adcss
        for femb_id in femb_ids:
            self.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 =00 ,cd2_0x27 = 0x1f)
        return vms_dict

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
                for femb_id in femb_ids:
                    self.femb_adc_cfg(femb_id)
                    self.femb_adc_mon(femb_id, mon_chip=mon_chip, mon_i=mon_i  )
                    #print (f"FEMB{femb_id} is configurated")
                adcss = []
                #time.sleep(1)
                if self.longcable:
                    time.sleep(0.5)
                else:
                    time.sleep(0.05)
                self.wib_mon_adcs() #get rid of previous result
                for i in range(sps):
                    adcs = self.wib_mon_adcs()
                    adcss.append(adcs)
                mon_dict[f"chip{mon_chip}"] = [mon_chip, mons[mon_i], self.adcs_paras[mon_chip], adcss]
             #   print (mon_dict[f"chip{mon_chip}"])
            mon_items.append(mon_dict)
        self.wib_mon_switches()
        return mon_items

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
            #time.sleep(1)
            if self.longcable:
                time.sleep(0.5)
            else:
                time.sleep(0.05)

            self.wib_mon_adcs() #get rid of previous result
            for i in range(sps):
                adcs = self.wib_mon_adcs()
                adcss.append(adcs)
            mon_dict[mons[mon_i]] = [self.adcs_paras[mon_chip], adcss]
        self.wib_mon_switches()
        return mon_dict

#    def spybuf_idle(self, fembs): 
#        for tmp in range(1):
#             self.poke(0xA00C0024, 0x7fff) #spy rec time
#             rdreg = self.peek(0xA00C0004)
#             wrreg = (rdreg&0xffffffbf)|0x40 #NEW FW
#             self.poke(0xA00C0004, wrreg) #reset spy buffer
#             rdreg = self.peek(0xA00C0004)
#             wrreg = rdreg&0xffffffbf #NEW FW
#             self.poke(0xA00C0004, wrreg) #release spy buffer
#             time.sleep(0.001) #NEW FW
#             rdreg = self.peek(0xA00C0004)
#             wrreg = (rdreg&0xffffffbf)|0x40 #NEW FW
#             self.poke(0xA00C0004, wrreg) #reset spy buffer
#             self.spybuf(fembs)
#
    def spybuf_trig(self, fembs, num_samples=1, trig_cmd=0x08, spy_rec_ticks=0x7fff, fastchk=True): 
        synctry = 0
        while True:
	    #spy_rec_ticks subject to change
	    #(spy_rec_ticks register now only 15 bits instead of 18)
            if trig_cmd == 0x00:
                #print (f"Data collection for FEMB {fembs} with software trigger")
                pass
            elif trig_cmd != 0xff:
                #print (f"Data collection for FEMB {fembs} with trigger from DTS") 
                pass
            if trig_cmd == 0xFF: #P11 trigger
                #print (f"Data collection for FEMB {fembs} with trigger from P11") 
                rdreg = self.peek(0xA00C0004)   
                wrreg = (rdreg&0xfbffffff)|0x2000000 #NEW FW
                self.poke(0xA00C0004, wrreg) #Eanble syp memory trigger from P11 connector
            else:
                rdreg = self.peek(0xA00C0004)   
                wrreg = rdreg&0xfbffffff
                self.poke(0xA00C0004, wrreg) 

            rdreg = self.peek(0xA00C0014)
            wrreg = (rdreg&0xff00ffff)|(trig_cmd<<16)|0x40000000
            self.poke(0xA00C0014, wrreg) #program cmd_code_trigger     
	    
            data = []    
            for i in range(num_samples):
                if trig_cmd == 0x00: #SW
                    self.poke(0xA00C0024, spy_rec_ticks) #spy rec time
                    rdreg = self.peek(0xA00C0004)
                    wrreg = (rdreg&0xffffffbf)|0x40 #NEW FW
                    self.poke(0xA00C0004, wrreg) #reset spy buffer
                    rdreg = self.peek(0xA00C0004)
                    wrreg = rdreg&0xffffffbf #NEW FW
                    self.poke(0xA00C0004, wrreg) #release spy buffer
                    time.sleep(0.003) #NEW FW
                    rdreg = self.peek(0xA00C0004)
                    wrreg = (rdreg&0xffffffbf)|0x40 #NEW FW
                    self.poke(0xA00C0004, wrreg) #reset spy buffer
                    rawdata = self.spybuf(fembs)
                    data.append((rawdata, 0, spy_rec_ticks, 0x00))    
                else: #HW
                    #print ("DTS trigger mode only supports 4 FEMBs attached")
                    rdreg = self.peek(0xA00C0004)   
                    wrreg = (rdreg&0xffffffbf)|0x40 #NEW FW
                    self.poke(0xA00C0004, wrreg)
                    rdreg = self.peek(0xA00C0004)
                    wrreg = rdreg&0xffffffbf #NEW FW
                    self.poke(0xA00C0004, wrreg) #release spy buffer
                    self.poke(0xA00C0024, spy_rec_ticks) #spy rec time
                    time.sleep(0.005)
	    
                    while True:
                        spy_full_flgs = False
                        rdreg = self.peek(0xA00C0080)
                        fullsig = 0x00
                        for fembid in fembs:
                            if fembid == 0:
                                fullsig = fullsig|0x03
                            if fembid == 1:
                                fullsig = fullsig|0x18
                            if fembid == 2:
                                fullsig = fullsig|0x60
                            if fembid == 3:
                                fullsig = fullsig|0x180
                        
                        if rdreg&0x1fb == fullsig:
                            print ("Recived %d of %d triggers"%((i+1), num_samples))
                            spy_full_flgs = True
                            spy_addr_regs = [0xA00C0094, 0xA00C0098, 0xA00C00CC, 0xA00C00D0]
                            buf_end_addrs = [0, 0, 0, 0, 0, 0, 0, 0 ]
                            for fembid in fembs:
                                femb_buf_end_addrs =  self.peek(spy_addr_regs[fembid])                  
                                buf_end_addrs[fembid*2] = femb_buf_end_addrs&0x7fff                 
                                buf_end_addrs[fembid*2+1] = (femb_buf_end_addrs>>16)&0x7fff                 
                            syncfemb = True
                            tmpend = buf_end_addrs[fembs[0]*2] 
                            for fembid in fembs:
                                if (tmpend != buf_end_addrs[fembid*2]) and (tmpend !=buf_end_addrs[fembid*2+1]):
                                    syncfemb = False
                            if syncfemb:
                                rawdata = self.spybuf(fembs)
                                data0 = (rawdata, buf_end_addrs[fembs[0]*2], spy_rec_ticks, trig_cmd)
                                data.append(data0)
                            else:
                                print("buffers out of sync")
                                pass
                        else:
                            spy_full_flgs = False
                        if spy_full_flgs:
                            break
                        else:
                            print ("No external trigger received, Wait a second ")
                            time.sleep(1)                
            if fastchk:
                syncsts = wib_dec(data, fembs=fembs, spy_num=1, fastchk=fastchk)

                if not syncsts : 
                    #self.spybuf_idle(fembs)  #useless but to assure refresh the data in spy buffer
                    synctry = synctry+1
                    if synctry > 100:
                        print ("Data can't be synchronzed, please contact tech coordinator... Exit anyway ")
                        exit()
                    if synctry%10 == 0:
                        print ("perform data synchronzation again...")
                        self.data_align(fembs)
                        time.sleep(1)
                else:
                    break
            else:
                break
        return data

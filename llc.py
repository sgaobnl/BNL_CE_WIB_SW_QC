import ctypes, ctypes.util
import struct, os

class LLC():
    def __init__(self):
        super().__init__()
        self.wib_path = os.getcwd() + "/build/wib_util.so"
        self.wib = ctypes.CDLL(self.wib_path)

        #define C functions' argument types and return types
        self.wib.peek.argtypes = [ctypes.c_size_t]
        self.wib.peek.restype = ctypes.c_uint32
        
        self.wib.poke.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
        self.wib.poke.restype = None

        self.wib.wib_peek.argtypes = [ctypes.c_size_t]
        self.wib.wib_peek.restype = ctypes.c_uint32
        
        self.wib.wib_poke.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
        self.wib.wib_poke.restype = None
      
        self.wib.cdpeek.argtypes = [ctypes.c_uint8,  ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        self.wib.cdpeek.restype = ctypes.c_uint8
        
        self.wib.cdpoke.argtypes = [ctypes.c_uint8,  ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        self.wib.cdpoke.restype = None  
        
        self.wib.bufread.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        self.wib.bufread.restype = None

        self.wib.i2cread.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        self.wib.i2cread.restype = ctypes.c_uint8
    
        self.wib.i2cwrite.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        self.wib.i2cwrite.restype = None

        self.wib.read_ltc2990.argtypes = [ctypes.c_uint8, ctypes.c_bool, ctypes.c_uint8]
        self.wib.read_ltc2990.restype = ctypes.c_double
    
        self.wib.read_ltc2991.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_bool, ctypes.c_uint8]
        self.wib.read_ltc2991.restype = ctypes.c_double    
    
        self.wib.read_ad7414.argtypes = [ctypes.c_uint8]
        self.wib.read_ad7414.restype = ctypes.c_double
     
        self.wib.read_ina226_c.argtypes = [ctypes.c_uint8]
        self.wib.read_ina226_c.restype = ctypes.c_double

        self.wib.read_ina226_v.argtypes = [ctypes.c_uint8]
        self.wib.read_ina226_v.restype = ctypes.c_double
   
        self.wib.read_ltc2499.argtypes = [ctypes.c_uint8]
        self.wib.read_ltc2499.restype = ctypes.c_double        

        self.wib.all_femb_bias_ctrl.argtypes = [ctypes.c_uint8 ]
        self.wib.all_femb_bias_ctrl.restype  = ctypes.c_bool

        self.wib.femb_power_en_ctrl.argtypes = [ctypes.c_int, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        self.wib.femb_power_en_ctrl.restype  = ctypes.c_bool

        self.wib.femb_power_reg_ctrl.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_double]
        self.wib.femb_power_reg_ctrl.restype = ctypes.c_bool
    
        self.wib.femb_power_config.argtypes = [ctypes.c_uint8, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double ]
        self.wib.femb_power_config.restype = ctypes.c_bool       

        self.wib.script_cmd.argtypes =  [ctypes.POINTER(ctypes.c_char) ] 
        self.wib.script_cmd.restype = ctypes.c_bool       
        self.wib.script.argtypes =  [ctypes.POINTER(ctypes.c_char), ctypes.c_bool  ] 
        self.wib.script.restype = ctypes.c_bool       

    def script_cmd(self, cmd):
        return self.wib.script_cmd(cmd)

    def script(self, fp, fp_flg=True): #false means argument is a raw script line
        return self.wib.script(fp, fp_flg)

    def peek(self, regaddr):
        val = self.wib.peek(regaddr)
        return val

    def poke(self, regaddr, regval):
        self.wib.poke(regaddr, regval)
        return None

    def wib_peek(self, regaddr):
        val = self.wib.wib_peek(regaddr)
        return val

    def wib_poke(self, regaddr, regval):
        self.wib.wib_poke(regaddr, regval)
        return None

#    def poke_chk(self, regaddr, regval):
#        self.poke(regaddr, regval)
#        val = self.peek(regaddr)
#        if val == regval:
#            return val
#        else:
#            print ("Error: WIB reg addr 0x%x readback value (0x%x) is different from write value (0x%x)"%(regaddr, regval, val))
#            return None

    def cdpeek(self, femb_id, chip_addr, reg_page, reg_addr):
        val = self.wib.cdpeek(femb_id, chip_addr, reg_page, reg_addr)
        return val

    def cdpoke(self, femb_id, chip_addr, reg_page, reg_addr, data):
        self.wib.cdpoke(femb_id, chip_addr, reg_page, reg_addr, data)
   
#    def cdpoke_chk(self, femb_id, chip_addr, reg_page, reg_addr, data):
#        for i in range(10):
#            self.wib.cdpoke(femb_id, chip_addr, reg_page, reg_addr, data)
#            val = self.wib.cdpeek(femb_id, chip_addr, reg_page, reg_addr)
#            if val == data:
#                return val
#            else:
#                print ("Warning: FEMB%d_chipI2C0x%x_page0x%x_addr0x%x readback(0x%x) is different from write value (0x%x)"%(femb_id, chip_addr, reg_page, reg_addr, regval, val))
#                print ("Try again...")
#                if i > 5: 
#                    print ("Error: Failed to configurate FEMB, please check hardware connection...")
#                    exit()

    def fastcmd(self, cmd):
        fast_dict = { 'reset':1, 'act':2, 'sync':4, 'edge':8, 'idle':16, 'edge_act':32 }        
        self.wib.poke(0xA0030000, fast_dict[cmd]) #fast command

#    def fastcmd_act(self, femb_id, act_cmd="idle"):
#        if act_cmd == "idle":
#            wrdata = 0
#        elif act_cmd == "larasic_pls":
#            wrdata = 0x01
#        elif act_cmd == "save_timestamp":
#            wrdata = 0x02
#        elif act_cmd == "save_status":
#            wrdata = 0x03
#        elif act_cmd == "clr_saves":
#            wrdata = 0x04
#        elif act_cmd == "rst_adcs":
#            wrdata = 0x05
#        elif act_cmd == "rst_larasics":
#            wrdata = 0x06
#        elif act_cmd == "rst_larasic_spi":
#            wrdata = 0x07
#        elif act_cmd == "prm_larasics":
#            wrdata = 0x08
#        elif act_cmd == "relay_i2c_sda":
#            wrdata = 0x09
#        else:
#            wrdata = 0
#
#        self.cdpoke_chk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=wrdata)
#        self.cdpoke_chk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=wrdata)
#        self.fastcmd(cmd='act')
#        #return to "idle" in case other FEMB runs FC 
#        self.cdpoke_chk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x20, wrdata=0)
#        self.cdpoke_chk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x20, wrdata=0)


    def spybuf(self, fembs= [0, 1,2,3]):
        buf0 = True if 0 in fembs or 1 in fembs else False
        buf1 = True if 2 in fembs or 3 in fembs else False 

        DAQ_SPY_SIZE = 0x00100000
        buf = (ctypes.c_char*DAQ_SPY_SIZE)()
        #allocate memory in python
        buf0_bytes = bytearray(DAQ_SPY_SIZE)
        buf1_bytes = bytearray(DAQ_SPY_SIZE)

        if buf0:
            self.wib.bufread(buf, 0) #read buf0
            byte_ptr0 = (ctypes.c_char*DAQ_SPY_SIZE).from_buffer(buf0_bytes)
            if not ctypes.memmove(byte_ptr0, buf, DAQ_SPY_SIZE):
                print('memmove failed')
                exit()

        if buf1:
            self.wib.bufread(buf, 1) #read buf1    
            byte_ptr1 = (ctypes.c_char*DAQ_SPY_SIZE).from_buffer(buf1_bytes)
            if not ctypes.memmove(byte_ptr1, buf, DAQ_SPY_SIZE):
                print('memmove failed')
                exit()
        return buf0_bytes, buf1_bytes

        
    def get_sensors(self):
        r357 = 0.001
        r350 = 0.001
        r351 = 0.001
        r413 = 0.001
        r416 = 0.001
        r352 = 0.001
        r353 = 0.001
        power_meas = { }
        ltc2990_4e_vs = []
        for i  in range(1,5,1):
            v = self.wib.read_ltc2990(0x4E, False, i) 
            ltc2990_4e_vs.append(v)
        power_meas["P0.9V_V"] = ltc2990_4e_vs[1]
        power_meas["P0.9V_I"] = (ltc2990_4e_vs[0] - ltc2990_4e_vs[1]) / r357
        power_meas["VCCPSPLL_Z_1P2V_V"] = ltc2990_4e_vs[2]
        power_meas["PS_DDR4_vtt_V"] = ltc2990_4e_vs[3]

        ltc2990_4c_vs = []
        for i  in range(1,5,1):
            v = self.wib.read_ltc2990(0x4C, False, i) 
            ltc2990_4c_vs.append(v)
        power_meas["P1.2V_V"] = ltc2990_4c_vs[1]
        power_meas["P1.2V_I"] = (ltc2990_4c_vs[0] - ltc2990_4c_vs[1])/r351
        power_meas["P3.3V_V"] = ltc2990_4c_vs[3]
        power_meas["P3.3V_I"] = (ltc2990_4c_vs[2] - ltc2990_4c_vs[3])/r350

        bus = 0
        ltc2991_48_vs = []
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x48, False, i) 
            ltc2991_48_vs.append(v)
        power_meas["P0.85V_V"] =  ltc2991_48_vs[1]
        power_meas["P0.85V_I"] = (ltc2991_48_vs[0] - ltc2991_48_vs[1])/r413
        power_meas["P5V_V"] =     ltc2991_48_vs[3]
        power_meas["P5V_I"] =    (ltc2991_48_vs[2] - ltc2991_48_vs[3])/r416
        power_meas["P2.5V_V"] =   ltc2991_48_vs[5]
        power_meas["P2.5V_I"] =  (ltc2991_48_vs[4] - ltc2991_48_vs[5])/r352
        power_meas["P1.8V_V"] =   ltc2991_48_vs[7]
        power_meas["P1.8V_I"] =  (ltc2991_48_vs[6] - ltc2991_48_vs[7])/r353

        vcco_psddr_504_c =  self.wib.read_ina226_c(0x46)
        vcco_psddr_504_v =  self.wib.read_ina226_v(0x46)
        power_meas["VCCO_PSDDR_504_V"] = vcco_psddr_504_c 
        power_meas["VCCO_PSDDR_504_I"] = vcco_psddr_504_v 

        ad7414_4d = self.wib.read_ad7414(0x4d)
        power_meas["Temp_U42_0x4d"] =  ad7414_4d

        if False:
            ad7414_49 = self.wib.read_ad7414(0x49)
            ad7414_4a = self.wib.read_ad7414(0x4a)
            power_meas["Temp_U47_0x49"] =  ad7414_49
            power_meas["Temp_U64_0x4a"] =  ad7414_4a

        ltc2499_15s = [] 
        for i  in range(0,7,1):
            t = self.wib.read_ltc2499(i)
            ltc2499_15s.append(t)
        power_meas["LTC4644_BRD0_temp"] = ltc2499_15s[0]
        power_meas["LTC4644_BRD1_temp"] = ltc2499_15s[1]
        power_meas["LTC4644_BRD2_temp"] = ltc2499_15s[2]
        power_meas["LTC4644_BRD3_temp"] = ltc2499_15s[3]
        power_meas["LTC4644_WIB1_temp"] = ltc2499_15s[4]
        power_meas["LTC4644_WIB2_temp"] = ltc2499_15s[5]
        power_meas["LTC4644_WIB3_temp"] = ltc2499_15s[6]

        bus = 2 #FEMB power monitoring
        bus2_ltc2991_48_vs = [] #DCDC for FEMB0
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x48, False, i) 
            bus2_ltc2991_48_vs.append(v)
        bus2_ltc2991_49_vs = [] #DCDC for FEMB1
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x49, False, i) 
            bus2_ltc2991_49_vs.append(v)
        bus2_ltc2991_4a_vs = [] #DCDC for FEMB2
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x4A, False, i) 
            bus2_ltc2991_4a_vs.append(v)
        bus2_ltc2991_4b_vs = [] #DCDC for FEMB3
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x4B, False, i) 
            bus2_ltc2991_4b_vs.append(v)
        bus2_ltc2991_4e_vs = [] #DCDC for FEMB BIAS(0-3)
        for i  in range(1,9,1):
            v = self.wib.read_ltc2991(bus, 0x4E, False, i) 
            bus2_ltc2991_4e_vs.append(v)
        power_meas["FEMB0_BIAS_V"]   =  bus2_ltc2991_4e_vs[1]
        power_meas["FEMB0_BIAS_I"]   = (bus2_ltc2991_4e_vs[0] - bus2_ltc2991_4e_vs[1])/0.1
        power_meas["FEMB0_DC2DC0_V"] =  bus2_ltc2991_48_vs[1]
        power_meas["FEMB0_DC2DC0_I"] = (bus2_ltc2991_48_vs[0] - bus2_ltc2991_48_vs[1])/0.1
        power_meas["FEMB0_DC2DC1_V"] =  bus2_ltc2991_48_vs[3]
        power_meas["FEMB0_DC2DC1_I"] = (bus2_ltc2991_48_vs[2] - bus2_ltc2991_48_vs[3])/0.1
        power_meas["FEMB0_DC2DC2_V"] =  bus2_ltc2991_48_vs[5]
        power_meas["FEMB0_DC2DC2_I"] = (bus2_ltc2991_48_vs[4] - bus2_ltc2991_48_vs[5])/0.01
        power_meas["FEMB0_DC2DC3_V"] =  bus2_ltc2991_48_vs[7]
        power_meas["FEMB0_DC2DC3_I"] = (bus2_ltc2991_48_vs[6] - bus2_ltc2991_48_vs[7])/0.1
        power_meas["FEMB1_BIAS_V"]   =  bus2_ltc2991_4e_vs[1]
        power_meas["FEMB1_BIAS_I"]   = (bus2_ltc2991_4e_vs[0] - bus2_ltc2991_4e_vs[1])/0.1
        power_meas["FEMB1_DC2DC0_V"] =  bus2_ltc2991_49_vs[1]
        power_meas["FEMB1_DC2DC0_I"] = (bus2_ltc2991_49_vs[0] - bus2_ltc2991_49_vs[1])/0.1
        power_meas["FEMB1_DC2DC1_V"] =  bus2_ltc2991_49_vs[3]
        power_meas["FEMB1_DC2DC1_I"] = (bus2_ltc2991_49_vs[2] - bus2_ltc2991_49_vs[3])/0.1
        power_meas["FEMB1_DC2DC2_V"] =  bus2_ltc2991_49_vs[5]
        power_meas["FEMB1_DC2DC2_I"] = (bus2_ltc2991_49_vs[4] - bus2_ltc2991_49_vs[5])/0.01
        power_meas["FEMB1_DC2DC3_V"] =  bus2_ltc2991_49_vs[7]
        power_meas["FEMB1_DC2DC3_I"] = (bus2_ltc2991_49_vs[6] - bus2_ltc2991_49_vs[7])/0.1
        power_meas["FEMB2_BIAS_V"]   =  bus2_ltc2991_4e_vs[1]
        power_meas["FEMB2_BIAS_I"]   = (bus2_ltc2991_4e_vs[0] - bus2_ltc2991_4e_vs[1])/0.1
        power_meas["FEMB2_DC2DC0_V"] =  bus2_ltc2991_4a_vs[1]
        power_meas["FEMB2_DC2DC0_I"] = (bus2_ltc2991_4a_vs[0] - bus2_ltc2991_4a_vs[1])/0.1
        power_meas["FEMB2_DC2DC1_V"] =  bus2_ltc2991_4a_vs[3]
        power_meas["FEMB2_DC2DC1_I"] = (bus2_ltc2991_4a_vs[2] - bus2_ltc2991_4a_vs[3])/0.1
        power_meas["FEMB2_DC2DC2_V"] =  bus2_ltc2991_4a_vs[5]
        power_meas["FEMB2_DC2DC2_I"] = (bus2_ltc2991_4a_vs[4] - bus2_ltc2991_4a_vs[5])/0.01
        power_meas["FEMB2_DC2DC3_V"] =  bus2_ltc2991_4a_vs[7]
        power_meas["FEMB2_DC2DC3_I"] = (bus2_ltc2991_4a_vs[6] - bus2_ltc2991_4a_vs[7])/0.1
        power_meas["FEMB3_BIAS_V"]   =  bus2_ltc2991_4e_vs[1]
        power_meas["FEMB3_BIAS_I"]   = (bus2_ltc2991_4e_vs[0] - bus2_ltc2991_4e_vs[1])/0.1
        power_meas["FEMB3_DC2DC0_V"] =  bus2_ltc2991_4b_vs[1]
        power_meas["FEMB3_DC2DC0_I"] = (bus2_ltc2991_4b_vs[0] - bus2_ltc2991_4b_vs[1])/0.1
        power_meas["FEMB3_DC2DC1_V"] =  bus2_ltc2991_4b_vs[3]
        power_meas["FEMB3_DC2DC1_I"] = (bus2_ltc2991_4b_vs[2] - bus2_ltc2991_4b_vs[3])/0.1
        power_meas["FEMB3_DC2DC2_V"] =  bus2_ltc2991_4b_vs[5]
        power_meas["FEMB3_DC2DC2_I"] = (bus2_ltc2991_4b_vs[4] - bus2_ltc2991_4b_vs[5])/0.01
        power_meas["FEMB3_DC2DC3_V"] =  bus2_ltc2991_4b_vs[7]
        power_meas["FEMB3_DC2DC3_I"] = (bus2_ltc2991_4b_vs[6] - bus2_ltc2991_4b_vs[7])/0.1

#        for key in power_meas:
#            print (key, ":", power_meas[key])
        return power_meas


    def femb_power_config(self, femb_id=0, vfe=3.0, vcd=3.0, vadc=3.5):
        self.wib.femb_power_config(femb_id, vfe, vcd, vadc, 0, 0, 0 )

    def all_femb_bias_ctrl(self, enable=0):
        self.wib.all_femb_bias_ctrl(enable )

    def femb_power_en_ctrl(self, femb_id=0, vfe_en=1, vcd_en=1, vadc_en=1, bias_en=1):
        self.wib.femb_power_en_ctrl(femb_id, vfe_en, vcd_en, vadc_en, 0, bias_en)


    def femb_power_set(self, femb_id=0, on=1, vfe=3.0, vcd=3.0, vadc=3.5, allon=1):
        self.femb_power_config(femb_id, vfe, vcd, vadc)
        self.all_femb_bias_ctrl(enable=allon)
        self.femb_power_en_ctrl(femb_id, vfe_en=on, vcd_en=on, vadc_en=on, bias_en=on)
            

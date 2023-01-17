import ctypes, ctypes.util
import struct, os, sys
import time
import importlib.machinery

wib_cfgs = importlib.machinery.SourceFileLoader('wib_cfgs','/home/BNL_CE_WIB_SW_QC/wib_cfgs.py').load_module()
from wib_cfgs import WIB_CFGS

power_on = ""
if len(sys.argv) > 1:
    power_on = sys.argv[1]

chk = WIB_CFGS()

chk.wib_rst_tp()
chk.wib_fw()
chk.wib_timing(pll=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)

if ("Y" in power_on) or ("y" in power_on):
    print("set FEMB voltages")
    chk.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)

    print("power on FEMBs")
    time.sleep(1)
    fembs = [0]
    chk.femb_powering(fembs)
    print("Sleeping")
    for i in range(15):
        time.sleep(1)
        print(".")
    input("powered, please program FPGA")

wib_path = os.getcwd() + "/build/wib_util.so"
wib = ctypes.CDLL(wib_path)

def get_constant(name_string, ctype): #doesn't shorten code
    return ctype.in_dll(wib, name_string)
    
def setup(): #define C functions' argument types and return types
    wib.peek.argtypes = [ctypes.c_size_t]
    wib.peek.restype = ctypes.c_uint32
    
    wib.poke.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
    wib.poke.restype = None

    wib.wib_peek.argtypes = [ctypes.c_size_t]
    wib.wib_peek.restype = ctypes.c_uint32
    
    wib.wib_poke.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
    wib.wib_poke.restype = None
  
    wib.cdpeek.argtypes = [ctypes.c_uint8,  ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.cdpeek.restype = ctypes.c_uint8
    
    wib.cdpoke.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.cdpoke.restype = None  
    
    wib.datpower_poke.argtypes = [ctypes.c_uint8,  ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_poke.restype = None
    
    wib.datpower_peek.argtypes = [ctypes.c_uint8,  ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_peek.restype = ctypes.c_uint16    

    wib.dat_monadc_trigger.argtypes = None
    wib.dat_monadc_trigger.restype = None
    
    wib.dat_monadc_busy.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.dat_monadc_busy.restype = ctypes.c_bool
    
    wib.dat_monadc_getdata.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.dat_monadc_getdata.restype = ctypes.c_uint16
    
    wib.dat_set_dac.argtypes = [ctypes.c_float, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.dat_set_dac.restype = None
    
    wib.bufread.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    wib.bufread.restype = None

    wib.i2cread.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.i2cread.restype = ctypes.c_uint8

    wib.i2cwrite.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.i2cwrite.restype = None

    wib.read_ltc2990.argtypes = [ctypes.c_uint8, ctypes.c_bool, ctypes.c_uint8]
    wib.read_ltc2990.restype = ctypes.c_double

    wib.read_ltc2991.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_bool, ctypes.c_uint8]
    wib.read_ltc2991.restype = ctypes.c_double    

    wib.read_ad7414.argtypes = [ctypes.c_uint8]
    wib.read_ad7414.restype = ctypes.c_double
 
    wib.read_ina226_c.argtypes = [ctypes.c_uint8]
    wib.read_ina226_c.restype = ctypes.c_double

    wib.read_ina226_v.argtypes = [ctypes.c_uint8]
    wib.read_ina226_v.restype = ctypes.c_double

    wib.read_ltc2499.argtypes = [ctypes.c_uint8]
    wib.read_ltc2499.restype = ctypes.c_double        

    wib.all_femb_bias_ctrl.argtypes = [ctypes.c_bool]
    wib.all_femb_bias_ctrl.restype  = ctypes.c_bool

    wib.femb_power_en_ctrl.argtypes = [ctypes.c_int, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.femb_power_en_ctrl.restype  = ctypes.c_bool

    wib.femb_power_reg_ctrl.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_double]
    wib.femb_power_reg_ctrl.restype = ctypes.c_bool

    wib.femb_power_config.argtypes = [ctypes.c_uint8, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double ]
    wib.femb_power_config.restype = ctypes.c_bool       

    wib.script_cmd.argtypes =  [ctypes.POINTER(ctypes.c_char) ] 
    wib.script_cmd.restype = ctypes.c_bool 
    
    wib.datpower_getvoltage.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_getvoltage.restype = ctypes.c_double
    
    wib.datpower_getcurrent.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_getcurrent.restype = ctypes.c_double    
#DAT registers
DAT_CD_CONFIG = ctypes.c_uint8.in_dll(wib, 'DAT_CD_CONFIG')
DAT_CD_CONFIG = ctypes.c_uint8.in_dll(wib, 'DAT_CD_CONFIG')
DAT_CD1_CONTROL = ctypes.c_uint8.in_dll(wib, 'DAT_CD1_CONTROL')
DAT_CD2_CONTROL = ctypes.c_uint8.in_dll(wib, 'DAT_CD2_CONTROL')
DAT_SOCKET_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_SOCKET_SEL')

DAT_INA226_REG_ADDR = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_REG_ADDR')
DAT_INA226_DEVICE_ADDR = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_DEVICE_ADDR')
DAT_INA226_NUM_BYTES = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_NUM_BYTES')
DAT_INA226_DIN_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_DIN_MSB')
DAT_INA226_DIN_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_DIN_LSB')
DAT_INA226_STRB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_STRB')
DAT_INA226_CD1_DOUT_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CD1_DOUT_MSB')
DAT_INA226_CD1_DOUT_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CD1_DOUT_LSB')
DAT_INA226_CD2_DOUT_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CD2_DOUT_MSB')
DAT_INA226_CD2_DOUT_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CD2_DOUT_LSB')
DAT_INA226_FE_DOUT_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_FE_DOUT_MSB')
DAT_INA226_FE_DOUT_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_FE_DOUT_LSB')

DAT_MONADC_START = ctypes.c_uint8.in_dll(wib, 'DAT_MONADC_START')
DAT_CD1_MONADC_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_CD1_MONADC_DATA_LSB')
DAT_CD1_MONADC_DATA_MSB_BUSY = ctypes.c_uint8.in_dll(wib, 'DAT_CD1_MONADC_DATA_MSB_BUSY')
DAT_CD2_MONADC_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_CD2_MONADC_DATA_LSB')
DAT_CD2_MONADC_DATA_MSB_BUSY = ctypes.c_uint8.in_dll(wib, 'DAT_CD2_MONADC_DATA_MSB_BUSY')
DAT_ADC_MONADC_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_MONADC_DATA_LSB')
DAT_ADC_MONADC_DATA_MSB_BUSY = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_MONADC_DATA_MSB_BUSY')
DAT_FE_MONADC_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_FE_MONADC_DATA_LSB')
DAT_FE_MONADC_DATA_MSB_BUSY = ctypes.c_uint8.in_dll(wib, 'DAT_FE_MONADC_DATA_MSB_BUSY')

DAT_CD_AMON_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_CD_AMON_SEL')
DAT_ADC_FE_TEST_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_FE_TEST_SEL')
DAT_ADC_TEST_SEL_INHIBIT = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_TEST_SEL_INHIBIT')
DAT_FE_TEST_SEL_INHIBIT = ctypes.c_uint8.in_dll(wib, 'DAT_FE_TEST_SEL_INHIBIT')
DAT_FE_IN_TST_SEL_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_FE_IN_TST_SEL_LSB')
DAT_FE_IN_TST_SEL_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_FE_IN_TST_SEL_MSB')
DAT_FE_CALI_CS = ctypes.c_uint8.in_dll(wib, 'DAT_FE_CALI_CS')
DAT_FE_INS_PLS_CS = ctypes.c_uint8.in_dll(wib, 'DAT_FE_INS_PLS_CS')
DAT_ADC_TST_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_TST_SEL')
DAT_ADC_SRC_CS_P_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_SRC_CS_P_LSB')
DAT_ADC_SRC_CS_P_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_SRC_CS_P_MSB')
DAT_ADC_PN_TST_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_PN_TST_SEL')
DAT_ADC_TEST_IN_SEL = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_TEST_IN_SEL')
DAT_EXT_PULSE_CNTL = ctypes.c_uint8.in_dll(wib, 'DAT_EXT_PULSE_CNTL')
DAT_FE_DAC_TP_SET = ctypes.c_uint8.in_dll(wib, 'DAT_FE_DAC_TP_SET')
DAT_FE_DAC_TP_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_FE_DAC_TP_DATA_LSB')
DAT_FE_DAC_TP_DATA_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_FE_DAC_TP_DATA_MSB')
DAT_DAC_OTHER_SET = ctypes.c_uint8.in_dll(wib, 'DAT_DAC_OTHER_SET')
DAT_ADC_P_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_P_DATA_LSB')
DAT_ADC_P_DATA_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_P_DATA_MSB')
DAT_ADC_N_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_N_DATA_LSB')
DAT_ADC_N_DATA_MSB = ctypes.c_uint8.in_dll(wib, 'DAT_ADC_N_DATA_MSB')
DAC_TP_DATA_LSB = ctypes.c_uint8.in_dll(wib, 'DAC_TP_DATA_LSB')
DAC_TP_DATA_MSB = ctypes.c_uint8.in_dll(wib, 'DAC_TP_DATA_MSB')


#INA226 registers
DAT_INA226_CONFIG = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CONFIG')
DAT_INA226_SHUNT_V = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_SHUNT_V')
DAT_INA226_BUS_V = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_BUS_V')
DAT_INA226_POWER = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_POWER')
DAT_INA226_CURRENT = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CURRENT')
DAT_INA226_CALIB = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_CALIB')
DAT_INA226_MASK_ENABLE = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_MASK_ENABLE')
DAT_INA226_ALERT_LIM = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_ALERT_LIM')
DAT_INA226_MANUF_ID = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_MANUF_ID')
DAT_INA226_DIE_ID = ctypes.c_uint8.in_dll(wib, 'DAT_INA226_DIE_ID')

    # wib.script.argtypes = [ctypes.c_char_p, ctypes.c_bool]
    # wib.script.restype = ctypes.c_bool
    
#Wrapper functions because Ctypes doesn't support default arguments
def datpower_poke(dev_addr, reg_addr, data, cd=-1, fe=-1):
    wib.datpower_poke(dev_addr, reg_addr, data, cd, fe)

def datpower_peek(dev_addr, reg_addr, cd=-1, fe=-1):
    return wib.datpower_peek(dev_addr, reg_addr, cd, fe)
    
def dat_monadc_busy(cd=-1, fe=-1, adc=-1):
    return wib.dat_monadc_busy(cd, adc, fe)
    
def dat_monadc_getdata(cd=-1, adc=-1, fe=-1): 
    return wib.dat_monadc_getdata(cd, adc, fe)
    
def dat_set_dac(val, fe=-1, adc=-1, fe_cal=-1):
    wib.dat_set_dac(val, fe, adc, fe_cal)
    
def datpower_getvoltage(addr, cd=-1, fe=-1):
    return wib.datpower_getvoltage(addr, cd, fe)
    
def datpower_getcurrent(addr, cd=-1, fe=-1):
    return wib.datpower_getcurrent(addr, cd, fe)
    
sel = 0
pwr = 2

setup()    
    
    
print("Testing peek/poke")
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))
wib.poke(0xA00C0004, reg_read & ~(1 << 16))
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))
wib.poke(0xA00C0004, reg_read | (1 << 16))
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))

# print("Reading i2c")
# time.sleep(1)

# print(hex(wib.i2cread(pwr,0x23,0xc)))
# print("Writing i2c")
# time.sleep(1)
# wib.i2cwrite(pwr,0x23,0xc,0x0)
# wib.i2cwrite(pwr,0x23,0x4,0x0)
# print(hex(wib.i2cread(pwr,0x23,0xc)))
# print(hex(wib.i2cread(pwr,0x23,0x4)))

# print("Setting femb voltages")
# time.sleep(1)
# wib.femb_power_config(0, 4.0, 4.0, 4.0, 0, 0, 0 )


# print("all off")
# time.sleep(1)
# wib.i2cwrite(pwr,0x23,0xc,0x0)
# wib.i2cwrite(pwr,0x23,0x4,0x0)
# wib.i2cwrite(pwr,0x23,0xd,0x0)
# wib.i2cwrite(pwr,0x23,0x5,0x0)
# wib.i2cwrite(pwr,0x23,0xe,0x0)
# wib.i2cwrite(pwr,0x23,0x6,0x0)
# wib.i2cwrite(pwr,0x22,0xc,0x0)
# wib.i2cwrite(pwr,0x22,0x4,0x0)
# ^this all succeeds

# print("femb0 on, others off")
# time.sleep(1)
# wib.i2cwrite(pwr,0x23,0xc,0x0)
# wib.i2cwrite(pwr,0x23,0x4,0x47) #this apparently crashes the wib
# wib.i2cwrite(pwr,0x23,0xd,0x0)
# wib.i2cwrite(pwr,0x23,0x5,0x0)
# wib.i2cwrite(pwr,0x23,0xe,0x0)
# wib.i2cwrite(pwr,0x23,0x6,0x0)
# wib.i2cwrite(pwr,0x22,0xc,0x0)
# wib.i2cwrite(pwr,0x22,0x4,0x0)


# print("Sleeping")
# for i in range(15):
    # time.sleep(1)
    # print(".")  
# print("Done")

# exit()

# print("Testing i2c communication & femb_power_en_ctrl - pwr")

# femb0 = True
# femb1 = False
# femb2 = False
# femb3 = False
# def script_rd (script, cmds=[]):
    # fdir = "./scripts/"
    # fn = fdir + script
    # with open(fn, 'r') as f:
        # cmdline = f.readline() 
        # while len(cmdline)>0: 
            # if ("i2c" in cmdline) or ("delay" in cmdline) or ("mem" in cmdline):
                # cmds.append(cmdline)
            # elif ("run" in cmdline):
                # x = cmdline[0:-1].split(" ")
                # if (len(x[1]) >0) and (len(x)>=2):
                    # script_rd(script=x[1], cmds=cmds)
                # else:
                    # print ("Error - file(%s) has an invalid RUN command: %s"%(fn, cmdline))
                    # exit()
            # cmdline = f.readline() 
        # return cmds

# def script_exe (script):
    # cmds = script_rd(script=script, cmds=[])
    # for cmd in cmds:
        # cmd = bytes(cmd, 'utf-8')
        # wib.script_cmd(cmd)
# print("femb0_off")
# time.sleep(1)
# script_exe("femb0_off")

# print("femb0_on")
# time.sleep(1)
# i2cwritepwr 0x23 0x4 0x47
# script_exe("femb0_on")




# print("all_femb_bias_ctrl off")
# time.sleep(1)       
# wib.all_femb_bias_ctrl(False)
# print("all_femb_bias_ctrl on")
# time.sleep(1)                                                                   
# wib.femb_power_en_ctrl(0,0x1)
###powering fembs like shanshan
# wib.all_femb_bias_ctrl(True)
# print("femb_power_en_ctrl")
# time.sleep(1)
# wib.femb_power_en_ctrl(0, 1, 1, 1, 0, 1)
    
    
# print("Sleeping 35 seconds")

# for i in range(35):
    # time.sleep(1)
    # print(".")
# exit()    


    
# print("Testing cdpeek/cdpoke")
# reg_read = wib.cdpeek(0, 0, 2, 0)
# print("cdpeek 0x%x"%(reg_read))
# wib.cdpoke(0, 0, 2, 0, 0x0)
# print("cdpoke 0x0")
# reg_read = wib.cdpeek(0, 0, 2, 0)
# print("cdpeek 0x%x"%(reg_read))
# wib.cdpoke(0, 0, 2, 0, 0x1)
# print("cdpoke 0x1")
# reg_read = wib.cdpeek(0, 0, 2, 0)
# print("cdpeek 0x%x"%(reg_read))

# print("Testing clock phase adjustment")

# for i in range(1064):
    # #os.system('sh i2c_phase.sh 1')
    # wib.cdpoke(0, 0xC, 0, 0x2, 0xa)
    # if wib.cdpeek(0, 0xC, 0, 0x2) is 0xa:
        # print("Hooray, we found the right number of steps, it's %d!"%(i))
        # break
    # else:
        # print(str(i)+" steps did not work.")



print("Testing COLDATA communication") 
cd_addr = [0x2, 0x3]
for cd in range(2):
    print("CD",cd+1)
    for reg in range(146):
        print("Reg",hex(reg),":",hex(wib.cdpeek(0, cd_addr[cd], 0, reg)))

    reg_read = wib.cdpeek(0, cd_addr[cd], 0, 0x1)
    print("Reg 1 is " + hex(reg_read))
    wib.cdpoke(0, cd_addr[cd], 0, 0x1, 0xa)
    print("Poked to a")
    print("Reg 1 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x1)))
    wib.cdpoke(0, cd_addr[cd], 0, 0x1, reg_read)
    print("Poked to reg_read")
    print("Reg 1 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x1)))
    print("")

    reg_read = wib.cdpeek(0, cd_addr[cd], 0, 0x20)
    print("Reg x20 is " + hex(reg_read))
    wib.cdpoke(0, cd_addr[cd], 0, 0x20, 0xa)
    print("Poked to a")
    print("Reg x20 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x20)))
    wib.cdpoke(0, cd_addr[cd], 0, 0x20, reg_read)
    print("Poked to reg_read")
    print("Reg x20 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x20)))
    print("")

# print("Toggling CD_SEL")
# reg = wib.cdpeek(0, 0xC, 0, 0x1) 
# reg = reg ^ 0x1 #toggle lsb
# wib.cdpoke(0, 0xC, 0, 0x1, reg)
# print("Reg 0x1 is now",hex(wib.cdpeek(0, 0xC, 0, 0x1)))
#time.sleep(5)


# cd_addr = [0x2, 0x3]
# for cd in range(2):
    # print("CD",cd+1)
    # for reg in range(146):
        # print("Reg",hex(reg),":",hex(wib.cdpeek(0, cd_addr[cd], 0, reg)))

    # reg_read = wib.cdpeek(0, cd_addr[cd], 0, 0x1)
    # print("Reg 1 is " + hex(reg_read))
    # wib.cdpoke(0, cd_addr[cd], 0, 0x1, 0xa)
    # print("Poked to a")
    # print("Reg 1 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x1)))
    # wib.cdpoke(0, cd_addr[cd], 0, 0x1, reg_read)
    # print("Poked to reg_read")
    # print("Reg 1 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x1)))
    # print("")

    # reg_read = wib.cdpeek(0, cd_addr[cd], 0, 0x20)
    # print("Reg x20 is " + hex(reg_read))
    # wib.cdpoke(0, cd_addr[cd], 0, 0x20, 0xa)
    # print("Poked to a")
    # print("Reg x20 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x20)))
    # wib.cdpoke(0, cd_addr[cd], 0, 0x20, reg_read)
    # print("Poked to reg_read")
    # print("Reg x20 is " + hex(wib.cdpeek(0, cd_addr[cd], 0, 0x20)))
    # print("")
    
    
# print("Toggling CD_SEL")
# reg = wib.cdpeek(0, 0xC, 0, 0x1) 
# reg = reg ^ 0x1 #toggle lsb
# wib.cdpoke(0, 0xC, 0, 0x1, reg)
# print("Reg 0x1 is now",hex(wib.cdpeek(0, 0xC, 0, 0x1)))

print("Testing DAT communication") #DAT addr is C
print("Reg 59 is " + hex(wib.cdpeek(0, 0xC, 0, 59)))
wib.cdpoke(0, 0xC, 0, 59, 0xa)
print("Poked to a")
print("Reg 59 is " + hex(wib.cdpeek(0, 0xC, 0, 59)))

print("CD INA226")
addrs = [0x40, 0x41, 0x43, 0x45, 0x44]
cd_name = ["CD1", "CD2"]
name = ["CD_VDDA", "FE_VDDA", "CD_VDDCORE", "CD_VDDD", "CD_VDDIO"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
cal = 0.00512/(I_LSB*R)
print("cal is",hex(int(cal)))
for cd in range(2):
# for cd in range(1):
    total_pwr_mw = 0
    for i in range(5):
    #addr = 0x40
    
        addr = addrs[i]



        # #Write calibration reg
        # datpower_poke(addr, DAT_INA226_CALIB, int(cal), cd=cd)
        # #Write config reg
        # datpower_poke(addr, DAT_INA226_CONFIG, 0x41FF, cd=cd)
        # #wait till conversion is completed
        # datpower_poke(addr, DAT_INA226_MASK_ENABLE, 0x0, cd=cd) #poke in order to peek
        # ready = 0x0
        # for loop in range(20):
            # reg = datpower_peek(addr, DAT_INA226_MASK_ENABLE, cd=cd)
            # ready = reg & 0x8
            # # print(hex(reg))
            # if ready is 0x8:
                # break
        # if ready is not 0x8:            
            # print(cd_name[cd], name[i], "timed out checking for CVRF")            
            # reg_addr_reg = wib.cdpeek(0, 0XC, 0, DAT_INA226_REG_ADDR)
            # print("DAT_INA226_REG_ADDR =",hex(reg_addr_reg))
        # #Read Bus voltage, Current, Power (need to poke first in order to read)
        # datpower_poke(addr, DAT_INA226_BUS_V, 0xAAAA, cd=cd)
        # bus_voltage_reg = datpower_peek(addr, DAT_INA226_BUS_V, cd=cd)
        # bus_voltage = bus_voltage_reg*V_LSB

        # datpower_poke(addr, DAT_INA226_CURRENT, 0xAAAA, cd=cd)
        # current_reg = datpower_peek(addr, DAT_INA226_CURRENT, cd=cd)
        # current = current_reg*I_LSB 

        # datpower_poke(addr, DAT_INA226_POWER, 0xAAAA, cd=cd)
        # power_reg = datpower_peek(addr, DAT_INA226_POWER, cd=cd)
        # power = power_reg*25*I_LSB 
        
        bus_voltage = datpower_getvoltage(addr, cd=cd)
        current = datpower_getcurrent(addr, cd=cd)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        print (cd_name[cd], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
        print (cd_name[cd], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        print (cd_name[cd], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")
        # print("Power (mW)=",  power*1e+3, "mW", hex(power_reg), '\n')                          #11 mW
    print (cd_name[cd], "Total Power =\t", total_pwr_mw)
    print("")

print("FE/ADC INA226")
fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42, 0x43, 0x45, 0x46, 0x44]
name = ["VDD", "VDDO", "VPPP", "VDDA2P5", "VDDD2P5", "VDDIO", "VDDD1P2"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
cal = 0.00512/(I_LSB*R)
print("cal is",hex(int(cal)))
for fe in range(8):
# for cd in range(1):
    total_pwr_mw = 0
    for i in range(7):
    #addr = 0x40
        addr = addrs[i]



        # #Write calibration reg
        # datpower_poke(addr, DAT_INA226_CALIB, int(cal), fe=fe)
        # #Write config reg
        # datpower_poke(addr, DAT_INA226_CONFIG, 0x41FF, fe=fe)
        # #wait till conversion is completed
        # datpower_poke(addr, DAT_INA226_MASK_ENABLE, 0x0, fe=fe) #poke in order to peek
        # ready = 0x0
        # for loop in range(20):
            # reg = datpower_peek(addr, DAT_INA226_MASK_ENABLE, fe=fe)
            # ready = reg & 0x8
            # # print(hex(reg))
            # if ready is 0x8:
                # break
        # if ready is not 0x8:            
            # print(fe_name[fe], name[i], "timed out checking for CVRF")            
            # reg_addr_reg = wib.cdpeek(0, 0XC, 0, DAT_INA226_REG_ADDR)
            # print("DAT_INA226_REG_ADDR =",hex(reg_addr_reg))
        # #Read Bus voltage, Current, Power (need to poke first in order to read)
        # datpower_poke(addr, DAT_INA226_BUS_V, 0xAAAA, fe=fe)
        # bus_voltage_reg = datpower_peek(addr, DAT_INA226_BUS_V, fe=fe)
        # bus_voltage = bus_voltage_reg*V_LSB

        # datpower_poke(addr, DAT_INA226_CURRENT, 0xAAAA, fe=fe)
        # current_reg = datpower_peek(addr, DAT_INA226_CURRENT, fe=fe)
        # current = current_reg*I_LSB 

        # datpower_poke(addr, DAT_INA226_POWER, 0xAAAA, fe=fe)
        # power_reg = datpower_peek(addr, DAT_INA226_POWER, fe=fe)
        # power = power_reg*25*I_LSB 

        bus_voltage = datpower_getvoltage(addr, fe=fe)
        current = datpower_getcurrent(addr, fe=fe)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        print (fe_name[fe], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
        print (fe_name[fe], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        print (fe_name[fe], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")
    print (fe_name[fe], "Total Power =\t", total_pwr_mw, "mW")
    print("")
        # print (fe_name[fe], name[i], "Bus V (V)=",  bus_voltage, "V", hex(bus_voltage_reg)) #0x40 nominal vals: 1.19 V
        # print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        # print("Power (mW)=",  power*1e+3, "mW", hex(power_reg), '\n')                          #11 mW
        #CD_VDDA_P - Datasheet voltage says 1.1 V - So all good

print("CD_CONTROL r/w checking")


for cd_swap in range(2):
    sel_reg = wib.cdpeek(0, 0xC, 0, DAT_CD_CONFIG)
    CD_SEL = sel_reg & 0x1
    print("CD_SEL =", CD_SEL)
    print("Toggling CD_SEL")
    sel_reg = sel_reg ^ 0x1
    wib.cdpoke(0, 0xC, 0, DAT_CD_CONFIG, sel_reg)
    print("")
    # input("Press enter to continue")
    for cd in [0x2, 0x3]:
    #making sure  DC-type level signals for the Front-end Mother Board (pads
    #FMB_CONTROL_N (bit N) are available at the pads
        # print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        wib.cdpoke(0, cd, 0, 0x27, 0xFF)
        
        # print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x27)))
        # if cd is 0x2:
            # fpga_control_addr = 51
        # else:
            # fpga_control_addr = 52
        # control_read = wib.cdpeek(0, 0xC, 0, fpga_control_addr)
        # print("FPGA:", hex(control_read))
        # print("")
        
        print("Poking to 0x0")
        wib.cdpoke(0, cd, 0, 0x26, 0x0)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD2_CONTROL))) 
        print("")
        # input("Press enter to continue")
        
        print("Poking to 0x10")
        wib.cdpoke(0, cd, 0, 0x26, 0x10)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD2_CONTROL)))   
        print("")
        # input("Press enter to continue")
        print("Poking to 0x15")
        wib.cdpoke(0, cd, 0, 0x26, 0x15)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD2_CONTROL))) 
        print("")
        # input("Press enter to continue")
        print("Poking to 0x0a")
        wib.cdpoke(0, cd, 0, 0x26, 0x0A)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, DAT_CD2_CONTROL))) 
        print("")
    

#AD7274 testing
#write 0x1, then 0x0 to reg 26

#then keep checking busy (reg 55 & 0x80) until it is 0
#busy_regs = [55, 3, 5, 7, 9, 11, 13, 15, 17]

select_names_cd = ["GND", "CD_VCEXT", "CD_LOCK", "CD_ATO", "CD_VDDIO", "CD_VDDA", "CD_VDDCORE", "CD_VDDD"]
select_names_adc = ["VOLTAGE_MONITOR_MUX", "CURRENT_MONITOR_MUX", "VREFP", "VREFN", "VCMI", "VCMO", "AUX_ISINK_MUX", "AUX_ISOURCE_MUX"]
select_names_fe = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]


AD_REF = 2.27 #V
AD_LSB = AD_REF/4096

#DAC
print("\nFE DAC")
for dac in range(8):
    #Set DAC output
    dac_float = (dac+1)*2.5/8 - 2.5/65546
    print("DAC %d: %f"%(dac,dac_float))
    # dac_val = int(dac_float*65536/2.5)
    # print("DAC %d: %f (0x%x)"%(dac,dac_float,dac_val))
    # dac_lsb = dac_val & 0xFF
    # dac_msb = (dac_val & 0xFF00) >> 8;

    # wib.cdpoke(0, 0xC, 0, DAT_FE_DAC_TP_DATA_LSB, dac_lsb);
    # wib.cdpoke(0, 0xC, 0, DAT_FE_DAC_TP_DATA_MSB, dac_msb);
    # #Set socket sel to dac
    # wib.cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, dac);
    # #Trigger DAC
    # wib.cdpoke(0, 0xC, 0, DAT_FE_DAC_TP_SET, 0x1<<dac);
    # wib.cdpoke(0, 0xC, 0, DAT_FE_DAC_TP_SET, 0x0);
    # # # Set FE MonADC input to 0x2
    # # wib.cdpoke(0, 0xC, 0, DAT_ADC_FE_TEST_SEL, 0x2 << 4);
    dat_set_dac(dac_float, fe=dac)
print("\nDAC ADC P")    
dac_float = 1.6
# dac_val = int(dac_float*65536/2.5)
# print("DAC %d: %f (0x%x)"%(dac,dac_float,dac_val))
# dac_lsb = dac_val & 0xFF
# dac_msb = (dac_val & 0xFF00) >> 8;

# wib.cdpoke(0, 0xC, 0, DAT_ADC_P_DATA_LSB, dac_lsb);
# wib.cdpoke(0, 0xC, 0, DAT_ADC_P_DATA_MSB, dac_msb);
# # #Set socket sel to dac
# # wib.cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, dac);
# #Trigger DAC
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x1<<0);
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x0);
dat_set_dac(dac_float,adc=0)

print("\nDAC ADC N") 
dac_float = 1.4
# dac_val = int(dac_float*65536/2.5)
# print("DAC %d: %f (0x%x)"%(dac,dac_float,dac_val))
# dac_lsb = dac_val & 0xFF
# dac_msb = (dac_val & 0xFF00) >> 8;

# wib.cdpoke(0, 0xC, 0, DAT_ADC_N_DATA_LSB, dac_lsb);
# wib.cdpoke(0, 0xC, 0, DAT_ADC_N_DATA_MSB, dac_msb);
# # #Set socket sel to dac
# # wib.cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, dac);
# #Trigger DAC
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x1<<1);
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x0);
dat_set_dac(dac_float,adc=1)

print("\nDAC TP") 
dac_float = 0.42
# dac_val = int(dac_float*65536/2.5)
# print("DAC %d: %f (0x%x)"%(dac,dac_float,dac_val))
# dac_lsb = dac_val & 0xFF
# dac_msb = (dac_val & 0xFF00) >> 8;

# wib.cdpoke(0, 0xC, 0, DAC_TP_DATA_LSB, dac_lsb);
# wib.cdpoke(0, 0xC, 0, DAC_TP_DATA_MSB, dac_msb);
# # #Set socket sel to dac
# # wib.cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, dac);
# #Trigger DAC
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x1<<2);
# wib.cdpoke(0, 0xC, 0, DAT_DAC_OTHER_SET, 0x0);
dat_set_dac(dac_float,fe_cal=0)


#CD1
for select in [0,1,2,3,4,5,6,7]:
    print("\n\nSelect =",hex(select),select_names_cd[select])
    
    wib.cdpoke(0, 0xC, 0, DAT_CD_AMON_SEL, select)    
    wib.dat_monadc_trigger()   
    time.sleep(1e-6)
    for loop in range(10):
        if not dat_monadc_busy(cd=0):
            break;
        if loop is 9:
            print("Timed out while waiting for AD7274 controller to finish")
    data = dat_monadc_getdata(cd=0)
    print("CD1 MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))

#CD2
# for select in [0,1,2,3,4,5,6,7,3,1,6,2,0,7]:
    print("\nSelect =",hex(select),select_names_cd[select])
    wib.cdpoke(0, 0xC, 0, DAT_CD_AMON_SEL, select<<4)    
    wib.dat_monadc_trigger() 
    time.sleep(1e-6)    
    for loop in range(10):
        if not dat_monadc_busy(cd=1):
            break;
        if loop is 9:
            print("Timed out while waiting for AD7274 controller to finish")
    data = dat_monadc_getdata(cd=1)
    print("CD2 MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))


#ADC
# for select in [0,1,2,3,4,5,6,7,3,1,6,2,0,7]:
    print("\nSelect =",hex(select),select_names_adc[select])
    wib.cdpoke(0, 0xC, 0, DAT_ADC_FE_TEST_SEL, select)    
    wib.dat_monadc_trigger()    
    time.sleep(1e-6)
    for adc in range(8):
        for check in range(10):
            if not dat_monadc_busy(adc=adc):
                break;
            if check is 9:
                print("Timed out while waiting for AD7274 controller to finish")
        data = dat_monadc_getdata(adc=adc)
        print("ADC MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))
        
#FE
# for select in [0,1,2,3,4,5,6,7,3,1,6,2,0,7]:
    print("\nSelect =",hex(select),select_names_fe[select])
    wib.cdpoke(0, 0xC, 0, DAT_ADC_FE_TEST_SEL, select<<4)    
    time.sleep(1e-6)
    wib.dat_monadc_trigger()    
    for fe in range(8):
        for check in range(10):
            if not dat_monadc_busy(fe=fe):
                break;
            if check is 9:
                print("Timed out while waiting for AD7274 controller to finish")
        data = dat_monadc_getdata(fe=fe)
        print("FE MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))


# Trigger ADC
# wib.dat_monadc_trigger()
# Get ADC data
# for fe in range(8):
    # for check in range(10):
        # if not dat_monadc_busy(fe=fe):
            # break;
        # if check is 9:
            # print("Timed out while waiting for AD7274 controller to finish")
    # data = dat_monadc_getdata(fe=fe)
    # print("FE",fe+1,"MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))



    # input("Press enter to continue")

    # time.sleep(1)
    # for busy_reg in busy_regs:
        # print("Busy reg", busy_reg)
        # for loop in range(20):
            # busy = wib.cdpeek(0, 0xC, 0, busy_reg) & 0x80
            # if busy is 0x0:
                # break
        # if busy is not 0x0:
            # print("Timed out while waiting for AD7274 controller to finish")
        # else:
        ###### then check ((reg55 & 0x7F) << 8) | reg 54
            # adc_out = ((wib.cdpeek(0, 0xC, 0, busy_reg) & 0x7F) << 8) | wib.cdpeek(0, 0xC, 0, busy_reg-1)
            # print("ADC_OUT = ",hex(adc_out))
    
# #FE INA
# print("FE INA226")
# V_LSB = 1.25e-3
# I_LSB = 0.01e-3 #amps
# R = 0.1 #ohms
# cal = 0.00512/(I_LSB*R)

# # for cd in range(2):
# # # for cd in range(1):
    # # bus = cd + 1
    
    # # for i in range(5):
# addr = 0x40
# addrs = [0x40, 0x41, 0x42, 0x43, 0x45, 0x46, 0x44]
# bus = 3
# for bus in [3,4]:
    
    # # for i in range(1000000):
    # for addr in addrs:
        # #Write calibration reg
        # wib.cdpoke_i2c(bus, addr, 0x05, int(cal))
        # #Write config reg
        # wib.cdpoke_i2c(bus, addr, 0x00, 0x41FF)
        # #wait till conversion is completed
        # wib.cdpoke_i2c(bus, addr, 0x06, 0x0) #poke in order to peek 
        # ready = 0x0
        # for loop in range(20):
            # reg = wib.cdpeek_i2c(bus, addr, 0x06)
            # ready = reg & 0x8
            # #print(hex(reg))
            # if ready is 0x8:
                # break
        # if ready is not 0x8:
            # print("timed out checking for CVRF")
        # #Read Bus voltage, Current, Power (need to poke first in order to read)
        # wib.cdpoke_i2c(bus, addr, 0x02, 0xAAAA)
        # bus_voltage_reg = wib.cdpeek_i2c(bus, addr, 0x02)
        # bus_voltage = bus_voltage_reg*V_LSB

        # wib.cdpoke_i2c(bus, addr, 0x04, 0xAAAA)
        # current_reg = wib.cdpeek_i2c(bus, addr, 0x04)
        # current = current_reg*I_LSB 

        # wib.cdpoke_i2c(bus, addr, 0x03, 0xAAAA)
        # power_reg = wib.cdpeek_i2c(bus, addr, 0x03)
        # power = power_reg*25*I_LSB 

        # print ("Bus V (V)=",  bus_voltage, "V", hex(bus_voltage_reg)) 
        # print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  
        # print("Power (mW)=",  power*1e+3, "mW", hex(power_reg), '\n')                         


    


# info to write: I2C_DEV_ADDR (write 0x40 to reg36_p(6 downto 0)), I2C_NUM_BYTES (write 0x1? to reg37_p(3 downto 0)), 
    # I2C_ADDRESS [register address?] (write 0x7 to reg35_p), I2C_DIN [data] (write 0xAB to reg38_p)
# trigger to actually write: I2C_WR_STRB (write 1 and then 0 to reg34_p(0))
# wib.cdpoke(0, 0xC, 0, 36, 0x40) #I2C_DEV_ADDR
# wib.cdpoke(0, 0xC, 0, 37, 0x1) #I2C_NUM_BYTES
# wib.cdpoke(0, 0xC, 0, 35, 0x7) #I2C_ADDRESS
# wib.cdpoke(0, 0xC, 0, 38, 0xAD) #DIN

# wib.cdpoke(0, 0xC, 0, 34, 0x1) #I2C_WR_STRB
# wib.cdpoke(0, 0xC, 0, 34, 0x0) #I2C_WR_STRB
# wib.cdpoke(0, 0xC, 0, 34, 0x0) #I2C_WR_STRB
# print("Strb is "+hex(wib.cdpeek(0, 0xC, 0, 34)))#I2C_WR_STRB - make sure it's off

# for i in range(500000):


# print("Trying to peek I2C addr 0x40 register 0xFE")
# wib.cdpoke_i2c(0b1000000, 0xFE, 0xAA); #need to poke first to update register pointer in order to peek 
# print("0x40 Reg FE is "+hex(wib.cdpeek_i2c(0b1000000,0xFE)))

# val = 0xFFFC
# print("Val: "+hex(val))
# for i in range(8):
    # if i is 0:
        # value = val & 0x7FFF
    # else:
        # value = val
    # #print("Trying to poke I2C addr 0x40 register "+hex(i)+" to value "+hex(value))
    # wib.cdpoke_i2c(0b1000000, i, value); 
    # print("0x40 Reg "+hex(i)+" is "+hex(wib.cdpeek_i2c(0b1000000,0x7)))

# i = 0xFE
# #print("Trying to poke I2C addr 0x40 register "+hex(i)+" to value "+hex(value))
# wib.cdpoke_i2c(0b1000000, i, value); 
# print("0x40 Reg "+hex(i)+" is "+hex(wib.cdpeek_i2c(0b1000000,0x7)))

# i = 0xFF
# #print("Trying to poke I2C addr 0x40 register "+hex(i)+" to value "+hex(value))
# wib.cdpoke_i2c(0b1000000, i, value); 
# print("0x40 Reg "+hex(i)+" is "+hex(wib.cdpeek_i2c(0b1000000,0x7)))

# print("Resetting values to defaults")
# wib.cdpoke_i2c(0b1000000, 0, 0x8000);

# print("Trying to poke I2C addr 1001111 [doesn't exist] register 7 to value 0xBC")
# wib.cdpoke_i2c(0b1001111, 0x7, 0xBC); 
# print("0b1001111 Reg 7 is "+hex(wib.cdpeek_i2c(0b1001111,0x7)))    

    # print("Trying to poke I2C addr 0x41 register 7 to value 0xAB")
    # wib.cdpoke_i2c(0b1000001, 0x7, 0xAB); 
    # print("0x41 Reg 7 is "+hex(wib.cdpeek_i2c(0b1000001,0x7)))

    # print("Trying to poke I2C addr 0x42 register 7 to value 0xAC")
    # wib.cdpoke_i2c(0b1000010, 0x7, 0xAC); 
    # print("0x42 Reg 7 is "+hex(wib.cdpeek_i2c(0b1000010,0x7)))

    # print("Trying to poke I2C addr 0x45 register 7 to value 0xAD")
    # wib.cdpoke_i2c(0b1000101, 0x7, 0xAD); 
    # print("0x45 Reg 7 is "+hex(wib.cdpeek_i2c(0b1000101,0x7)))

    # print("Trying to poke I2C addr 0x44 register 7 to value 0xAE")
    # wib.cdpoke_i2c(0b1000100, 0x7, 0xAE); 
    # print("0x44 Reg 7 is "+hex(wib.cdpeek_i2c(0b1000100,0x7)))

#power_off = input("Turn off FEMBs?")
power_off = "y"
if ("Y" in power_off) or ("y" in power_off):
    print("Turning off FEMBs")
    chk.femb_powering([])
exit()

# print("Powering off all FEMBs")
# for i in range(0,3):
    # wib.femb_power_en_ctrl(0,0x0)
    


print("Testing i2c communication - sel")
i2c_sensor = 5
wib.i2cselect(i2c_sensor)
reg_read = wib.i2cread(sel, 0x4E, 0)

#print("Turning voltages off")
#wib.femb_power_config(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)



for i in range(1,5):
    print("2990 4E Voltage %d is %f"%(i,wib.read_ltc2990(0x4E, False, i)))
print("2990 4E Vcc is %f"%(wib.read_ltc2990(0x4E, False, 6)+2.5))
for i in range(1,5):
    print("2990 4C Voltage %d is %f"%(i,wib.read_ltc2990(0x4C, False, i)))
print("2990 4C Vcc is %f"%(wib.read_ltc2990(0x4C, False, 6)+2.5))

for i in range(1,9):
    print("sel bus: 2991 48 Voltage %d is %f"%(i,wib.read_ltc2991(sel, 0x48, False, i)))
print("2991 0x48 Vcc is %f"%(wib.read_ltc2991(sel,0x48, False, 10)+2.5))

print("7414 49 Temp is %f"%(wib.read_ad7414(0x49)))
print("7414 4D Temp is %f"%(wib.read_ad7414(0x4D)))  
print("7414 4A Temp is %f"%(wib.read_ad7414(0x4A)))

for i in range(0,7):
    print("2499 Temp %d is %f"%(i,wib.read_ltc2499(i))) 
    
femb_power_addr = [0x48,0x49,0x4a,0x4b,0x4c,0x4d,0x4E]
for i in range(0,7):
    if (i<4):
        print("\nReading FEMB%i DC2DC current sensor"%(i))
    for j in range(1,9):
        print("pwr bus: 2991 0x%x Voltage ch %d is %f"%(femb_power_addr[i],j,wib.read_ltc2991(pwr,femb_power_addr[i], False, j)))
    print("pwr bus: 2991 0x%x Vcc is %f"%(femb_power_addr[i],wib.read_ltc2991(pwr,femb_power_addr[i], False, 10)+2.5))





print("Turning voltages on")
if (wib.femb_power_config(3.0, 3.0, 3.5, 0.0, 0.0, 0.0)):#<-will test femb_power_reg_ctrl
    print("Success") 
else:
    print("Failed")

for i in range(1,5):
    print("2990 4E Voltage %d is %f"%(i,wib.read_ltc2990(0x4E, False, i)))
print("2990 4E Vcc is %f"%(wib.read_ltc2990(0x4E, False, 6)+2.5))
for i in range(1,5):
    print("2990 4C Voltage %d is %f"%(i,wib.read_ltc2990(0x4C, False, i)))
print("2990 4C Vcc is %f"%(wib.read_ltc2990(0x4C, False, 6)+2.5))

for i in range(1,9):
    print("sel bus: 2991 48 Voltage %d is %f"%(i,wib.read_ltc2991(sel, 0x48, False, i)))
print("2991 0x48 Vcc is %f"%(wib.read_ltc2991(sel,0x48, False, 10)+2.5))

print("7414 49 Temp is %f"%(wib.read_ad7414(0x49)))
print("7414 4D Temp is %f"%(wib.read_ad7414(0x4D)))  
print("7414 4A Temp is %f"%(wib.read_ad7414(0x4A)))

for i in range(0,7):
    print("2499 Temp %d is %f"%(i,wib.read_ltc2499(i))) 
    
femb_power_addr = [0x48,0x49,0x4a,0x4b,0x4c,0x4d,0x4E]
for i in range(0,7):
    if (i<4):
        print("\nReading FEMB%i DC2DC current sensor"%(i))
    for j in range(1,9):
        print("pwr bus: 2991 0x%x Voltage ch %d is %f"%(femb_power_addr[i],j,wib.read_ltc2991(pwr,femb_power_addr[i], False, j)))
    print("pwr bus: 2991 0x%x Vcc is %f"%(femb_power_addr[i],wib.read_ltc2991(pwr,femb_power_addr[i], False, 10)+2.5))


print("Python running script")
# success = wib.script(ctypes.c_char_p(b"femb0_off"),True)
# print(success)
success = wib.script(ctypes.c_char_p(b"delay"),True)


success = wib.script(ctypes.c_char_p(b"i2c pwr 0x23 0xc 0\ni2c pwr 0x23 0x4 0x0"),False)

# reg_read = wib.peek(0xA00C0004)
# print("Read "+hex(reg_read))
# val = reg_read & ~(1 << 16)
# success = wib.script(ctypes.c_char_p(b"mem 0xa00c0004 "+bytes(hex(val),'utf-8')),False)
# print(success)
# reg_read = wib.peek(0xA00C0004)
# print("Read "+hex(reg_read))
# val = reg_read | (1 << 16)
# success = wib.script(ctypes.c_char_p(b"mem 0xa00c0004 "+bytes(hex(val),'utf-8')),False)
# print(success)
# reg_read = wib.peek(0xA00C0004)
# print("Read "+hex(reg_read))

print(success)


#wib.i2cwrite(0,0x70,0x7,1)
exit()


# reg_read = wib.i2cread("sel", 0x70,0x7)

print('Testing bufread')
DAQ_SPY_SIZE = 0x00100000
buf = (ctypes.c_char*DAQ_SPY_SIZE)()
wib.bufread(buf, 0) #read buf0

#allocate memory in python
buf_bytes = bytearray(DAQ_SPY_SIZE)
byte_ptr = (ctypes.c_char*DAQ_SPY_SIZE).from_buffer(buf_bytes)
if not ctypes.memmove(byte_ptr, buf, DAQ_SPY_SIZE):
    print('memmove failed')
    exit()
    
#now buf_bytes can be unpacked via struct.unpack_from, etc
    #eg. frames0 = spymemory_decode(buf=buf_bytes)
num_words = int(len(buf_bytes) // 4)
words = list(struct.unpack_from("<%dI"%(num_words),buf_bytes))   
print("First 200 words of buf0:")
for i in range(200):
    print("%x"%(words[i]))
    
    
    
wib.bufread(buf, 1) #read buf1    
if not ctypes.memmove(byte_ptr, buf, DAQ_SPY_SIZE):
    print('memmove failed')
    exit()
num_words = int(len(buf_bytes) // 4)
words = list(struct.unpack_from("<%dI"%(num_words),buf_bytes))   
print("First 200 words of buf1:")
for i in range(200):
    print("%x"%(words[i]))
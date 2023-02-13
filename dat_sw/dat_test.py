import ctypes, ctypes.util
import struct, os, sys
import time
import importlib.machinery

wib_cfgs = importlib.machinery.SourceFileLoader('wib_cfgs','/home/BNL_CE_WIB_SW_QC/wib_cfgs.py').load_module()
from wib_cfgs import WIB_CFGS

# power_on = ""
# if len(sys.argv) > 1:
    # power_on = sys.argv[1]

chk = WIB_CFGS()

chk.wib_rst_tp()
chk.wib_fw()
chk.wib_timing(pll=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)

# if ("Y" in power_on) or ("y" in power_on):
print("set FEMB voltages")
chk.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)

print("power on FEMBs")
time.sleep(1)
fembs = [0]
chk.femb_powering(fembs)
print("Sleeping")
for i in range(20):
    time.sleep(1)
    print(".")
input("Program FPGA if needed, then press enter to continue.")

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
    
    wib.datpower_getvoltage.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_getvoltage.restype = ctypes.c_double
    
    wib.datpower_getcurrent.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.datpower_getcurrent.restype = ctypes.c_double    
    
    wib.dat_set_dac.argtypes = [ctypes.c_float, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    wib.dat_set_dac.restype = None
    
    wib.dat_set_pulse.argtypes = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_float]
    wib.dat_set_pulse.restype = None




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
    
def datpower_getvoltage(addr, cd=-1, fe=-1):
    return wib.datpower_getvoltage(addr, cd, fe)
    
def datpower_getcurrent(addr, cd=-1, fe=-1):
    return wib.datpower_getcurrent(addr, cd, fe)    
    
def dat_monadc_busy(cd=-1, fe=-1, adc=-1):
    return wib.dat_monadc_busy(cd, adc, fe)
    
def dat_monadc_getdata(cd=-1, adc=-1, fe=-1): 
    return wib.dat_monadc_getdata(cd, adc, fe)
    
def dat_set_dac(val, fe=-1, adc=-1, fe_cal=-1):
    wib.dat_set_dac(val, fe, adc, fe_cal)
    
def dat_set_pulse(en=0, period=0, width=0, amplitude=0):
    wib.dat_set_pulse(en, period, width, amplitude)
    
    
    
sel = 0
pwr = 2

setup()    
    
    
print("Testing WIB peek/poke")
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))
wib.poke(0xA00C0004, reg_read & ~(1 << 16))
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))
wib.poke(0xA00C0004, reg_read | (1 << 16))
reg_read = wib.peek(0xA00C0004)
print("peek 0x%x"%(reg_read))


print("Testing DAT peek/poke") #DAT addr is C
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
    total_pwr_mw = 0
    for i in range(5):    
        addr = addrs[i]
        
        bus_voltage = datpower_getvoltage(addr, cd=cd)
        current = datpower_getcurrent(addr, cd=cd)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        print (cd_name[cd], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
        print (cd_name[cd], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        print (cd_name[cd], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")                         #11 mW
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


        bus_voltage = datpower_getvoltage(addr, fe=fe)
        current = datpower_getcurrent(addr, fe=fe)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        print (fe_name[fe], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
        print (fe_name[fe], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        print (fe_name[fe], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")
    print (fe_name[fe], "Total Power =\t", total_pwr_mw, "mW")
    print("")


print("CD_CONTROL r/w checking")
for cd_swap in range(2):
    sel_reg = wib.cdpeek(0, 0xC, 0, chk.DAT_CD_CONFIG)
    CD_SEL = sel_reg & 0x1
    print("CD_SEL =", CD_SEL)
    print("Toggling CD_SEL")
    sel_reg = sel_reg ^ 0x1
    wib.cdpoke(0, 0xC, 0, chk.DAT_CD_CONFIG, sel_reg)
    print("")
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
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD2_CONTROL))) 
        print("")
        # input("Press enter to continue")
        
        print("Poking to 0x10")
        wib.cdpoke(0, cd, 0, 0x26, 0x10)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD2_CONTROL)))   
        print("")
        # input("Press enter to continue")
        print("Poking to 0x15")
        wib.cdpoke(0, cd, 0, 0x26, 0x15)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD2_CONTROL))) 
        print("")
        # input("Press enter to continue")
        print("Poking to 0x0a")
        wib.cdpoke(0, cd, 0, 0x26, 0x0A)
        print(hex(cd),": ",hex(wib.cdpeek(0, cd, 0, 0x26)))
        # time.sleep(5)
        print("CONTROL 1:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD1_CONTROL)))   
        print("CONTROL 2:", hex(wib.cdpeek(0, 0xC, 0, chk.DAT_CD2_CONTROL))) 
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
    dat_set_dac(dac_float, fe=dac)
    
print("\nDAC ADC P")    
dac_float = 1.6
dat_set_dac(dac_float,adc=0)

print("\nDAC ADC N") 
dac_float = 1.4
dat_set_dac(dac_float,adc=1)

print("\nDAC TP") 
dac_float = 0.42
dat_set_dac(dac_float,fe_cal=0)


#CD1
for select in [0,1,2,3,4,5,6,7]:
    print("\n\nSelect =",hex(select),select_names_cd[select])
    
    wib.cdpoke(0, 0xC, 0, chk.DAT_CD_AMON_SEL, select)    
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
    print("\nSelect =",hex(select),select_names_cd[select])
    wib.cdpoke(0, 0xC, 0, chk.DAT_CD_AMON_SEL, select<<4)    
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
    print("\nSelect =",hex(select),select_names_adc[select])
    wib.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, select)    
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
    print("\nSelect =",hex(select),select_names_fe[select])
    wib.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, select<<4)    
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

dat_set_pulse(0x7, 0x2e4, 0x50, 1.0)


print("\nSetting FE DAC for TP")
for dac in range(8):
    #Set DAC output
    dac_float = 1.0 #(dac+1)*2.5/8 - 2.5/65546
    print("DAC %d: %f"%(dac,dac_float))
    dat_set_dac(dac_float, fe=dac)

# #Test with all TP_EN combinations
# for tp_en in range(16): #0 to F
    # wib.cdpoke(0, 0xC, 0, DAC_TEST_PULSE_EN, tp_en)
    # fpga = tp_en & 0x1 is 0x1
    # asic = tp_en & 0x2 is 0x2
    # int_ = tp_en & 0x4 is 0x4
    # ext = tp_en & 0x8 is 0x8
    # print("FPGA = %d, ASIC = %d, INT = %d, EXT = %d"%(fpga, asic, int_, ext))
    # input("Check signal tap, press enter to continue")
tp_en = 0x7
wib.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_EN, tp_en)






###This doesn't work for some reason:
#power_off = input("Turn off FEMBs?")
# power_off = "y"
# if ("Y" in power_off) or ("y" in power_off):
# print("Turning off FEMBs") 
# chk.femb_powering([])


## =========================================
import numpy as np
# import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
from function.raw_convertor import RAW_CONV
from function.csv_manager import WIB_QC_CSV_Manager
import datetime


import function.Rigol_DP800 as rigol
from function.ping_host import ping_host
import file.report_dict as rp_dict

## =========================================
# initial
print("\033[35m" + "A_RT06: PTB Interface Path" + "\033[0m")
t1 = time.time()
print("\033[35m" + "A_RT03_01 : Power Rail" + "\033[0m")
t1 = time.time()
psu = rigol.RigolDP800()

psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(2)  # FIXED: was psu.measure(1)
print(f"WIB Power - Ch1: {v1:.3f}V {c1:.3f}A, Ch2: {v2:.3f}V {c2:.3f}A")

# Update CSV with WIB power measurements
if rp_dict.csv_manager:
    v1_status = "PASS" if 11.0 <= v1 <= 13.0 else "FAIL"
    c1_status = "PASS" if 0.5 <= c1 <= 3.0 else "FAIL"
    v2_status = "PASS" if 11.0 <= v2 <= 13.0 else "FAIL"
    c2_status = "PASS" if 0.5 <= c2 <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T06_00", "value": round(v1, 3), "status": v1_status},
        {"item_id": "T06_01", "value": round(c1, 3), "status": c1_status},
        {"item_id": "T06_02", "value": round(v2, 3), "status": v2_status},
        {"item_id": "T06_03", "value": round(c2, 3), "status": c2_status}
    ])

time.sleep(1)

time.sleep(30) # wait for boot
print(c1)
print(c2)
time.sleep(27) # wait for boot

# Internet Connection
# TCP/IP 192.168.121.1
ping1_result = ping_host(ip_address="192.168.121.1", count=4)
ping2_result = ping_host(ip_address="192.168.121.2", count=4)

# Update CSV with ping test results
if rp_dict.csv_manager:
    ping1_status = "PASS" if ping1_result else "FAIL"
    ping2_status = "PASS" if ping2_result else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T06_04", "value": "Connected" if ping1_result else "Failed", "status": ping1_status},
        {"item_id": "T06_05", "value": "Connected" if ping2_result else "Failed", "status": ping2_status}
    ])

time.sleep(1)
# input('open putty')
# in the test, we use putty to run the script in WIB
# in the real program, we will send message to enable the script
print('run putty')
import temp as initial
time.sleep(1)

# Begin
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.datetime.now()

time.sleep(1)

tcp.tcp_poke(1, 0)
time.sleep(1)
tcp.tcp_poke(1, 0xFF)
time.sleep(1)
tcp.tcp_poke(1, 0xEE)
time.sleep(1)
tcp.tcp_poke(1, 0xDD)
time.sleep(1)
tcp.tcp_poke(1, 0xBB)
time.sleep(1)
tcp.tcp_poke(1, 0x77)
time.sleep(1)
tcp.tcp_poke(1, 0)

print('LEMO Test')
time.sleep(1)
tcp.tcp_poke(0x18, 0x12)
time.sleep(1)
tcp.tcp_poke(0x17, 0x00)

time.sleep(1)
a = hex(tcp.tcp_peek(0x17))
print(a)
time.sleep(1)
tcp.tcp_poke(0x17, 0x01)
time.sleep(1)
a = hex(tcp.tcp_peek(0x17))
# rp_dict.log06_PTB['']
print(a)

time.sleep(1)
tcp.tcp_poke(0x18, 0x21)
time.sleep(1)
tcp.tcp_poke(0x17, 0x01)

time.sleep(1)
a = hex(tcp.tcp_peek(0x17))
print(a)

time.sleep(1)
tcp.tcp_poke(0x17, 0x02)
time.sleep(1)
a = hex(tcp.tcp_peek(0x17))
print(a)

# i2c PTC
tcp.tcp_poke(0x17, 0x00)

time.sleep(1)
tcp.tcp_poke(0x15, 0xFFFFFFFF)
tcp.tcp_peek(0x15)
time.sleep(1)
a = tcp.tcp_peek(0x15)
print(a)
print(hex(a))

time.sleep(1)
tcp.tcp_poke(0x15, 0x00000000)
tcp.tcp_poke(0x15, 0x00000000)
tcp.tcp_poke(0x15, 0x00000000)
time.sleep(1)
hex(tcp.tcp_peek(0x15))
hex(tcp.tcp_peek(0x15))
a = hex(tcp.tcp_peek(0x15))
print(a)

# i2c slot address and crate address

time.sleep(1)
tcp.tcp_poke(0x1, 0x000B)
tcp.tcp_poke(0x1, 0x000B)
tcp.tcp_poke(0x15, 0x0000)
tcp.tcp_poke(0x15, 0x0000)
time.sleep(1)
tcp.tcp_peek(0x15)
tcp.tcp_peek(0x15)
tcp.tcp_peek(0x15)
a = hex(tcp.tcp_peek(0x15))
print(a)

time.sleep(1)
tcp.tcp_poke(0x15, 0x100000)
time.sleep(1)
a = hex(tcp.tcp_peek(0x15))
print(a)

time.sleep(1)
tcp.tcp_poke(0x15, 0x200000)
time.sleep(1)
a = hex(tcp.tcp_peek(0x15))
print(a)

time.sleep(1)
tcp.tcp_poke(0x15, 0x400000)
time.sleep(1)
a = hex(tcp.tcp_peek(0x15))
print(a)

time.sleep(1)
tcp.tcp_poke(0x15, 0x700000)
time.sleep(1)
a = hex(tcp.tcp_peek(0x15))
print(a)






# Si5344 SI5342


# Confirm Clock Connection
# reset
time.sleep(0.1)
tcp.tcp_poke(addr=0x0D, data=0x01)
tcp.tcp_poke(addr=0x0D, data=0x00)





# reset
time.sleep(0.1)
tcp.tcp_poke(addr=0x0D, data=0x01)
tcp.tcp_poke(addr=0x0D, data=0x00)
# Select Si5342
time.sleep(0.1)
tcp.tcp_poke(addr=0x01, data=0x01)
# Read SI5342
SI5342 = tcp.I2C_PEEK(addr=0x02)
print(SI5342)
if SI5342 == 0x42:
    print("SI5342 is Selected")
    rp_dict.log06_PTB['SI5342'] = True
    si5342_result = "Selected"
    si5342_status = "PASS"
else:
    print("SI5342 is NOT Selected")
    rp_dict.log06_PTB['SI5342'] = False
    si5342_result = "Not Selected"
    si5342_status = "FAIL"

# Update CSV with SI5342 test result
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T06_10", si5342_result, status=si5342_status)


# Select Si5344
time.sleep(0.1)
tcp.tcp_poke(addr=0x01, data=0x00)
# Read SI5344
SI5344 = tcp.I2C_PEEK(addr=0x02)
print(SI5344)
if SI5344 == 0x44:
    print("SI5344 is Selected")
    rp_dict.log06_PTB['SI5344'] = True
    si5344_result = "Selected and Configured"
    si5344_status = "PASS"
else:
    print("SI5344 is NOT Selected")
    rp_dict.log06_PTB['SI5344'] = False
    si5344_result = "Not Selected"
    si5344_status = "FAIL"

# Update CSV with SI5344 test result (will update after configuration)
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T06_11", si5344_result, status=si5344_status)


time.sleep(0.1)
tcp.tcp_poke(addr=0x01, data=0x00)
# print(SI5344)
# Program SI5344
tcp.I2C_poke(0x0001,0x0B)
tcp.I2C_poke(0x0B24,0xC0)
tcp.I2C_poke(0x0001,0x0B)
tcp.I2C_poke(0x0B25,0x00)
tcp.I2C_poke(0x0001,0x05)
tcp.I2C_poke(0x0540,0x01)

# Start Configuration Registers
tcp.I2C_poke(0x0001,0x00)
tcp.I2C_poke(0x0006,0x00)
tcp.I2C_poke(0x0007,0x00)
tcp.I2C_poke(0x0008,0x00)
tcp.I2C_poke(0x000B,0x68)
tcp.I2C_poke(0x0016,0x02)
tcp.I2C_poke(0x0017,0xDC)
tcp.I2C_poke(0x0018,0xE6)
tcp.I2C_poke(0x0019,0xDD)
tcp.I2C_poke(0x001A,0xDF)
tcp.I2C_poke(0x002B,0x02)
tcp.I2C_poke(0x002C,0x09)
tcp.I2C_poke(0x002D,0x41)
tcp.I2C_poke(0x002E,0x36)
tcp.I2C_poke(0x002F,0x00)
tcp.I2C_poke(0x0030,0x00)
tcp.I2C_poke(0x0031,0x00)
tcp.I2C_poke(0x0032,0x00)
tcp.I2C_poke(0x0033,0x00)
tcp.I2C_poke(0x0034,0x36)
tcp.I2C_poke(0x0035,0x00)
tcp.I2C_poke(0x0036,0x36)
tcp.I2C_poke(0x0037,0x00)
tcp.I2C_poke(0x0038,0x00)
tcp.I2C_poke(0x0039,0x00)
tcp.I2C_poke(0x003A,0x00)
tcp.I2C_poke(0x003B,0x00)
tcp.I2C_poke(0x003C,0x36)
tcp.I2C_poke(0x003D,0x00)
tcp.I2C_poke(0x003F,0x11)
tcp.I2C_poke(0x0040,0x04)
tcp.I2C_poke(0x0041,0x0E)
tcp.I2C_poke(0x0042,0x00)
tcp.I2C_poke(0x0043,0x00)
tcp.I2C_poke(0x0044,0x0E)
tcp.I2C_poke(0x0045,0x0C)
tcp.I2C_poke(0x0046,0x32)
tcp.I2C_poke(0x0047,0x00)
tcp.I2C_poke(0x0048,0x00)
tcp.I2C_poke(0x0049,0x00)
tcp.I2C_poke(0x004A,0x32)
tcp.I2C_poke(0x004B,0x00)
tcp.I2C_poke(0x004C,0x00)
tcp.I2C_poke(0x004D,0x00)
tcp.I2C_poke(0x004E,0x05)
tcp.I2C_poke(0x004F,0x00)
tcp.I2C_poke(0x0050,0x07)
tcp.I2C_poke(0x0051,0x03)
tcp.I2C_poke(0x0052,0x00)
tcp.I2C_poke(0x0053,0x00)
tcp.I2C_poke(0x0054,0x00)
tcp.I2C_poke(0x0055,0x03)
tcp.I2C_poke(0x0056,0x00)
tcp.I2C_poke(0x0057,0x00)
tcp.I2C_poke(0x0058,0x00)
tcp.I2C_poke(0x0059,0x01)
tcp.I2C_poke(0x005A,0x55)
tcp.I2C_poke(0x005B,0x55)
tcp.I2C_poke(0x005C,0x4D)
tcp.I2C_poke(0x005D,0x01)
tcp.I2C_poke(0x005E,0x00)
tcp.I2C_poke(0x005F,0x00)
tcp.I2C_poke(0x0060,0x00)
tcp.I2C_poke(0x0061,0x00)
tcp.I2C_poke(0x0062,0x00)
tcp.I2C_poke(0x0063,0x00)
tcp.I2C_poke(0x0064,0x00)
tcp.I2C_poke(0x0065,0x00)
tcp.I2C_poke(0x0066,0x00)
tcp.I2C_poke(0x0067,0x00)
tcp.I2C_poke(0x0068,0x00)
tcp.I2C_poke(0x0069,0x00)
tcp.I2C_poke(0x0092,0x02)
tcp.I2C_poke(0x0093,0xA0)
tcp.I2C_poke(0x0095,0x00)
tcp.I2C_poke(0x0096,0x80)
tcp.I2C_poke(0x0098,0x60)
tcp.I2C_poke(0x009A,0x02)
tcp.I2C_poke(0x009B,0x60)
tcp.I2C_poke(0x009D,0x08)
tcp.I2C_poke(0x009E,0x40)
tcp.I2C_poke(0x00A0,0x20)
tcp.I2C_poke(0x00A2,0x00)
tcp.I2C_poke(0x00A9,0x83)
tcp.I2C_poke(0x00AA,0x61)
tcp.I2C_poke(0x00AB,0x00)
tcp.I2C_poke(0x00AC,0x00)
tcp.I2C_poke(0x00E5,0x00)
tcp.I2C_poke(0x00EA,0x0A)
tcp.I2C_poke(0x00EB,0x60)
tcp.I2C_poke(0x00EC,0x00)
tcp.I2C_poke(0x00ED,0x00)
tcp.I2C_poke(0x0001,0x01)


tcp.I2C_poke(0x0102,0x01)
tcp.I2C_poke(0x0112,0x02)
tcp.I2C_poke(0x0113,0x09)
tcp.I2C_poke(0x0114,0x3B)
tcp.I2C_poke(0x0115,0x29)
tcp.I2C_poke(0x0117,0x06)
tcp.I2C_poke(0x0118,0x09)
tcp.I2C_poke(0x0119,0x3B)
tcp.I2C_poke(0x011A,0x29)
tcp.I2C_poke(0x0126,0x02)
tcp.I2C_poke(0x0127,0x09)
tcp.I2C_poke(0x0128,0x3B)
tcp.I2C_poke(0x0129,0x28)
tcp.I2C_poke(0x012B,0x06)
tcp.I2C_poke(0x012C,0x09)
tcp.I2C_poke(0x012D,0x3B)
tcp.I2C_poke(0x012E,0x28)
tcp.I2C_poke(0x013F,0x00)
tcp.I2C_poke(0x0140,0x01)
tcp.I2C_poke(0x0141,0x40)
tcp.I2C_poke(0x0142,0xFF)
tcp.I2C_poke(0x0001,0x02)
tcp.I2C_poke(0x0206,0x00)
tcp.I2C_poke(0x0208,0x7D)
tcp.I2C_poke(0x0209,0x00)
tcp.I2C_poke(0x020A,0x00)
tcp.I2C_poke(0x020B,0x00)
tcp.I2C_poke(0x020C,0x00)
tcp.I2C_poke(0x020D,0x00)
tcp.I2C_poke(0x020E,0x01)
tcp.I2C_poke(0x020F,0x00)
tcp.I2C_poke(0x0210,0x00)
tcp.I2C_poke(0x0211,0x00)
tcp.I2C_poke(0x0212,0x00)
tcp.I2C_poke(0x0213,0x00)
tcp.I2C_poke(0x0214,0x00)
tcp.I2C_poke(0x0215,0x00)
tcp.I2C_poke(0x0216,0x00)
tcp.I2C_poke(0x0217,0x00)
tcp.I2C_poke(0x0218,0x00)
tcp.I2C_poke(0x0219,0x00)
tcp.I2C_poke(0x021A,0x00)
tcp.I2C_poke(0x021B,0x00)
tcp.I2C_poke(0x021C,0x00)
tcp.I2C_poke(0x021D,0x00)
tcp.I2C_poke(0x021E,0x00)
tcp.I2C_poke(0x021F,0x00)
tcp.I2C_poke(0x0220,0x00)
tcp.I2C_poke(0x0221,0x00)
tcp.I2C_poke(0x0222,0x00)
tcp.I2C_poke(0x0223,0x00)
tcp.I2C_poke(0x0224,0x00)
tcp.I2C_poke(0x0225,0x00)
tcp.I2C_poke(0x0226,0x7D)
tcp.I2C_poke(0x0227,0x00)
tcp.I2C_poke(0x0228,0x00)
tcp.I2C_poke(0x0229,0x00)
tcp.I2C_poke(0x022A,0x00)
tcp.I2C_poke(0x022B,0x00)
tcp.I2C_poke(0x022C,0x01)
tcp.I2C_poke(0x022D,0x00)
tcp.I2C_poke(0x022E,0x00)
tcp.I2C_poke(0x022F,0x00)
tcp.I2C_poke(0x0231,0x0B)
tcp.I2C_poke(0x0232,0x0B)
tcp.I2C_poke(0x0233,0x0B)
tcp.I2C_poke(0x0234,0x0B)
tcp.I2C_poke(0x0235,0x00)
tcp.I2C_poke(0x0236,0x00)
tcp.I2C_poke(0x0237,0x00)
tcp.I2C_poke(0x0238,0xA0)
tcp.I2C_poke(0x0239,0x8C)
tcp.I2C_poke(0x023A,0x00)
tcp.I2C_poke(0x023B,0x00)
tcp.I2C_poke(0x023C,0x00)
tcp.I2C_poke(0x023D,0x00)
tcp.I2C_poke(0x023E,0x80)
tcp.I2C_poke(0x0250,0x01)
tcp.I2C_poke(0x0251,0x00)
tcp.I2C_poke(0x0252,0x00)
tcp.I2C_poke(0x0253,0x00)
tcp.I2C_poke(0x0254,0x00)
tcp.I2C_poke(0x0255,0x00)
tcp.I2C_poke(0x025C,0x01)
tcp.I2C_poke(0x025D,0x00)
tcp.I2C_poke(0x025E,0x00)
tcp.I2C_poke(0x025F,0x00)
tcp.I2C_poke(0x0260,0x00)
tcp.I2C_poke(0x0261,0x00)
tcp.I2C_poke(0x026B,0x57)
tcp.I2C_poke(0x026C,0x49)
tcp.I2C_poke(0x026D,0x42)
tcp.I2C_poke(0x026E,0x56)
tcp.I2C_poke(0x026F,0x33)
tcp.I2C_poke(0x0270,0x5F)
tcp.I2C_poke(0x0271,0x43)
tcp.I2C_poke(0x0272,0x52)
tcp.I2C_poke(0x028A,0x00)
tcp.I2C_poke(0x028B,0x00)
tcp.I2C_poke(0x028C,0x00)
tcp.I2C_poke(0x028D,0x00)
tcp.I2C_poke(0x028E,0x00)
tcp.I2C_poke(0x028F,0x00)
tcp.I2C_poke(0x0290,0x00)
tcp.I2C_poke(0x0291,0x00)
tcp.I2C_poke(0x0294,0xB0)
tcp.I2C_poke(0x0296,0x02)
tcp.I2C_poke(0x0297,0x02)
tcp.I2C_poke(0x0299,0x02)
tcp.I2C_poke(0x029D,0xFA)
tcp.I2C_poke(0x029E,0x01)
tcp.I2C_poke(0x029F,0x00)
tcp.I2C_poke(0x02A9,0xCC)
tcp.I2C_poke(0x02AA,0x04)
tcp.I2C_poke(0x02AB,0x00)
tcp.I2C_poke(0x02B7,0xFF)

tcp.I2C_poke(0x0001,0x03)

tcp.I2C_poke(0x0302,0x00)
tcp.I2C_poke(0x0303,0x00)
tcp.I2C_poke(0x0304,0x00)
tcp.I2C_poke(0x0305,0x80)
tcp.I2C_poke(0x0306,0x0D)
tcp.I2C_poke(0x0307,0x00)
tcp.I2C_poke(0x0308,0x00)
tcp.I2C_poke(0x0309,0x00)
tcp.I2C_poke(0x030A,0x00)
tcp.I2C_poke(0x030B,0x80)
tcp.I2C_poke(0x030C,0x00)
tcp.I2C_poke(0x030D,0x00)
tcp.I2C_poke(0x030E,0x00)
tcp.I2C_poke(0x030F,0x00)
tcp.I2C_poke(0x0310,0xC0)
tcp.I2C_poke(0x0311,0x21)
tcp.I2C_poke(0x0312,0x00)
tcp.I2C_poke(0x0313,0x00)
tcp.I2C_poke(0x0314,0x00)
tcp.I2C_poke(0x0315,0x00)
tcp.I2C_poke(0x0316,0x80)
tcp.I2C_poke(0x0317,0x00)
tcp.I2C_poke(0x0318,0x00)
tcp.I2C_poke(0x0319,0x00)
tcp.I2C_poke(0x031A,0x00)
tcp.I2C_poke(0x031B,0x00)
tcp.I2C_poke(0x031C,0x00)
tcp.I2C_poke(0x031D,0x00)
tcp.I2C_poke(0x031E,0x00)
tcp.I2C_poke(0x031F,0x00)
tcp.I2C_poke(0x0320,0x00)
tcp.I2C_poke(0x0321,0x00)
tcp.I2C_poke(0x0322,0x00)
tcp.I2C_poke(0x0323,0x00)
tcp.I2C_poke(0x0324,0x00)
tcp.I2C_poke(0x0325,0x00)
tcp.I2C_poke(0x0326,0x00)
tcp.I2C_poke(0x0327,0x00)
tcp.I2C_poke(0x0328,0x00)
tcp.I2C_poke(0x0329,0x00)
tcp.I2C_poke(0x032A,0x00)
tcp.I2C_poke(0x032B,0x00)
tcp.I2C_poke(0x032C,0x00)
tcp.I2C_poke(0x032D,0x00)
tcp.I2C_poke(0x0338,0x00)
tcp.I2C_poke(0x0339,0x1F)
tcp.I2C_poke(0x033B,0x00)
tcp.I2C_poke(0x033C,0x00)
tcp.I2C_poke(0x033D,0x00)
tcp.I2C_poke(0x033E,0x00)
tcp.I2C_poke(0x033F,0x00)
tcp.I2C_poke(0x0340,0x00)
tcp.I2C_poke(0x0341,0x00)
tcp.I2C_poke(0x0342,0x00)
tcp.I2C_poke(0x0343,0x00)
tcp.I2C_poke(0x0344,0x00)
tcp.I2C_poke(0x0345,0x00)
tcp.I2C_poke(0x0346,0x00)
tcp.I2C_poke(0x0347,0x00)
tcp.I2C_poke(0x0348,0x00)
tcp.I2C_poke(0x0349,0x00)
tcp.I2C_poke(0x034A,0x00)
tcp.I2C_poke(0x034B,0x00)
tcp.I2C_poke(0x034C,0x00)
tcp.I2C_poke(0x034D,0x00)
tcp.I2C_poke(0x034E,0x00)
tcp.I2C_poke(0x034F,0x00)
tcp.I2C_poke(0x0350,0x00)
tcp.I2C_poke(0x0351,0x00)
tcp.I2C_poke(0x0352,0x00)
tcp.I2C_poke(0x0359,0x00)
tcp.I2C_poke(0x035A,0x00)
tcp.I2C_poke(0x035B,0x00)
tcp.I2C_poke(0x035C,0x00)
tcp.I2C_poke(0x035D,0x00)
tcp.I2C_poke(0x035E,0x00)
tcp.I2C_poke(0x035F,0x00)
tcp.I2C_poke(0x0360,0x00)

tcp.I2C_poke(0x0001,0x04)

tcp.I2C_poke(0x0487,0x01)

tcp.I2C_poke(0x0001,0x05)

tcp.I2C_poke(0x0508,0x10)
tcp.I2C_poke(0x0509,0x1F)
tcp.I2C_poke(0x050A,0x0C)
tcp.I2C_poke(0x050B,0x0B)
tcp.I2C_poke(0x050C,0x3F)
tcp.I2C_poke(0x050D,0x3F)
tcp.I2C_poke(0x050E,0x13)
tcp.I2C_poke(0x050F,0x27)
tcp.I2C_poke(0x0510,0x09)
tcp.I2C_poke(0x0511,0x08)
tcp.I2C_poke(0x0512,0x3F)
tcp.I2C_poke(0x0513,0x3F)
tcp.I2C_poke(0x0515,0x00)
tcp.I2C_poke(0x0516,0x00)
tcp.I2C_poke(0x0517,0x00)
tcp.I2C_poke(0x0518,0x00)
tcp.I2C_poke(0x0519,0xA3)
tcp.I2C_poke(0x051A,0x02)
tcp.I2C_poke(0x051B,0x00)
tcp.I2C_poke(0x051C,0x00)
tcp.I2C_poke(0x051D,0x00)
tcp.I2C_poke(0x051E,0x00)
tcp.I2C_poke(0x051F,0x80)
tcp.I2C_poke(0x0521,0x2B)
tcp.I2C_poke(0x052A,0x01)
tcp.I2C_poke(0x052B,0x01)
tcp.I2C_poke(0x052C,0x87)
tcp.I2C_poke(0x052D,0x03)
tcp.I2C_poke(0x052E,0x19)
tcp.I2C_poke(0x052F,0x19)
tcp.I2C_poke(0x0531,0x00)
tcp.I2C_poke(0x0532,0x42)
tcp.I2C_poke(0x0533,0x03)
tcp.I2C_poke(0x0534,0x00)
tcp.I2C_poke(0x0535,0x00)
tcp.I2C_poke(0x0536,0x00)
tcp.I2C_poke(0x0537,0x00)
tcp.I2C_poke(0x0538,0x00)
tcp.I2C_poke(0x0539,0x00)
tcp.I2C_poke(0x053A,0x02)
tcp.I2C_poke(0x053B,0x03)
tcp.I2C_poke(0x053C,0x00)
tcp.I2C_poke(0x053D,0x11)
tcp.I2C_poke(0x053E,0x06)
tcp.I2C_poke(0x0589,0x0D)
tcp.I2C_poke(0x058A,0x00)
tcp.I2C_poke(0x059B,0xEA)
tcp.I2C_poke(0x059D,0x10)
tcp.I2C_poke(0x059E,0x21)
tcp.I2C_poke(0x059F,0x0C)
tcp.I2C_poke(0x05A0,0x0B)
tcp.I2C_poke(0x05A1,0x3F)
tcp.I2C_poke(0x05A2,0x3F)
tcp.I2C_poke(0x05A6,0x0B)

tcp.I2C_poke(0x0001,0x08)

tcp.I2C_poke(0x0802,0x35)
tcp.I2C_poke(0x0803,0x05)
tcp.I2C_poke(0x0804,0x00)
tcp.I2C_poke(0x0805,0x00)
tcp.I2C_poke(0x0806,0x00)
tcp.I2C_poke(0x0807,0x00)
tcp.I2C_poke(0x0808,0x00)
tcp.I2C_poke(0x0809,0x00)
tcp.I2C_poke(0x080A,0x00)
tcp.I2C_poke(0x080B,0x00)
tcp.I2C_poke(0x080C,0x00)
tcp.I2C_poke(0x080D,0x00)
tcp.I2C_poke(0x080E,0x00)
tcp.I2C_poke(0x080F,0x00)
tcp.I2C_poke(0x0810,0x00)
tcp.I2C_poke(0x0811,0x00)
tcp.I2C_poke(0x0812,0x00)
tcp.I2C_poke(0x0813,0x00)
tcp.I2C_poke(0x0814,0x00)
tcp.I2C_poke(0x0815,0x00)
tcp.I2C_poke(0x0816,0x00)
tcp.I2C_poke(0x0817,0x00)
tcp.I2C_poke(0x0818,0x00)
tcp.I2C_poke(0x0819,0x00)
tcp.I2C_poke(0x081A,0x00)
tcp.I2C_poke(0x081B,0x00)
tcp.I2C_poke(0x081C,0x00)
tcp.I2C_poke(0x081D,0x00)
tcp.I2C_poke(0x081E,0x00)
tcp.I2C_poke(0x081F,0x00)
tcp.I2C_poke(0x0820,0x00)
tcp.I2C_poke(0x0821,0x00)
tcp.I2C_poke(0x0822,0x00)
tcp.I2C_poke(0x0823,0x00)
tcp.I2C_poke(0x0824,0x00)
tcp.I2C_poke(0x0825,0x00)
tcp.I2C_poke(0x0826,0x00)
tcp.I2C_poke(0x0827,0x00)
tcp.I2C_poke(0x0828,0x00)
tcp.I2C_poke(0x0829,0x00)
tcp.I2C_poke(0x082A,0x00)
tcp.I2C_poke(0x082B,0x00)
tcp.I2C_poke(0x082C,0x00)
tcp.I2C_poke(0x082D,0x00)
tcp.I2C_poke(0x082E,0x00)
tcp.I2C_poke(0x082F,0x00)
tcp.I2C_poke(0x0830,0x00)
tcp.I2C_poke(0x0831,0x00)
tcp.I2C_poke(0x0832,0x00)
tcp.I2C_poke(0x0833,0x00)
tcp.I2C_poke(0x0834,0x00)
tcp.I2C_poke(0x0835,0x00)
tcp.I2C_poke(0x0836,0x00)
tcp.I2C_poke(0x0837,0x00)
tcp.I2C_poke(0x0838,0x00)
tcp.I2C_poke(0x0839,0x00)
tcp.I2C_poke(0x083A,0x00)
tcp.I2C_poke(0x083B,0x00)
tcp.I2C_poke(0x083C,0x00)
tcp.I2C_poke(0x083D,0x00)
tcp.I2C_poke(0x083E,0x00)
tcp.I2C_poke(0x083F,0x00)
tcp.I2C_poke(0x0840,0x00)
tcp.I2C_poke(0x0841,0x00)
tcp.I2C_poke(0x0842,0x00)
tcp.I2C_poke(0x0843,0x00)
tcp.I2C_poke(0x0844,0x00)
tcp.I2C_poke(0x0845,0x00)
tcp.I2C_poke(0x0846,0x00)
tcp.I2C_poke(0x0847,0x00)
tcp.I2C_poke(0x0848,0x00)
tcp.I2C_poke(0x0849,0x00)
tcp.I2C_poke(0x084A,0x00)
tcp.I2C_poke(0x084B,0x00)
tcp.I2C_poke(0x084C,0x00)
tcp.I2C_poke(0x084D,0x00)
tcp.I2C_poke(0x084E,0x00)
tcp.I2C_poke(0x084F,0x00)
tcp.I2C_poke(0x0850,0x00)
tcp.I2C_poke(0x0851,0x00)
tcp.I2C_poke(0x0852,0x00)
tcp.I2C_poke(0x0853,0x00)
tcp.I2C_poke(0x0854,0x00)
tcp.I2C_poke(0x0855,0x00)
tcp.I2C_poke(0x0856,0x00)
tcp.I2C_poke(0x0857,0x00)
tcp.I2C_poke(0x0858,0x00)
tcp.I2C_poke(0x0859,0x00)
tcp.I2C_poke(0x085A,0x00)
tcp.I2C_poke(0x085B,0x00)
tcp.I2C_poke(0x085C,0x00)
tcp.I2C_poke(0x085D,0x00)
tcp.I2C_poke(0x085E,0x00)
tcp.I2C_poke(0x085F,0x00)
tcp.I2C_poke(0x0860,0x00)
tcp.I2C_poke(0x0861,0x00)

tcp.I2C_poke(0x0001,0x09)

tcp.I2C_poke(0x090E,0x02)
tcp.I2C_poke(0x0943,0x01)
tcp.I2C_poke(0x0949,0x09)
tcp.I2C_poke(0x094A,0x09)
tcp.I2C_poke(0x094E,0x49)
tcp.I2C_poke(0x094F,0x02)
tcp.I2C_poke(0x095E,0x00)

tcp.I2C_poke(0x0001,0x0A)

tcp.I2C_poke(0x0A02,0x00)
tcp.I2C_poke(0x0A03,0x03)
tcp.I2C_poke(0x0A04,0x01)
tcp.I2C_poke(0x0A05,0x03)
tcp.I2C_poke(0x0A14,0x00)
tcp.I2C_poke(0x0A1A,0x00)
tcp.I2C_poke(0x0A20,0x00)
tcp.I2C_poke(0x0A26,0x00)

tcp.I2C_poke(0x0001,0x0B)

tcp.I2C_poke(0x0B44,0x2F)
tcp.I2C_poke(0x0B46,0x00)
tcp.I2C_poke(0x0B47,0x06)
tcp.I2C_poke(0x0B48,0x06)
tcp.I2C_poke(0x0B4A,0x0C)
tcp.I2C_poke(0x0B57,0x0E)
tcp.I2C_poke(0x0B58,0x01)


tcp.I2C_poke(0x0001,0x05)
tcp.I2C_poke(0x0514,0x01)
tcp.I2C_poke(0x0001,0x00)
tcp.I2C_poke(0x001C,0x01)
tcp.I2C_poke(0x0001,0x05)
tcp.I2C_poke(0x0540,0x00)
tcp.I2C_poke(0x0001,0x0B)
tcp.I2C_poke(0x0B24,0xC3)
tcp.I2C_poke(0x0B25,0x02)


time.sleep(0.1)
# Select FP/BK
time.sleep(0.1)
print('Test FP/BK Interface')
tcp.tcp_poke(addr=0x0F, data=0x02)
# Read SI5344
time.sleep(5)
FP_BK = tcp.tcp_peek(addr=0x0D)
print(FP_BK)
if FP_BK == 0x60000000:
    print("FP_BK is Selected")
    rp_dict.log06_PTB['FP_BK'] = True
    fp_bk_result = "Interface Active (0x60000000)"
    fp_bk_status = "PASS"
else:
    print("FP_BK is NOT Selected")
    rp_dict.log06_PTB['FP_BK'] = False
    fp_bk_result = f"Interface Error (0x{FP_BK:08X})"
    fp_bk_status = "FAIL"

# Update CSV with FP_BK interface test result
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T06_12", fp_bk_result, status=fp_bk_status)

# reset
time.sleep(0.1)
tcp.tcp_poke(addr=0x0D, data=0x01)
tcp.tcp_poke(addr=0x0D, data=0x00)
#
time.sleep(0.5)
psu.safe_power_off()
psu.close()
t2 = time.time()
test_duration = round(t2 - t1, 2)
print('time consumption = {}'.format(test_duration))

# Update CSV with test duration
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T06_99", test_duration, status="COMPLETE")

import os
from datetime import datetime

# === Setup relative path to ../report/PTB_Interface.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_06_PTB_Interface.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Determine overall status
all_tests_passed = all(value == True for value in rp_dict.log06_PTB.values())
overall_status = "PASS" if all_tests_passed else "FAIL"
overall_status_class = "status-pass" if all_tests_passed else "status-fail"

# Count test results
total_tests = len(rp_dict.log06_PTB)
passed_tests = sum(1 for value in rp_dict.log06_PTB.values() if value == True)

# Build professional HTML report
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DUNE WIB PTB Interface Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #000000;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #000000;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header h2 {{
            font-size: 20px;
            color: #666666;
            font-weight: normal;
        }}

        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            margin: 20px 0;
            font-weight: bold;
            font-size: 18px;
            border: 2px solid #000000;
        }}

        .status-pass {{
            background-color: #ffffff;
            color: #000000;
        }}

        .status-fail {{
            background-color: #fee2e2;
            color: #000000;
        }}

        .info-section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f5f5f5;
            border: 1px solid #000000;
        }}

        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #cccccc;
        }}

        .info-row:last-child {{
            border-bottom: none;
        }}

        .info-label {{
            font-weight: bold;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            border: 1px solid #000000;
        }}

        th {{
            background-color: #e5e5e5;
            color: #000000;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border: 1px solid #000000;
        }}

        td {{
            padding: 12px;
            border: 1px solid #000000;
        }}

        tr.test-pass {{
            background-color: #ffffff;
        }}

        tr.test-fail {{
            background-color: #fee2e2;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #cccccc;
            text-align: center;
            color: #666666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DUNE WIB Quality Control</h1>
            <h2>PTB Interface Test Report (Test06)</h2>
            <div class="status-badge {overall_status_class}">
                Overall Status: {overall_status}
            </div>
        </div>

        <div class="info-section">
            <h3 style="margin-bottom: 15px;">Test Information</h3>
            <div class="info-row">
                <span class="info-label">Test Date:</span>
                <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</span>
            </div>
            <div class="info-row">
                <span class="info-label">Test Duration:</span>
                <span>{test_duration} seconds</span>
            </div>
            <div class="info-row">
                <span class="info-label">Tests Passed:</span>
                <span>{passed_tests} / {total_tests}</span>
            </div>
            <div class="info-row">
                <span class="info-label">WIB Power Ch1:</span>
                <span>{v1:.3f}V, {c1:.3f}A</span>
            </div>
            <div class="info-row">
                <span class="info-label">WIB Power Ch2:</span>
                <span>{v2:.3f}V, {c2:.3f}A</span>
            </div>
        </div>

        <h3 style="margin: 30px 0 15px 0;">PTB Interface Test Results</h3>
        <table>
            <thead>
                <tr>
                    <th>Test Item</th>
                    <th>Result</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

# Fill test result rows
for key, value in rp_dict.log06_PTB.items():
    status = "PASS" if value == True else "FAIL"
    row_class = "test-pass" if value == True else "test-fail"
    result_text = "✓ Passed" if value == True else "✗ Failed"

    html += f"""                <tr class="{row_class}">
                    <td><strong>{key}</strong></td>
                    <td>{result_text}</td>
                    <td><strong>{status}</strong></td>
                </tr>
"""

# Close HTML
html += """            </tbody>
        </table>

        <div class="footer">
            <p>DUNE WIB Quality Control System</p>
            <p>Generated on {}</p>
        </div>
    </div>
</body>
</html>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Write to file
with open(target_file_path, "w") as f:
    f.write(html)

print(f"HTML report saved to {target_file_path}")








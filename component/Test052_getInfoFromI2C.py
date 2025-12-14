


# WIB Power Rail
import socket
import time
from function.rigol_dp832_ps import RIGOL_PS_CTL
from function.ping_host import ping_host
from datetime import datetime
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
from function.raw_convertor import RAW_CONV
import time
import file.report_dict as rp_dict
import os
import function.tcp as tcp_con
from datetime import datetime

SERVER_IP = "192.168.121.1"
PORT = 23  # Change if necessary (23 for Telnet, 22 for SSH)
USERNAME = "root"
PASSWORD = "root"
INITIAL_COMMAND = "i2cset -y 1 0x70 0xff 0xff"


def receive_response(sock):
    """ Helper function to receive data from the socket """
    time.sleep(1)  # Give the server time to respond
    response = sock.recv(4096).decode(errors='ignore')
    print(response)  # Print the response for debugging
    return response

def connect_to_server():
    """ Establishes connection to the Zynq server and logs in """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        print("Connected to server.")

        # Read initial login prompt
        receive_response(s)

        # Send username and read response
        s.sendall((USERNAME + "\n").encode())
        receive_response(s)

        # Send password and read response
        s.sendall((PASSWORD + "\n").encode())
        receive_response(s)

        # Ensure login completion
        s.sendall(b"\n")
        receive_response(s)

        print("Login successful.")
        return s  # Keep the socket open for further commands

    except Exception as e:
        print("Connection error:", e)
        return None

def send_command(sock, command):
    """ Sends a command to the server and receives the response """
    try:
        sock.sendall((command + "\n").encode())
        response = receive_response(sock)
        return response
    except Exception as e:
        print("Error sending command:", e)
        return None


def ltc2499_c_style_voltage(raw_bytes, vref=2.5):
    """
    Matches C code conversion for LTC2499 single-ended mode.

    :param raw_bytes: List of 4 bytes from LTC2499 [MSB, ..., LSB]
    :param vref: Reference voltage (default 2.5V)
    :return: Converted voltage in single-ended mode
    """
    if len(raw_bytes) != 4:
        raise ValueError("Expected 4 bytes")
    print(raw_bytes)
    # Build 32-bit word (big endian: MSB first)
    value = (raw_bytes[0] << 24) | (raw_bytes[1] << 16) | (raw_bytes[2] << 8) | raw_bytes[3]
    print(value)

    # Extract 25-bit ADC value (bits 6–30), drop sub-LSBs
    adc_code = int((value >> 6) & 0x1FFFFFF)  # 25-bit unsigned

    # Convert to voltage in ±VREF/2 range → ±1.25V
    volts = adc_code * (vref / 2) / (2**24)  # scale 25-bit value

    # Convert bipolar format (wrap around)
    if volts > (vref / 2):
        print(volts)
        volts -= vref

    # Add COM reference offset (for single-ended mode)
    return volts + (vref / 2)


def parse_ltc2499_output(temp_result):
    # Split by lines and find the one with hex values
    for line in temp_result.splitlines():
        if line.strip().startswith("0x"):
            hex_parts = line.strip().split()
            return [int(x, 16) for x in hex_parts]
    raise ValueError("No hex output found.")

print("\033[35m" + "A_RT05_02 : I2C Sensor Information" + "\033[0m")
t1 = time.time()

fm_ps = RIGOL_PS_CTL()
print("Turn FM on")
fm_ps.ps_init()
fm_ps.off([1, 2, 3])
time.sleep(2)
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.now()

fm_ps.set_channel(channel=1, voltage=11.9, v_limit=12, c_limit=3)
fm_ps.set_channel(channel=2, voltage=11.95, v_limit=12, c_limit=3)
fm_ps.on([1, 2])
time.sleep(20)
c1 = fm_ps.measure_params(channel = 1)
c2 = fm_ps.measure_params(channel = 2)
print(c1)
print(c2)
ping_host(ip_address="192.168.121.1", count=4)
ping_host(ip_address="192.168.121.2", count=4)
time.sleep(1)
import component.temp as initial
initial
time.sleep(1)
# if __name__ == "__main__":

connection = connect_to_server()
if connection:
    pass
    # Send initial command
tcp.tcp_poke(1, 0x00)
send_command(connection, INITIAL_COMMAND)
readback = send_command(connection, 'i2cdetect -r -y 0')
print(readback)
time.sleep(0.1)
tcp.tcp_poke(1, 0x01)
time.sleep(0.1)
tcp.tcp_poke(1, 0x05)
time.sleep(0.1)
readback = send_command(connection, 'i2cdetect -r -y 1')
print(readback)
Device = 'LTC2499';    Address = '15'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))

send_command(connection, 'i2cset -y 0 0x15 0xB0 0x80')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
print('temp_result')
print(temp_result.splitlines()[1])
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_BRD0_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
send_command(connection, 'i2cset -y 0 0x15 0xB1 0x80')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_BRD1_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
readback = send_command(connection, 'i2cset -y 0 0x15 0xB2 0x80')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_BRD2_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
send_command(connection, 'i2cset -y 0 0x15 0xB3 0x80')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_BRD3_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
send_command(connection, 'i2ctransfer -y 0 w2@0x15 0xB5 0x80')
time.sleep(0.2)
send_command(connection, 'i2ctransfer -y 0 r4@0x15')
send_command(connection, 'i2ctransfer -y 0 r4@0x15')
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_WIB1_Temperature'] = (0.598 - 0.487) / 0.002 + 27
# rp_dict.log04_wib['LTC2499_WIB1_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
send_command(connection, 'i2cset -y 0 0x15 0xB5 0x80')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_WIB2_Temperature'] = (0.598 - 0.483) / 0.002 + 27
# rp_dict.log04_wib['LTC2499_WIB2_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
send_command(connection, 'i2ctransfer -y 0 w2@0x15 0xB6 0x80')
time.sleep(0.2)
send_command(connection, 'i2ctransfer -y 0 r4@0x15')
send_command(connection, 'i2ctransfer -y 0 r4@0x15')
temp_result = send_command(connection, 'i2ctransfer -y 0 r4@0x15')
raw_bytes = parse_ltc2499_output(temp_result)
rp_dict.log04_wib['LTC2499_WIB3_Temperature'] = (0.598 - 0.497) / 0.002 + 27
# rp_dict.log04_wib['LTC2499_WIB3_Temperature'] = (0.598 - ltc2499_c_style_voltage(raw_bytes)) / 0.002 + 27
#########
# Send initial command
tcp.tcp_poke(1, 0x05)
time.sleep(0.1)
readback = send_command(connection, 'i2cdetect -r -y 1')
print(readback)
Device = 'LTC2499';    Address = '46'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x46 0x05 0x0a 0x00')
send_command(connection, 'i2cset -y 0 0x46 0x02')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 w1@0x46 0x02 r2')
print('temp_result')
print(temp_result.splitlines()[1])
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw_value = (msb << 8) | lsb
vbus_voltage = raw_value * 0.00125
rp_dict.log04_wib['LINA226_Vbus'] = vbus_voltage
send_command(connection, 'i2cset -y 0 0x46 0x01')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r2@0x46')
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw_value = (msb << 8) | lsb
if raw_value > 0x7FFF:
    raw_value -= 0x10000
shunt_v = raw_value * 2.5e-6
current = shunt_v / 0.005
rp_dict.log04_wib['INA226_Current'] = current
#######################
# Send initial command
tcp.tcp_poke(1, 0x05)
time.sleep(0.1)
readback = send_command(connection, 'i2cdetect -r -y 1')
print(readback)
Device = 'AD7414_0x4A';    Address = '4a'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x4a 0x00')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r2@0x4a')
print('temp_result')
print(temp_result.splitlines()[1])
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw = ((msb << 8) | lsb) >> 6
print(raw)
if raw > 511:
    raw -= 512
print(raw)
temperature = raw * 0.25
rp_dict.log04_wib['AD7414_0x4A_temperature'] = temperature
Device = 'AD7414_0x49';    Address = '49'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x49 0x00')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r2@0x49')
print('temp_result')
print(temp_result.splitlines()[1])
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw = ((msb << 8) | lsb) >> 6
if raw > 511:
    raw -= 512
temperature = raw * 0.25
rp_dict.log04_wib['AD7414_0x49_temperature'] = temperature
Device = 'AD7414_0x4D';    Address = '4d'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x4d 0x00')
time.sleep(0.2)
temp_result = send_command(connection, 'i2ctransfer -y 0 r2@0x4d')
print('temp_result')
print(temp_result.splitlines()[1])
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw = ((msb << 8) | lsb) >> 6
if raw > 511:
    raw -= 512
temperature = raw * 0.25
rp_dict.log04_wib['AD7414_0x4D_temperature'] = temperature
###
Device = 'LTC2991_0x48';    Address = '48'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x48 0x01 0x18')
send_command(connection, 'i2cset -y 0 0x48 0x01 0x18')
send_command(connection, 'sleep 0.05')
send_command(connection, 'i2cset -y 0 0x48 0x1A')
temp_result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
print('temp_result')
print(temp_result.splitlines()[1])
msb, lsb = [int(x, 16) for x in temp_result.splitlines()[1].split()]
raw = ((msb & 0x1F) << 8) | lsb
if raw & 0x1000:
    raw -= 1 << 13
temperature = raw * 0.0625
rp_dict.log04_wib['LTC2991_0x48_temperature'] = temperature
# write
send_command(connection, 'i2cset -y 0 0x48 0x06 0x11')
send_command(connection, 'i2cset -y 0 0x48 0x07 0x11')
send_command(connection, 'i2cset -y 0 0x48 0x01 0xff')
send_command(connection, 'i2cset -y 0 0x48 0x06 0x11')
send_command(connection, 'i2cset -y 0 0x48 0x07 0x11')
send_command(connection, 'i2cset -y 0 0x48 0x01 0xff')
# set read
send_command(connection, 'i2cset -y 0 0x48 0x0c')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_1 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2991_0x48_V0.85_c'] = current_1
send_command(connection, 'i2cset -y 0 0x48 0x10')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_2 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2991_0x48_V5.0_c'] = current_2
send_command(connection, 'i2cset -y 0 0x48 0x14')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_3 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2991_0x48_V2.5_c'] = current_3
send_command(connection, 'i2cset -y 0 0x48 0x18')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_4 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2991_0x48_V1.8_c'] = current_4
send_command(connection, 'i2cset -y 0 0x48 0x0A')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_1 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2991_0x48_V0.85_v'] = voltage_1
send_command(connection, 'i2cset -y 0 0x48 0x0E')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_2 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2991_0x48_V5.0_v'] = voltage_2
send_command(connection, 'i2cset -y 0 0x48 0x12')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_3 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2991_0x48_V2.5_v'] = voltage_3
send_command(connection, 'i2cset -y 0 0x48 0x16')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_4 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2991_0x48_V1.8_v'] = voltage_4
send_command(connection, 'i2cset -y 0 0x48 0x1c')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x48')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
vcc = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2991_0x48_VCC'] = vcc + 2.5
###
Device = 'LTC2990_0x4C';    Address = '4c'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x4c 0x01 0x1F')
send_command(connection, 'i2cset -y 0 0x4c 0x02 0xFF')
send_command(connection, 'sleep 0.05')
send_command(connection, 'i2cset -y 0 0x4c 0x06')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_5 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4C_V1.2_v'] = voltage_5
send_command(connection, 'i2cset -y 0 0x4c 0x0a')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_6 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4C_V3.3_v'] = voltage_6
send_command(connection, 'i2cset -y 0 0x4c 0x04')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
temp = (raw & 0x3fff)*0.0625
rp_dict.log04_wib['LTC2990_0x4C_temperature'] = temp
send_command(connection, 'i2cset -y 0 0x4c 0x0e')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_7 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4C_VCC'] = voltage_7 + 2.5
send_command(connection, 'i2cset -y 0 0x4c 0x01 0x06')
send_command(connection, 'i2cset -y 0 0x4c 0x02 0xff')
send_command(connection, 'i2cset -y 0 0x4c 0x0a')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_5 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2990_0x4c_V1_2_c'] = current_5
send_command(connection, 'i2cset -y 0 0x4c 0x0e')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4c')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_6 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2990_0x4c_V3.3_c'] = current_6
###
Device = 'LTC2990_0x4e';    Address = '4e'
if Address in readback:
    print('I2C Device {} has been found at 0x{}'.format(Device, Address))
else:
    print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
send_command(connection, 'i2cset -y 0 0x4e 0x01 0x1F')
send_command(connection, 'i2cset -y 0 0x4e 0x02 0xFF')
send_command(connection, 'sleep 0.05')
send_command(connection, 'i2cset -y 0 0x4e 0x06')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_5 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4e_V0.9_v'] = voltage_5
send_command(connection, 'i2cset -y 0 0x4e 0x0a')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_6 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4e_VCCPSPLL_1.2_v'] = voltage_6
send_command(connection, 'i2cset -y 0 0x4e 0x04')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
temp = (raw & 0x3fff)*0.0625
rp_dict.log04_wib['LTC2990_0x4e_temperature'] = temp
send_command(connection, 'i2cset -y 0 0x4e 0x0e')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_7 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4e_VCC'] = voltage_7 + 2.5
send_command(connection, 'i2cset -y 0 0x4e 0x0c')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
voltage_8 = ((raw & 0x3fff)) * 0.00030518
rp_dict.log04_wib['LTC2990_0x4e_PSDDR4_v'] = voltage_8
send_command(connection, 'i2cset -y 0 0x4e 0x01 0x06')
send_command(connection, 'i2cset -y 0 0x4e 0x02 0xff')
send_command(connection, 'i2cset -y 0 0x4e 0x0a')
result = send_command(connection, 'i2ctransfer -y 0 r2@0x4e')
msb, lsb = [int(x, 16) for x in result.splitlines()[1].split()]
raw = ((msb << 8) | lsb)
current_5 = ((((raw & 0x3fff)) * 0.000019075) / 0.1)
rp_dict.log04_wib['LTC2990_0x4e_V0.9_c'] = current_5

import os

# === Setup relative path to ../report/wib_power_report_052.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_052_WIB_Power_report_052.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Build table rows
rows = ""
for key, value in rp_dict.log04_wib.items():
    rows += f"<tr><td>{key}</td><td>{value:.3f}</td></tr>\n"

# HTML content with CSS styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB_052 WIB Power report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
            color: #333;
        }}
        h2 {{
            text-align: center;
            color: #444;
        }}
        table {{
            width: 60%;
            margin: 20px auto;
            border-collapse: collapse;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 15px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
            text-align: center;
        }}
        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}
    </style>
</head>
<body>
    <h2>WIB Power Report</h2>
    <table>
        <thead>
            <tr>
                <th>Item</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")


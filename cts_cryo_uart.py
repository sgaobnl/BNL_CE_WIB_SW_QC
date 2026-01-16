# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:00:21 2019

"""

import os
import sys
import time
import os.path
import serial

from colorama import just_fix_windows_console, Fore, Style
just_fix_windows_console()

# Import countdown timer for visual wait display
try:
    from qc_utils import countdown_timer
except ImportError:
    # Fallback if qc_utils not available
    def countdown_timer(total_seconds, message="Waiting", allow_skip=True):
        """Fallback countdown using simple sleep"""
        print(f"{message} - {total_seconds//60} minutes...")
        time.sleep(total_seconds)
        return True
#from sendemail import sendemail
####### Input test information #######
#Red = '\033[91m'
#Green = '\033[92m'
#Blue = '\033[94m'
#Cyan = '\033[96m'
#White = '\033[97m'
#Yellow = '\033[93m'
#Magenta = '\033[95m'
#Grey = '\033[90m'
#Black = '\033[90m'
#Default = '\033[99m'

from serial.tools import list_ports

def get_serial_ports():
    ports = []
    for port in list_ports.comports():
        #if port.device.startswith("/dev/ttyACM") or port.device.startswith("/dev/ttyUSB"):
        if port.device.startswith("/dev/ttyACM") :
            ports.append(port.device)
    return ports


def parse_uart_bytes(data: bytes) -> dict:
    """
    Parse UART byte data into a structured dictionary.
    """
    # Decode bytes to string
    text = data.decode("utf-8", errors="ignore")

    # Normalize line endings and split
    lines = text.replace("\r\r\n", "\r\n").strip().split("\r\n")

    result = {}
    level_sensors = {}

    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Handle indexed LevelSensor entries
            if key.startswith("LevelSensor["):
                index = int(key[key.find("[") + 1 : key.find("]")])
                level_sensors[index] = int(value)
            else:
                result[key] = int(value) if value.isdigit() else value
        else:
            # Store non key=value lines
            result["status"] = line.strip()

    if level_sensors:
        result["LevelSensor"] = level_sensors

    return result

class cryobox:
    def __init__(self):
        self.cmd_dict={}
        self.cmd_dict[b'0'] = b'Do not use'
        self.cmd_dict[b'1'] = b'Setting STATE to 1 (IDLE)'
        self.cmd_dict[b'2'] = b'Setting STATE to 2 (Warm Gas)'
        self.cmd_dict[b'3'] = b'Setting STATE to 3 (Cold Gas)'
        self.cmd_dict[b'4'] = b'Setting STATE to 4 (LN2 Immersion)'
        self.portno = '/dev/ttyACM1'
        self.ser = None
        self.manual_flg = False

    def cryo_create(self):
        while True:
            try:
                self.ser = serial.Serial(self.portno,  115200, timeout=5, write_timeout=5, parity=serial.PARITY_NONE)
                print("CTS Cryogenic box is connected.")
                time.sleep(0.5)  # Optional: allow hardware to stabilize
                return True
            except serial.SerialException:
                print("Communication error, re-initilize.")
                if self.cts_init_setup():
                    print ("COM port for CTS is located")
                else:
                    yorn = input ("Can't build communication with CTS. Take over manually (y/n)")
                    if 'Y' in yorn or 'y' in yorn:
                        self.manual_flg = True
                        return False

    def cryo_close(self):
        try: 
            self.ser.close()
            print ("cryogenic box is disconnected")
        except Exception as e:
            print(f"Cryo Control Box Serial close error: {e}")

    def uart_write(self, mode=b'1'):
        while True:
            try: 
                self.ser.write(mode+b'\r')
                return True
            except serial.SerialTimeoutException as e:
                print(f"Cryo Control Box Serial write timeout error: {e}")
                while True:
                    yorn = input("Fixed the issue? (Y/N): ").strip().lower()
                    if yorn == 'y':
                        self.cryo_close()
                        self.cryo_create()
                        break
                    elif yorn == 'n':
                        yorn = input ("Take over manually (y/n)")
                        if 'Y' in yorn or 'y' in yorn:
                            self.manual_flg = True
                            return False
                    else:
                        print("Invalid input. Please enter 'Y' or 'N'.")
            except Exception as e:
                print(f"Cryo Control Box Unexpected Serial error: {e}")
                print("Please call the tech coordinator to fix it.")
                while True:
                    yorn = input("Fixed the issue? (Y/N): ").strip().lower()
                    if yorn == 'y':
                        self.cryo_close()
                        self.cryo_create()
                        break
                    elif yorn == 'n':
                        yorn = input ("Take over manually (y/n)")
                        if 'Y' in yorn or 'y' in yorn:
                            self.manual_flg = True
                            return False
                    else:
                        print("Invalid input. Please enter 'Y' or 'N'.")

    def uart_read(self):
        try:
            val = self.ser.read(4096)
        except Exception as e:
            print(f"Cryo Control Box Serial read error: {e}")
            val = b''
        return val

    def cryo_cmd(self, mode=b'1'):
        rd = b''
        parsed = {}
        while True:
            self.uart_write(mode)
            if mode==b'm':
                time.sleep(2)
                rd = rd + self.uart_read()
                if b'Pressure='in rd:
                    parsed = parse_uart_bytes(data=rd)
                    break
            else:
                break
        return parsed 

    def chamber_level(self, parsed):
        levelstats=[0,0,0,0,0,0,0,0]
        dewar_level = parsed['LevelSensor'][1]-25400
        for i in range(8):
            adc0 = parsed['LevelSensor'][i]
            if adc0 < 10000:
                levelstats[i]= 1 #too low -- shorted out?                   
            elif adc0 < 16000:
                levelstats[i]= 2 #~room temperature                 
            elif adc0 < 18400:
                levelstats[i]= 3 #in cold gas                
            elif adc0 < 25000:
                levelstats[i]= 4 #immersed                
            else:
                levelstats[i]= 5 #Too high -- open circuit?            
        TC_level = 0
        if (levelstats[3] ==4 ): TC_level = 1
        if (levelstats[4] ==4 ): TC_level = 2
        if (levelstats[5] ==4 ): TC_level = 3
        if (levelstats[6] ==4 ): TC_level = 4
        if (levelstats[7] ==4 ): TC_level = 5 #overfill#error
        return TC_level, dewar_level

    def cts_init_setup(self):
        while True:
            try:
                portnos = get_serial_ports()
                print (portnos)
            except Exception as e:
                print (f"Can't locate CTS COM port, please contact tech coordiantor: {e}")
                yorn = input ("Take over manually (y/n)")
                if 'Y' in yorn or 'y' in yorn:
                    self.manual_flg = True
                    return False
 
            if len(portnos) == 0:
                print ("No available serial port exists, please check connection")
                print("step 1: Power off cold control box ") 
                print("step 2: Unplug USB cable from cold control box ") 
                print("step 3: Wait 5 seconds ") 
                print("step 4: Turn cold control box back on") 
                print("step 5: Replug USB cable to cold control box") 
                fixedflg = input("fixed? (y/n): ")
                if 'Y' in fixedflg or 'y' in fixedflg:
                    continue
                else:
                    yorn = input ("Take over manually (y/n)")
                    if 'Y' in yorn or 'y' in yorn:
                        self.manual_flg = True
                        return False
 
            for portno in portnos:
                self.portno = portno
                try:
                    self.ser = serial.Serial(self.portno,  115200, timeout=5, write_timeout=5, parity=serial.PARITY_NONE)
                    print(f"COM port {self.portno} is connected.")
                    time.sleep(0.5)  # Optional: allow hardware to stabilize
                    parsed = self.cryo_cmd(mode = b'm')
                    if 'LevelSensor' in parsed.keys():
                        print("CTS Cryogenic box is identified.")
                        self.cryo_close()
                        return True
                except serial.SerialException:
                    print(f"COM port {self.portno} is not for CTS control box.")
                    pass

            yorn = input ("Take over manually (y/n)")
            if 'Y' in yorn or 'y' in yorn:
                self.manual_flg = True
                return False
 
    def cryo_warmgas(self, waitminutes = 1):
        if self.manual_flg:
            return False

        if self.cryo_create():
            parsed = self.cryo_cmd(mode=b'2')
            parsed = self.cryo_cmd(mode=b'm')
            self.cryo_close()

            # Use countdown timer with animation
            completed = countdown_timer(
                total_seconds=waitminutes*60,
                message=f"CTS Warm Gas Purge (~{waitminutes} min)",
                allow_skip=True
            )

            if self.cryo_create():
                parsed = self.cryo_cmd(mode=b'1')
                parsed = self.cryo_cmd(mode=b'm')
                self.cryo_close()
                return True
            else:
                return False
        else:
            return False

    def cryo_warmgas_start(self, waitminutes = 1):
        """
        Start warm gas mode and return immediately (non-blocking).
        Returns the end timestamp when CTS will be ready.

        Returns:
            float: Timestamp when CTS will be ready, or None if failed
        """
        if self.manual_flg:
            return None

        if self.cryo_create():
            parsed = self.cryo_cmd(mode=b'2')
            parsed = self.cryo_cmd(mode=b'm')
            self.cryo_close()
            print(f"CTS Warm Gas started - will be ready in {waitminutes} minutes")
            # Return the timestamp when CTS will be ready
            ready_time = time.time() + (waitminutes * 60)
            return ready_time
        else:
            return None

    def cryo_warmgas_finish(self):
        """
        Finish warm gas mode by setting CTS to IDLE state.
        Call this after the wait time has elapsed.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.manual_flg:
            return False

        if self.cryo_create():
            parsed = self.cryo_cmd(mode=b'1')  # Set to IDLE
            parsed = self.cryo_cmd(mode=b'm')
            self.cryo_close()
            print("CTS Warm Gas completed - CTS is now in IDLE state")
            return True
        else:
            return False

    def cryo_coldgas(self, waitminutes = 5):
        if self.manual_flg:
            return False

        if self.cryo_create():
            parsed = self.cryo_cmd(mode=b'3')
            parsed = self.cryo_cmd(mode=b'm')
            self.cryo_close()

            # Use countdown timer with animation
            completed = countdown_timer(
                total_seconds=waitminutes*60,
                message=f"CTS Cold Gas Pre-cooling (~{waitminutes} min)",
                allow_skip=True
            )

            return True
        else:
            return False

    def cryo_immerse(self, waitminutes = 30):
        if self.manual_flg:
            return False

        print(Fore.CYAN + f"\n{'='*70}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  CTS LN₂ Immersion (~{waitminutes} min)" + Style.RESET_ALL)
        print(Fore.CYAN + f"  Monitoring level every 60 seconds..." + Style.RESET_ALL)
        print(Fore.CYAN + f"{'='*70}\n" + Style.RESET_ALL)

        t0 = time.time_ns()//1e9
        if self.cryo_create():
            parsed = self.cryo_cmd(mode=b'4')
            self.cryo_close()
        else:
            return False

        check_count = 0
        while True:
            time.sleep(60)
            check_count += 1

            if self.cryo_create():
                parsed =  self.cryo_cmd(mode=b'm')
                self.cryo_close()
                tc_level, dewar_level = self.chamber_level(parsed)
                tgap = time.time_ns()//1e9 - t0

                # Display progress with color coding
                mins_elapsed = tgap // 60
                progress_pct = min(100, (tgap / (waitminutes * 60)) * 100)

                if tc_level >= 3:
                    level_color = Fore.GREEN
                    level_status = "✓ Ready"
                elif tc_level >= 2:
                    level_color = Fore.YELLOW
                    level_status = "In Progress"
                else:
                    level_color = Fore.RED
                    level_status = "Filling"

                print(f"{Fore.CYAN}[Check {check_count}] {mins_elapsed} min elapsed | "
                      f"{level_color}Chamber Level: {tc_level} ({level_status}) | "
                      f"{Fore.CYAN}Dewar: {dewar_level}{Style.RESET_ALL}")

                if (tc_level ==3) or (tc_level ==4):
                    print(Fore.GREEN + "\n✓ LN₂ in chamber reached Level 3 - Ready for cold test!" + Style.RESET_ALL)
                    return True

                if tgap > waitminutes*60:
                    while True:
                        print(Fore.RED + f"\n⚠️  TIMEOUT: Over {waitminutes} minutes, LN₂ still not at Level 3!" + Style.RESET_ALL)
                        yorn = input(Fore.YELLOW + "Fixed? (y/n): " + Style.RESET_ALL)
                        if 'Y' in yorn or 'y' in yorn:
                            t0 = (time.time_ns()//1e9)
                            break
                        else:
                            yorn = input(Fore.YELLOW + "Take over manually? (y/n): " + Style.RESET_ALL)
                            if 'Y' in yorn or 'y' in yorn:
                                self.manual_flg = True
                                return False

    def cts_status(self):
        if self.manual_flg:
            return -1, -1

        if self.cryo_create():
            parsed = self.cryo_cmd(mode = b'm')
            self.cryo_close()
            tc_level, dewar_level = self.chamber_level(parsed)
            return tc_level, dewar_level 
        else:
            return -1, -1


if __name__=="__main__":
    cryo=cryobox()
    t0 =  time.time_ns()//1e9
    cryo.cts_init_setup() #use only once before checking liquid nitrogen level..
##    print (cryo.manual_flg)
#    print ("Time:", time.time_ns()//1e9 - t0)
#
#    t0 =  time.time_ns()//1e9
#    tc_level, dewar_level = cryo.cts_status() #use it to check liquid nitorgen level
#    print (tc_level, dewar_level)
#    print ("Time:", time.time_ns()//1e9 - t0)
#
#    t0 =  time.time_ns()//1e9
#    cryo.cryo_coldgas(waitminutes = 5)
#    print ("Time:", time.time_ns()//1e9 - t0)
#
#    t0 =  time.time_ns()//1e9
#    cryo.cryo_immerse(waitminutes = 30)
#    print ("Time:", time.time_ns()//1e9 - t0)

    t0 =  time.time_ns()//1e9
    cryo.cryo_warmgas(waitminutes = 60)
    print ("Time:", time.time_ns()//1e9 - t0)
# 

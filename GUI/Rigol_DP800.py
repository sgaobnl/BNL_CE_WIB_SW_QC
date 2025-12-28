import csv

import pyvisa
import time
import usb.core
import usb.util

import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

technician_csv = os.path.join(ROOT_DIR, "../init_setup.csv")
print(technician_csv)


class RigolDP800:

    csv_data = {}
    with open(technician_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                csv_data[key.strip()] = value.strip()

    def __init__(self, resource=csv_data['Rigol_PS_ID'], timeout=5000):
        self.rm = pyvisa.ResourceManager()

        self._release_usb_device()

        try:
            self.inst = self.rm.open_resource(resource)
            self.inst.timeout = timeout
            self.resource = resource

            idn = self.inst.query("*IDN?").strip()
            print(f"✅ Power Supply Connected: {idn}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise

    def _release_usb_device(self):
        try:
            # Rigol DP800的USB VID:PID
            RIGOL_VID = 0x1AB1
            RIGOL_PID = 0x0E11

            dev = usb.core.find(idVendor=RIGOL_VID, idProduct=RIGOL_PID)

            if dev is None:
                print("⚠️ Rigol device not found via USB")
                return

            for cfg in dev:
                for intf in cfg:
                    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                        try:
                            dev.detach_kernel_driver(intf.bInterfaceNumber)
                            print(f"🔓 Detached kernel driver from interface {intf.bInterfaceNumber}")
                        except usb.core.USBError as e:
                            print(f"⚠️ Could not detach kernel driver: {e}")

            try:
                dev.reset()
                time.sleep(1)
                print("🔄 USB device reset")
            except usb.core.USBError as e:
                print(f"⚠️ Could not reset device: {e}")

        except Exception as e:
            print(f"⚠️ USB release error: {e}")



    # ---------------------------------------------------------------------
    # Core control methods
    # ---------------------------------------------------------------------
    def select_channel(self, ch):
        """Select channel 1, 2, or 3."""
        self.inst.write(f"INST:NSEL {ch}")
        time.sleep(0.05)

    def set_voltage(self, ch, voltage):
        """Set voltage for channel."""
        self.select_channel(ch)
        self.inst.write(f"SOUR:VOLT {voltage}")
        time.sleep(0.05)

    def set_current(self, ch, current):
        """Set current limit for channel."""
        self.select_channel(ch)
        self.inst.write(f"SOUR:CURR {current}")
        time.sleep(0.05)

    def output_on(self, ch):
        """Turn output ON for channel."""
        self.select_channel(ch)
        self.inst.write("OUTP ON")

    def output_off(self, ch):
        """Turn output OFF for channel."""
        self.select_channel(ch)
        self.inst.write("OUTP OFF")

    def measure(self, ch):
        """Measure voltage and current from channel."""
        self.select_channel(ch)
        v = float(self.inst.query("MEAS:VOLT?"))
        i = float(self.inst.query("MEAS:CURR?"))
        return v, i

    def set_channel(self, ch, voltage, current, on=True):
        """Convenience function to set and enable a channel."""
        self.set_voltage(ch, voltage)
        self.set_current(ch, current)
        if on:
            self.output_on(ch)
        else:
            self.output_off(ch)

    def turn_off_all(self):
        """Turn off all outputs safely."""
        for ch in (1, 2, 3):
            self.output_off(ch)

    def close(self):
        """Close VISA session."""
        self.turn_off_all()
        self.inst.close()
        self.rm.close()
        print("🔌 Connection closed.")



# ---------------------------------------------------------------------
# Example usage (test block)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    psu = RigolDP800()

    print("\n⚙️ Configuring channels...")
    psu.set_channel(1, 12.0, 3.0, on=True)
    psu.set_channel(2, 12.0, 3.0, on=True)
    psu.set_channel(3, 5.0, 1.0, on=False)

    time.sleep(15)
    total_i = 0.0
    print("\n📏 Measurements:")
    for ch in (1, 2):
        v, i = psu.measure(ch)
        print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
        total_i += i
    print(f"Total current: {total_i:.3f} A")
    psu.turn_off_all()

    while True:
        total_i = 0
        for ch in (1, 2):
            v, i = psu.measure(ch)
            print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
            total_i += i  # 累加电流
        print(f"Total current: {total_i:.3f} A")
        psu.turn_off_all()
        if total_i < 0.2:
            break
        else:
            print('power off again')
            time.sleep(0.5)
    psu.close()

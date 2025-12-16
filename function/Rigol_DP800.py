import pyvisa
import time
import usb.core
import usb.util
import colorama
from colorama import init, Fore, Style


class RigolDP800:
    """
    Simple class to control Rigol DP800 series power supplies via USB or LAN.
    Works with DP832, DP831, etc.
    """

    # def __init__(self, resource="USB0::0x1AB1::0x0E11::DP8C184550857::INSTR", timeout=5000):
    #     self.rm = pyvisa.ResourceManager()
    #     self.inst = self.rm.open_resource(resource)
    #     self.inst.timeout = timeout
    #     self.resource = resource
    #
    #     idn = self.inst.query("*IDN?").strip()
    #     print(f"✅ Power Supply Connected")

    # def __init__(self, resource="USB0::0x1AB1::0x0E11::DP8C184550857::INSTR", timeout=5000):
    def __init__(self, resource="USB0::0x1AB1::0x0E11::DP8C184550811::INSTR", timeout=5000):
        self.rm = pyvisa.ResourceManager()
        print(self.rm.list_resources())

        # 先尝试释放USB设备
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

    def safe_power_off(psu, current_threshold=0.2, max_attempts=5):
        """
        Safely power off WIB with current verification.
        Attempts automatic power-off up to max_attempts times.
        If current remains high, enters manual confirmation mode with verification.

        Args:
            psu: Power supply unit object
            current_threshold: Maximum acceptable current (A) to consider power OFF successful
            max_attempts: Maximum number of automatic attempts before requiring manual intervention

        Returns:
            True if power-off successful
        """
        attempt = 0
        print(Fore.YELLOW + "\n⚡ Initiating safe power OFF sequence..." + Style.RESET_ALL)

        while True:
            # Attempt power off
            psu.turn_off_all()
            time.sleep(1)
            # Measure current on both channels
            total_i = 0
            for ch in (1, 2):
                v, i = psu.measure(ch)
                print(f"  CH{ch}: {v:.3f} V, {i:.3f} A")
                total_i += i
            print(Fore.CYAN + f"  Total current: {total_i:.3f} A" + Style.RESET_ALL)
            # Check if successful
            if total_i < current_threshold:
                print(Fore.GREEN + "✓ Power OFF successful" + Style.RESET_ALL)
                return True

            # Failed → auto retry
            attempt += 1
            print(Fore.YELLOW +
                  f"⚠️  Power off attempt {attempt}/{max_attempts} failed (current too high)" +
                  Style.RESET_ALL)

            # Max attempts reached → require manual intervention
            if attempt >= max_attempts:
                print(Fore.RED + "\n" + "=" * 70)
                print("⚠️  WARNING: AUTO POWER-OFF FAILED")
                print("    Manual power shutdown is REQUIRED!")
                print("=" * 70 + "\n" + Style.RESET_ALL)

                # Manual confirmation mode with current verification
                while True:
                    print(Fore.YELLOW + "Please manually turn OFF the WIB power supply." + Style.RESET_ALL)
                    print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' after power is OFF')
                    com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

                    if com.lower() == "confirm":
                        # Verify power is actually off
                        v1, i1 = psu.measure(1)
                        v2, i2 = psu.measure(2)
                        total_i = i1 + i2

                        if total_i < current_threshold:
                            print(Fore.GREEN +
                                  "✓ Manual power-off verified. Proceeding..." +
                                  Style.RESET_ALL)
                            return True
                        else:
                            print(Fore.RED +
                                  f"✗ Verification failed: Current still high ({total_i:.3f} A)" +
                                  Style.RESET_ALL)
                            print(Fore.YELLOW +
                                  "Please ensure power is completely OFF and try again." +
                                  Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Invalid input. Please type 'confirm'." + Style.RESET_ALL)

            print(Fore.CYAN + "Retrying auto power off...\n" + Style.RESET_ALL)

    def _release_usb_device(self):
        """释放被占用的USB设备"""
        try:
            # Rigol DP800的USB VID:PID
            RIGOL_VID = 0x1AB1
            RIGOL_PID = 0x0E11

            # 查找设备
            dev = usb.core.find(idVendor=RIGOL_VID, idProduct=RIGOL_PID)

            if dev is None:
                print("⚠️ Rigol device not found via USB")
                return

            # 如果内核驱动已激活，分离它
            for cfg in dev:
                for intf in cfg:
                    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                        try:
                            dev.detach_kernel_driver(intf.bInterfaceNumber)
                            print(f"🔓 Detached kernel driver from interface {intf.bInterfaceNumber}")
                        except usb.core.USBError as e:
                            print(f"⚠️ Could not detach kernel driver: {e}")

            # 重置设备
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
        # self.turn_off_all()
        # self.inst.close()
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
        total_i += i  # 累加电流
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

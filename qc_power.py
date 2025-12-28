"""
QC Power Management Functions
Contains power supply control and safety functions
"""

import time
import colorama
from colorama import Fore, Style

colorama.init()


def safe_power_off(psu, current_threshold=0.2, max_attempts=5):
    """
    Automatically power off WIB. Attempts up to max_attempts times.
    If current remains high, enters manual confirmation mode with current verification.
    """
    attempt = 0
    while True:
        time.sleep(1)
        # Measure current on both channels
        total_i = 0
        for ch in (1, 2):
            v, i = psu.measure(ch)
            print(f"  CH{ch}: {v:.3f} V, {i:.3f} A")
            total_i += i
        print(Fore.CYAN + f"  Total current: {total_i:.3f} A" + Style.RESET_ALL)

        # Attempt power off
        psu.turn_off_all()

        # Success
        if total_i < current_threshold:
            print(Fore.GREEN + "✓ Power OFF successful." + Style.RESET_ALL)
            return True

        # Failed → auto retry
        attempt += 1
        print(
            Fore.YELLOW + f"⚠️  Power off attempt {attempt}/{max_attempts} failed (current too high)." + Style.RESET_ALL)

        # Max attempts reached → manual intervention
        if attempt >= max_attempts:
            print(Fore.RED + "\n" + "=" * 60)
            print("⚠️  WARNING: AUTO POWER-OFF FAILED")
            print("    Manual power shutdown is REQUIRED!")
            print("=" * 60 + "\n" + Style.RESET_ALL)

            # Manual confirmation mode with verification
            while True:
                print(Fore.YELLOW + "Please manually turn OFF the WIB power supply." + Style.RESET_ALL)
                print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' after power is OFF')
                com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                if com.lower() == "confirm":
                    # Verify power is actually off
                    v1, i1 = psu.measure(1)
                    v2, i2 = psu.measure(2)
                    if (i1 + i2) < current_threshold:
                        print(Fore.GREEN + "✓ Manual power-off verified. Proceeding..." + Style.RESET_ALL)
                        return True
                    else:
                        print(
                            Fore.RED + f"✗ Verification failed: Current still high ({i1 + i2:.3f} A)" + Style.RESET_ALL)
                        print(Fore.YELLOW + "Please ensure power is completely OFF and try again." + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Invalid input. Please type 'confirm'." + Style.RESET_ALL)

        print(Fore.CYAN + "Retrying auto power off...\n" + Style.RESET_ALL)

"""
QC User Interface Functions
Contains user interaction and input validation functions
"""

import os
import colorama
from colorama import Fore, Style

colorama.init()


def confirm(prompt):
    """Simple confirmation - requires typing 'confirm' to continue"""
    while True:
        print(Fore.CYAN + prompt + Style.RESET_ALL)
        print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == "confirm":
            return True
        else:
            print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
            break


def get_email():
    """Validate and get user email with confirmation"""
    while True:
        email1 = input('Please enter your email address:\n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        email2 = input('Please enter again to confirm:\n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # Check for @ symbol
        if "@" not in email1:
            print(Fore.RED + "✗ Invalid email: missing '@' symbol!" + Style.RESET_ALL)
            continue

        # Check if they match
        if email1 != email2:
            print(Fore.RED + "✗ Email addresses do not match. Please try again." + Style.RESET_ALL)
            continue

        # Both passed
        print(Fore.GREEN + "✓ Email confirmed!" + Style.RESET_ALL)
        return email1


def get_cebox_image(version, root_dir):
    """Return image path for CE box disassembly based on VD/HD."""
    return os.path.join(
        root_dir, "GUI", "output_pngs",
        "17.png" if version == "VD" else "18.png"
    )

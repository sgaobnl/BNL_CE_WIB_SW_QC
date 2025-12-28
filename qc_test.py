"""
QC Test Process Functions
Contains FEMB QC test execution functions
"""

import time
import colorama
from colorama import Fore, Style
from qc_utils import QC_Process

colorama.init()


def FEMB_QC(input_info):
    """Execute FEMB Quality Control test sequence"""
    print(Fore.CYAN + "⏱️  Waiting 30 seconds to enable Fiber Converter..." + Style.RESET_ALL)
    time.sleep(30)
    print(Fore.CYAN + "🔌 Pinging Warm Interface Board..." + Style.RESET_ALL)
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=77, input_info=input_info)  # initial wib

    # C FEMB QC
    print(Fore.GREEN + "▶️  Starting FEMB Quality Control (estimated: <30 min)" + Style.RESET_ALL)
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=0, input_info=input_info)  # initial wib
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=1, input_info=input_info)  # initial FEMB I2C
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=2, input_info=input_info)  # assembly checkout
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=3, input_info=input_info)  # QC
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=6, input_info=input_info)  # QC
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=10, input_info=input_info)  # QC
    return 0

# bnl-dat-fw-sw
Working repository for DAT firmware and WIB SW that deals with the DAT.

### To load firmware onto FPGA (DUNE_DAT_FPGA_V2B):
1) Open DUNE_DAT_FPGA_V2B/DUNE_DAT_FPGA.qpf in Quartus Prime 17.1.
2) Click Start Compilation.
3) When compilation finishes, click Programmer.
4) Click Hardware Setup to select your JTAG blaster.
5) Click Add Files to add the .sof file if not already present
6) Check Program/Configure if not checked already, and click Start.

### To run software (dat_sw):
Copy dat_sw and paste into the WIB at /home. Run make.
#### python3 quick_checkout.py [FEMBs] [save number_to_save]
Unmodified from original repo other than 1) an increased waiting time for powerup (20 seconds) and 2) an increase in voltage setting for VFE, VCD, and VADC from 3-3.5 to 4.0. These modifications are due to the increased size and power requirements of DAT- it's a large board.
#### python3 dat_test.py
A script created by me testing basic communication and control with the DAT. It will be updated as features are added. Currently it tests:
 - Basic peek/poking of WIB
 - Prints out the contents of COLDATA (for debugging purposes, to be commented out)
 - Basic peek/poking of COLDATA
 - Basic peeking/poking of DAT FPGA
 - Reading out INA226 power monitors (for COLDATA, ColdADC, and FE)
 - Verifying that writing to COLDATA's CD_CONTROL registers changes COLDATA's CD_CONTROL output pins accordingly
 - Writing values to DACs (these values are verified with the monitoring ADCs)
 - Reading out all possible inputs to monitoring ADCs
The script is messy from previously being used to test wib_util, so I need to fix it.

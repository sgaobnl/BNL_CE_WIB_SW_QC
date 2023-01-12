# bnl-dat-fw-sw
Working repository for DAT firmware and WIB SW that deals with the DAT.

### To test firmware (DUNE_DAT_FPGA_V2B):
1) Open DUNE_DAT_FPGA_V2B/DUNE_DAT_FPGA.qpf in Quartus Prime 17.1.
2) Click Start Compilation.
3) When compilation finishes, click Programmer.
4) Click Hardware Setup to select your JTAG blaster.
5) Click Add Files to add the .sof file if not already present
6) Check Program/Configure if not checked already, and click Start.

### To test software (dat_sw):
Copy dat_sw and paste into the WIB at /home. Run the makefile.

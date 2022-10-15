# BNL_CE_WIB_SW_QC
 
# These scripts are developed for standalone WIB operation

# how to use
## 1. pull to WIB local 
## 2. “make” to compile and generate C++ library
## 3. scripts for power configuration/measurement are not ready yet, so fembs should be powered on with Penn’s SW (Jillian is working on)
## 4. python3 top_chkout_pls_fake_timing.py 0 1 2 3 save 1
###  use PLL as clock source
## 5. python3 top_chkout_pls_ptc_timing.py 0 1 2 3 save 1
## clock is from external timing system

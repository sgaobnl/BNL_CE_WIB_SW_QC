## Generated SDC file "DUNE_DAT_FPGA.out.sdc"

## Copyright (C) 2016  Intel Corporation. All rights reserved.
## Your use of Intel Corporation's design tools, logic functions 
## and other software and tools, and its AMPP partner logic 
## functions, and any output files from any of the foregoing 
## (including device programming or simulation files), and any 
## associated documentation or information are expressly subject 
## to the terms and conditions of the Intel Program License 
## Subscription Agreement, the Intel Quartus Prime License Agreement,
## the Intel MegaCore Function License Agreement, or other 
## applicable license agreement, including, without limitation, 
## that your use is for the sole purpose of programming logic 
## devices manufactured by Intel and sold by Intel or its 
## authorized distributors.  Please refer to the applicable 
## agreement for further details.


## VENDOR  "Altera"
## PROGRAM "Quartus Prime"
## VERSION "Version 16.1.0 Build 196 10/24/2016 SJ Standard Edition"

## DATE    "Thu Oct 03 11:29:36 2024"

##
## DEVICE  "EP4CGX50DF27C8"
##


#**************************************************************
# Time Information
#**************************************************************

set_time_format -unit ns -decimal_places 3



#**************************************************************
# Create Clock
#**************************************************************

create_clock -name {CLK_64MHZ_SYS_P} -period 16.000 -waveform { 0.000 8.000 } [get_ports {CLK_64MHZ_SYS_P}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1} -period 10.000 -waveform { 0.000 5.000 } [get_registers { COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1 }]
create_clock -name {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1} -period 1.000 -waveform { 0.000 0.500 } [get_registers {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}]
create_clock -name {CD1_LOCK} -period 1.000 -waveform { 0.000 0.500 } [get_ports {CD1_LOCK}]


#**************************************************************
# Create Generated Clock
#**************************************************************

create_generated_clock -name {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]} -source [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 8 -divide_by 5 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] 
create_generated_clock -name {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]} -source [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 1 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] 
create_generated_clock -name {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]} -source [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 4 -divide_by 5 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] 
create_generated_clock -name {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]} -source [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 2 -divide_by 5 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] 
create_generated_clock -name {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]} -source [get_pins {DAT_PLL2_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 1 -divide_by 5 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] 
create_generated_clock -name {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]} -source [get_pins {DAT_PLL2_inst|altpll_component|auto_generated|pll1|inclk[0]}] -duty_cycle 50/1 -multiply_by 1 -divide_by 32 -master_clock {CLK_64MHZ_SYS_P} [get_pins {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] 


#**************************************************************
# Set Clock Latency
#**************************************************************



#**************************************************************
# Set Clock Uncertainty
#**************************************************************

set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {CD1_LOCK}] -setup 0.110  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {CD1_LOCK}] -hold 0.080  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {CD1_LOCK}] -setup 0.110  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {CD1_LOCK}] -hold 0.080  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {CD1_LOCK}] -setup 0.110  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -rise_to [get_clocks {CD1_LOCK}] -hold 0.080  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {CD1_LOCK}] -setup 0.110  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -fall_to [get_clocks {CD1_LOCK}] -hold 0.080  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -setup 0.100  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -hold 0.070  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.150  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}]  0.150  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -rise_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}] -fall_to [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.060  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.090  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.060  
set_clock_uncertainty -rise_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.090  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.060  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.090  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.060  
set_clock_uncertainty -fall_from [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[1]}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.090  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:4:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:7:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:5:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:6:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:2:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:1:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:0:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.070  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.100  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -rise_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -fall_from [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}] -fall_to [get_clocks {COLDADC_RO_CNT:\gen_ro_cnt:3:ro_inst|ro_in_s1}]  0.020  
set_clock_uncertainty -rise_from [get_clocks {CD1_LOCK}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.080  
set_clock_uncertainty -rise_from [get_clocks {CD1_LOCK}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.110  
set_clock_uncertainty -rise_from [get_clocks {CD1_LOCK}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.080  
set_clock_uncertainty -rise_from [get_clocks {CD1_LOCK}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.110  
set_clock_uncertainty -fall_from [get_clocks {CD1_LOCK}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.080  
set_clock_uncertainty -fall_from [get_clocks {CD1_LOCK}] -rise_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.110  
set_clock_uncertainty -fall_from [get_clocks {CD1_LOCK}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -setup 0.080  
set_clock_uncertainty -fall_from [get_clocks {CD1_LOCK}] -fall_to [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] -hold 0.110  


#**************************************************************
# Set Input Delay
#**************************************************************



#**************************************************************
# Set Output Delay
#**************************************************************



#**************************************************************
# Set Clock Groups
#**************************************************************



#**************************************************************
# Set False Path
#**************************************************************



#**************************************************************
# Set Multicycle Path
#**************************************************************



#**************************************************************
# Set Maximum Delay
#**************************************************************



#**************************************************************
# Set Minimum Delay
#**************************************************************



#**************************************************************
# Set Input Transition
#**************************************************************


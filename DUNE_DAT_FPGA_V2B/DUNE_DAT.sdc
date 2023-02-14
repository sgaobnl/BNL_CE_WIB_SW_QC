create_clock -name "DAT_SYS_CLK" -period 16.000ns [get_ports {CLK_64MHZ_SYS_P}]


#create_clock -name {ADC_RO_OUT[0]} -period 10.000 [get_ports {ADC_RO_OUT[0]}]
#create_clock -name {ADC_RO_OUT[1]} -period 10.000 [get_ports {ADC_RO_OUT[1]}]
#create_clock -name {ADC_RO_OUT[2]} -period 10.000 [get_ports {ADC_RO_OUT[2]}]
#create_clock -name {ADC_RO_OUT[3]} -period 10.000 [get_ports {ADC_RO_OUT[3]}]
#create_clock -name {ADC_RO_OUT[4]} -period 10.000 [get_ports {ADC_RO_OUT[4]}]
#create_clock -name {ADC_RO_OUT[5]} -period 10.000 [get_ports {ADC_RO_OUT[5]}]
#create_clock -name {ADC_RO_OUT[6]} -period 10.000 [get_ports {ADC_RO_OUT[6]}]
#create_clock -name {ADC_RO_OUT[7]} -period 10.000 [get_ports {ADC_RO_OUT[7]}]


derive_pll_clocks -create_base_clocks


set_clock_groups \
    -asynchronous \
    -group [get_clocks DAT_SYS_CLK] \
    -group [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[0]}] \
    -group [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[1]}] \
    -group [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[2]}] \
	 -group [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[3]}] \
    -group [get_clocks {DAT_PLL_inst|altpll_component|auto_generated|pll1|clk[4]}] \
    -group [get_clocks {DAT_PLL2_inst|altpll_component|auto_generated|pll1|clk[0]}]

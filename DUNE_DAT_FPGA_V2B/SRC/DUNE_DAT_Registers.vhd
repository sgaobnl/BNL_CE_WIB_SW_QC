--/////////////////////////////////////////////////////////////////////
--////                              
--////  File: DUNE_DAT_Registers.VHD          
--////                                                                                                                                      
--////  Author: Jack Fried			                  
--////          jfried@bnl.gov	              
--////  Created: 02/04/2016
--////  Description:  SBND UDP, I2C  and DPM register interface
--////					
--////
--/////////////////////////////////////////////////////////////////////
--////
--//// Copyright (C) 2016 Brookhaven National Laboratory
--////
--/////////////////////////////////////////////////////////////////////

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_arith.all;
USE ieee.std_logic_unsigned.all;

--  Entity Declaration

ENTITY DUNE_DAT_Registers IS

	PORT
	(
		rst         	 : IN  STD_LOGIC;  -- state machine reset
		clk         	 : IN  STD_LOGIC;
		
		BOARD_ID			 : IN  STD_LOGIC_VECTOR(7 downto 0);
		VERSION_ID		 : IN  STD_LOGIC_VECTOR(7 downto 0);
		
		
		-----WIB interface----
		WIB_data        : IN STD_LOGIC_VECTOR(7 downto 0);	
		WIB_WR_address  : IN STD_LOGIC_VECTOR(7 downto 0); 
		WIB_RD_address  : IN STD_LOGIC_VECTOR(7 downto 0); 
		WIB_WR    	 	 : IN STD_LOGIC;	
		WIB_data_out	 : OUT  STD_LOGIC_VECTOR(7 downto 0);			

		----------registers-----------------------------
		reg0_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg1_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg2_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg3_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg4_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg5_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg6_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg7_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg8_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg9_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg10_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg11_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg12_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg13_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg14_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg15_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg16_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg17_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg18_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg19_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg20_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg21_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg22_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg23_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg24_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg25_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg26_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg27_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg28_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg29_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg30_i		: IN  STD_LOGIC_VECTOR(7 downto 0);			
		reg31_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg32_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg33_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg34_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg35_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg36_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg37_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg38_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg39_i		: IN  STD_LOGIC_VECTOR(7 downto 0);			
		reg40_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg41_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg42_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg43_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg44_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg45_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg46_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg47_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg48_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg49_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg50_i		: IN  STD_LOGIC_VECTOR(7 downto 0);			
		reg51_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg52_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg53_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg54_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg55_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg56_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg57_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg58_i		: IN  STD_LOGIC_VECTOR(7 downto 0);		
		reg59_i		: IN  STD_LOGIC_VECTOR(7 downto 0);	
		reg60_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg61_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg62_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg63_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg64_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg65_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg66_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg67_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg68_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg69_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg70_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg71_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg72_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg73_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg74_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg75_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg76_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg77_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg78_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg79_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg80_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg81_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg82_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg83_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg84_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg85_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg86_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg87_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg88_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg89_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg90_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg91_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg92_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg93_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg94_i		: IN  STD_LOGIC_VECTOR(7 downto 0);
		reg95_i		: IN  STD_LOGIC_VECTOR(7 downto 0);

		
		reg0_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg1_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg2_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg3_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg4_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg5_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg6_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg7_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg8_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg9_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg10_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg11_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg12_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg13_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg14_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg15_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg16_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg17_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg18_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg19_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg20_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg21_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg22_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg23_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg24_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg25_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg26_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg27_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg28_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg29_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg30_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg31_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg32_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg33_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg34_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg35_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg36_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg37_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg38_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg39_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg40_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg41_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg42_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg43_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg44_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg45_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg46_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg47_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg48_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg49_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg50_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg51_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg52_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg53_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg54_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg55_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg56_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg57_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg58_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg59_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg60_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg61_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg62_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg63_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg64_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg65_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg66_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg67_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg68_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg69_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg70_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg71_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg72_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg73_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg74_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg75_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg76_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg77_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg78_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg79_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg80_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg81_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg82_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);		
		reg83_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg84_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg85_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg86_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg87_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);	
		reg88_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg89_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg90_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg91_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg92_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg93_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg94_o		: OUT  STD_LOGIC_VECTOR(7 downto 0);
		reg95_o		: OUT  STD_LOGIC_VECTOR(7 downto 0)


		
	);
	
END DUNE_DAT_Registers;


ARCHITECTURE Behavior OF DUNE_DAT_Registers IS



component version_reg
	PORT
	(
        data_out    : OUT STD_LOGIC_VECTOR(11 downto 0);
        Date_s      : OUT STD_LOGIC_VECTOR(31 downto 0);   
        Time_s      : OUT STD_LOGIC_VECTOR(23 downto 0)   
	);
end component;



SIGNAL	SCRATCH_PAD			: STD_LOGIC_VECTOR (7 DOWNTO 0);
SIGNAL	DP_A_WR_DLY			: STD_LOGIC;
signal	VERSION	 			: STD_LOGIC_VECTOR (15 DOWNTO 0);  							 
signal	DATE_O	 			: STD_LOGIC_VECTOR (31 DOWNTO 0);  	 				 
signal	TIME_O				: STD_LOGIC_VECTOR (23 DOWNTO 0);  	 

begin





 version_reg_inst : version_reg
	PORT MAP
	(
        data_out    => VERSION(11 downto 0),
        Date_s      => DATE_O,
        Time_s      => TIME_O(23 downto 0)
	);
	
VERSION(15 downto 12)	<=  x"0";



	----register read back------
	WIB_data_out  <=		 reg0_i 	when (WIB_RD_address = x"00")	else
								 reg1_i 	when (WIB_RD_address = x"01")	else
								 reg2_i 	when (WIB_RD_address = x"02")	else
								 reg3_i 	when (WIB_RD_address = x"03")	else
								 reg4_i 	when (WIB_RD_address = x"04")	else
								 reg5_i 	when (WIB_RD_address = x"05")	else
								 reg6_i 	when (WIB_RD_address = x"06")	else
								 reg7_i 	when (WIB_RD_address = x"07")	else
								 reg8_i 	when (WIB_RD_address = x"08")	else
								 reg9_i 	when (WIB_RD_address = x"09")	else
								 reg10_i	when (WIB_RD_address = x"0a")	else
								 reg11_i	when (WIB_RD_address = x"0b")	else
								 reg12_i	when (WIB_RD_address = x"0c")	else
								 reg13_i	when (WIB_RD_address = x"0d")	else
								 reg14_i	when (WIB_RD_address = x"0e")	else
								 reg15_i	when (WIB_RD_address = x"0f")	else
								 reg16_i	when (WIB_RD_address = x"10")	else
								 reg17_i	when (WIB_RD_address = x"11")	else
								 reg18_i	when (WIB_RD_address = x"12")	else
								 reg19_i	when (WIB_RD_address = x"13")	else
								 reg20_i	when (WIB_RD_address = x"14")	else
								 reg21_i	when (WIB_RD_address = x"15")	else
								 reg22_i	when (WIB_RD_address = x"16")	else
								 reg23_i	when (WIB_RD_address = x"17")	else
								 reg24_i	when (WIB_RD_address = x"18")	else
								 reg25_i	when (WIB_RD_address = x"19")	else
								 reg26_i	when (WIB_RD_address = x"1A")	else
								 reg27_i	when (WIB_RD_address = x"1B")	else
								 reg28_i	when (WIB_RD_address = x"1C")	else
								 reg29_i	when (WIB_RD_address = x"1D")	else
								 reg30_i	when (WIB_RD_address = x"1E")	else	
								 reg31_i	when (WIB_RD_address = x"1F")	else
								 reg32_i	when (WIB_RD_address = x"20")	else
								 reg33_i	when (WIB_RD_address = x"21")	else
								 reg34_i	when (WIB_RD_address = x"22")	else
								 reg35_i	when (WIB_RD_address = x"23")	else
								 reg36_i	when (WIB_RD_address = x"24")	else
								 reg37_i	when (WIB_RD_address = x"25")	else
								 reg38_i	when (WIB_RD_address = x"26")	else
								 reg39_i	when (WIB_RD_address = x"27")	else		
								 reg40_i	when (WIB_RD_address = x"28")	else	
								 reg41_i	when (WIB_RD_address = x"29")	else
								 reg42_i	when (WIB_RD_address = x"2A")	else
								 reg43_i	when (WIB_RD_address = x"2B")	else
								 reg44_i	when (WIB_RD_address = x"2C")	else
								 reg45_i	when (WIB_RD_address = x"2D")	else
								 reg46_i	when (WIB_RD_address = x"2E")	else
								 reg47_i	when (WIB_RD_address = x"2F")	else
								 reg48_i	when (WIB_RD_address = x"30")	else
								 reg49_i	when (WIB_RD_address = x"31")	else
								 reg50_i	when (WIB_RD_address = x"32")	else	
								 reg51_i	when (WIB_RD_address = x"33")	else
								 reg52_i	when (WIB_RD_address = x"34")	else
								 reg53_i	when (WIB_RD_address = x"35")	else
								 reg54_i	when (WIB_RD_address = x"36")	else
								 reg55_i	when (WIB_RD_address = x"37")	else
								 reg56_i	when (WIB_RD_address = x"38")	else
								 reg57_i	when (WIB_RD_address = x"39")	else
								 reg58_i	when (WIB_RD_address = x"3A")	else
								 reg59_i	when (WIB_RD_address = x"3B")	else		
								 reg60_i	when (WIB_RD_address = x"3C")	else
								 reg61_i	when (WIB_RD_address = x"3D")	else
								 reg62_i	when (WIB_RD_address = x"3E")	else
								 reg63_i	when (WIB_RD_address = x"3F")	else
								 reg64_i	when (WIB_RD_address = x"40")	else
								 reg65_i	when (WIB_RD_address = x"41")	else
								 reg66_i	when (WIB_RD_address = x"42")	else
								 reg67_i	when (WIB_RD_address = x"43")	else
								 reg68_i	when (WIB_RD_address = x"44")	else
								 reg69_i	when (WIB_RD_address = x"45")	else
								 reg70_i	when (WIB_RD_address = x"46")	else
								 reg71_i	when (WIB_RD_address = x"47")	else
								 reg72_i	when (WIB_RD_address = x"48")	else
								 reg73_i	when (WIB_RD_address = x"49")	else
								 reg74_i	when (WIB_RD_address = x"4A")	else
								 reg75_i	when (WIB_RD_address = x"4B")	else
								 reg76_i	when (WIB_RD_address = x"4C")	else
								 reg77_i	when (WIB_RD_address = x"4D")	else
								 reg78_i	when (WIB_RD_address = x"4E")	else
								 reg79_i	when (WIB_RD_address = x"4F")	else		
								 reg80_i	when (WIB_RD_address = x"50")	else
								 reg81_i	when (WIB_RD_address = x"51")	else
								 reg82_i	when (WIB_RD_address = x"52")	else
								 reg83_i	when (WIB_RD_address = x"53")	else
								 reg84_i	when (WIB_RD_address = x"54")	else
								 reg85_i	when (WIB_RD_address = x"55")	else
								 reg86_i	when (WIB_RD_address = x"56")	else
								 reg87_i	when (WIB_RD_address = x"57")	else
								 reg88_i	when (WIB_RD_address = x"58")	else
								 reg89_i	when (WIB_RD_address = x"59")	else		
								 reg90_i	when (WIB_RD_address = x"5A")	else
								 reg91_i	when (WIB_RD_address = x"5B")	else
								 reg92_i	when (WIB_RD_address = x"5C")	else
								 reg93_i	when (WIB_RD_address = x"5D")	else
								 reg94_i	when (WIB_RD_address = x"5E")	else
								 reg95_i	when (WIB_RD_address = x"5F")	else

								 BOARD_ID						when (WIB_RD_address = x"f3")	else
								 VERSION_ID						when (WIB_RD_address = x"f4")	else
								 VERSION(7 downto 0)			when (WIB_RD_address = x"f5") else	
		 						 VERSION(15 downto 8)		when (WIB_RD_address = x"f6") else	
								 DATE_O(7 downto 0)			when (WIB_RD_address = x"f7") else	
								 DATE_O(15 downto 8)			when (WIB_RD_address = x"f8") else	
								 DATE_O(23 downto 16)		when (WIB_RD_address = x"f9") else	
								 DATE_O(31 downto 24)		when (WIB_RD_address = x"fa") else	
								 TIME_O(7 downto 0)			when (WIB_RD_address = x"fb") else	
								 TIME_O(15 downto 8)			when (WIB_RD_address = x"fc") else	
								 TIME_O(23 downto 16)		when (WIB_RD_address = x"fd") else	
								 SCRATCH_PAD					when (WIB_RD_address = x"fe")	else
								 X"00";		 
		 					 
  process(clk,rst) 
  begin
		if (rst = '1') then
			reg0_o		<= x"00";	
			reg1_o		<= x"00";
			reg2_o		<= x"00";
			reg3_o		<= x"00";
			reg4_o		<= x"00";
			reg5_o		<= x"00";	
			reg6_o		<= x"00";
			reg7_o		<= X"00";	
			reg8_o		<= X"00";		
			reg9_o		<= X"00";	
			reg10_o		<= X"00";
			reg11_o		<= X"00";	
			reg12_o		<= X"00";		
			reg13_o		<= X"00";
			reg14_o		<= X"00";	
			reg15_o		<= X"00";
			reg16_o		<= X"00";	
			reg17_o		<= X"00";	
			reg18_o		<= X"00";		
			reg19_o		<= X"00";	
			reg20_o		<= X"00";	
			reg21_o		<= X"00";	
			reg22_o		<= X"00";		
			reg23_o		<= X"00";
			reg24_o		<= X"00";	
			reg25_o		<= X"00";
			reg26_o		<= X"00";	
			reg27_o		<= X"00";	
			reg28_o		<= X"00";		
			reg29_o		<= X"00";	
			reg30_o		<= X"00";	
			reg31_o		<= X"00";	
			reg32_o		<= X"00";		
			reg33_o		<= X"00";
			reg34_o		<= X"ff";	
			reg35_o		<= X"ff";
			reg36_o		<= X"00";	
			reg37_o		<= X"00";	
			reg38_o		<= X"00";		
			reg39_o		<= X"00";
			reg40_o		<= X"00";
			reg41_o		<= X"00";	
			reg42_o		<= X"00";		
			reg43_o		<= X"00";
			reg44_o		<= X"00";	
			reg45_o		<= X"00";
			reg46_o		<= X"00";	
			reg47_o		<= X"00";	
			reg48_o		<= X"00";		
			reg49_o		<= X"00";	
			reg40_o		<= X"00";	
			reg51_o		<= X"00";	
			reg52_o		<= X"00";		
			reg53_o		<= X"00";
			reg54_o		<= X"00";	
			reg55_o		<= X"00";
			reg56_o		<= X"00";	
			reg57_o		<= X"00";	
			reg58_o		<= X"00";		
			reg59_o		<= X"00";
			reg60_o		<= X"00";
			reg61_o		<= X"00";
			reg62_o		<= X"00";		
			reg63_o		<= X"00";
			reg64_o		<= X"01";	
			reg65_o		<= X"01";
			reg66_o		<= X"00";	
			reg67_o		<= X"00";	
			reg68_o		<= X"00";		
			reg69_o		<= X"00";
			reg70_o		<= X"00";
			reg71_o		<= X"00";
			reg72_o		<= X"01";		
			reg73_o		<= X"01";
			reg74_o		<= X"01";	
			reg75_o		<= X"01";
			reg76_o		<= X"01";	
			reg77_o		<= X"01";	
			reg78_o		<= X"01";		
			reg79_o		<= X"01";
			reg80_o		<= X"01";
			reg81_o		<= X"01";
			reg82_o		<= X"01";		
			reg83_o		<= X"01";
			reg84_o		<= X"01";	
			reg85_o		<= X"01";
			reg86_o		<= X"01";	
			reg87_o		<= X"01";	
			reg88_o		<= X"00";	
			reg89_o		<= X"00";
			reg90_o		<= X"00";	
			reg91_o		<= X"00";	
			reg92_o		<= X"00";	
			reg93_o		<= X"00";
			reg94_o		<= X"00";	
			reg95_o		<= X"00";	


		elsif (clk'event  AND  clk = '1') then				


			reg0_o					<= X"00";	-- AUTO CLEAR REG 	
		
			
			if (WIB_WR = '1')  then
				CASE WIB_WR_address IS
					when x"00" => 	reg0_o   <= WIB_data;
					when x"01" => 	reg1_o   <= WIB_data;	
					when x"02" => 	reg2_o   <= WIB_data;
					when x"03" => 	reg3_o   <= WIB_data;
					when x"04" => 	reg4_o   <= WIB_data;
					when x"05" => 	reg5_o   <= WIB_data;
					when x"06" => 	reg6_o   <= WIB_data;
					when x"07" => 	reg7_o   <= WIB_data;
					when x"08" => 	reg8_o   <= WIB_data;
					when x"09" => 	reg9_o   <= WIB_data;	
					when x"0A" => 	reg10_o  <= WIB_data;
					when x"0B" => 	reg11_o  <= WIB_data;
					when x"0C" => 	reg12_o  <= WIB_data;
					when x"0D" => 	reg13_o  <= WIB_data;
					when x"0E" => 	reg14_o  <= WIB_data;
					when x"0F" => 	reg15_o  <= WIB_data;
					when x"10" => 	reg16_o  <= WIB_data;
					when x"11" => 	reg17_o  <= WIB_data;
					when x"12" => 	reg18_o  <= WIB_data;
					when x"13" => 	reg19_o  <= WIB_data;
					when x"14" => 	reg20_o  <= WIB_data;
					when x"15" => 	reg21_o  <= WIB_data;
					when x"16" => 	reg22_o  <= WIB_data;
					when x"17" => 	reg23_o  <= WIB_data;
					when x"18" => 	reg24_o  <= WIB_data;
					when x"19" => 	reg25_o  <= WIB_data;	
					when x"1A" => 	reg26_o  <= WIB_data;
					when x"1B" => 	reg27_o  <= WIB_data;
					when x"1C" => 	reg28_o  <= WIB_data;
					when x"1D" => 	reg29_o  <= WIB_data;
					when x"1E" => 	reg30_o  <= WIB_data;		
					when x"1F" => 	reg31_o  <= WIB_data;	
					when x"20" => 	reg32_o  <= WIB_data;	
					when x"21" => 	reg33_o  <= WIB_data;	
					when x"22" => 	reg34_o  <= WIB_data;	
					when x"23" => 	reg35_o  <= WIB_data;		
					when x"24" => 	reg36_o  <= WIB_data;	
					when x"25" => 	reg37_o  <= WIB_data;	
					when x"26" => 	reg38_o  <= WIB_data;	
					when x"27" => 	reg39_o  <= WIB_data;
					when x"28" => 	reg40_o  <= WIB_data;	
					when x"29" => 	reg41_o  <= WIB_data;
					when x"2A" => 	reg42_o  <= WIB_data;
					when x"2B" => 	reg43_o  <= WIB_data;
					when x"2C" => 	reg44_o  <= WIB_data;
					when x"2D" => 	reg45_o  <= WIB_data;	
					when x"2E" => 	reg46_o  <= WIB_data;
					when x"2F" => 	reg47_o  <= WIB_data;
					when x"30" => 	reg48_o  <= WIB_data;
					when x"31" => 	reg49_o  <= WIB_data;
					when x"32" => 	reg50_o  <= WIB_data;		
					when x"33" => 	reg51_o  <= WIB_data;	
					when x"34" => 	reg52_o  <= WIB_data;	
					when x"35" => 	reg53_o  <= WIB_data;	
					when x"36" => 	reg54_o  <= WIB_data;	
					when x"37" => 	reg55_o  <= WIB_data;		
					when x"38" => 	reg56_o  <= WIB_data;	
					when x"39" => 	reg57_o  <= WIB_data;	
					when x"3A" => 	reg58_o  <= WIB_data;	
					when x"3B" => 	reg59_o  <= WIB_data;	
					when x"3C" => 	reg60_o  <= WIB_data;
					when x"3D" => 	reg61_o  <= WIB_data;
					when x"3E" => 	reg62_o  <= WIB_data;	
					when x"3F" => 	reg63_o  <= WIB_data;	
					when x"40" => 	reg64_o  <= WIB_data;	
					when x"41" => 	reg65_o  <= WIB_data;		
					when x"42" => 	reg66_o  <= WIB_data;	
					when x"43" => 	reg67_o  <= WIB_data;	
					when x"44" => 	reg68_o  <= WIB_data;	
					when x"45" => 	reg69_o  <= WIB_data;	
					when x"46" => 	reg70_o  <= WIB_data;
					when x"47" => 	reg71_o  <= WIB_data;
	     			when x"48" => 	reg72_o  <= WIB_data;	
					when x"49" => 	reg73_o  <= WIB_data;	
					when x"4A" => 	reg74_o  <= WIB_data;	
					when x"4B" => 	reg75_o  <= WIB_data;		
					when x"4C" => 	reg76_o  <= WIB_data;	
					when x"4D" => 	reg77_o  <= WIB_data;	
					when x"4E" => 	reg78_o  <= WIB_data;	
					when x"4F" => 	reg79_o  <= WIB_data;	
					when x"50" => 	reg80_o  <= WIB_data;
					when x"51" => 	reg81_o  <= WIB_data;
					when x"52" => 	reg82_o  <= WIB_data;	
					when x"53" => 	reg83_o  <= WIB_data;	
					when x"54" => 	reg84_o  <= WIB_data;	
					when x"55" => 	reg85_o  <= WIB_data;		
					when x"56" => 	reg86_o  <= WIB_data;	
					when x"57" => 	reg87_o  <= WIB_data;	
					when x"58" => 	reg88_o  <= WIB_data;	
					when x"59" => 	reg89_o  <= WIB_data;	
					when x"5A" => 	reg90_o  <= WIB_data;	
					when x"5B" => 	reg91_o  <= WIB_data;	
					when x"5C" => 	reg92_o  <= WIB_data;	
					when x"5D" => 	reg93_o  <= WIB_data;	
					when x"5E" => 	reg94_o  <= WIB_data;	
					when x"5F" => 	reg95_o  <= WIB_data;	


					when x"FE" =>	SCRATCH_PAD	<= WIB_data;					
					WHEN OTHERS =>  
				end case;  
			 end if;

	end if;
end process;

END behavior;

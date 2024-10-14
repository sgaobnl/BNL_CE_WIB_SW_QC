--/////////////////////////////////////////////////////////////////////
--////                              
--////  File: DUNE_DAT_FPGA.VHD            
--////                                                                                                                                      
--////  Author: Jack Fried			                  
--////          jfried@bnl.gov	              
--////  Created:  04/08/2022
--////  Modified: 02/08/2022
--//// 
--////  Description:  TOP LEVEL DUNE DAT tester
--////					  preliminary -- CODE
--////
--/////////////////////////////////////////////////////////////////////
--////
--//// Copyright (C) 2022 Brookhaven National Laboratory
--////
--/////////////////////////////////////////////////////////////////////

library ieee;
use ieee.std_logic_1164.all;
USE ieee.std_logic_arith.all;
USE ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

entity DUNE_DAT_FPGA is
	port 
	(
	
		--#DAT_FPGA_CLK
		--SBND_CLK_P       
		--CLK_100MHz_OSC_P
		--CLK_DAQ_P		: IN STD_LOGIC;
		--CLK_125MHz_OSC_P
		--#set_location_assignment PIN_AA23 -to c125_LP_P
		--#set_location_assignment PIN_K10 -to c125_LP_P
		--#set_location_assignment PIN_W26 -to CLK_LP_P
		--#set_location_assignment PIN_T15 -to CLK_LP_P

		
	--CLOCKS	
		CLK_64MHZ_SYS_P 					: IN STD_LOGIC;	
		CD1_CLK_64MHZ_SYS_P 				: OUT STD_LOGIC;	
		CD2_CLK_64MHZ_SYS_P 				: OUT STD_LOGIC;

	--POWER MONITORING - INA226
		--COLDATA
		CD1_FPGA_CD_INA_SDA 				: INOUT STD_LOGIC;
		CD1_FPGA_CD_INA_SCL 				: OUT STD_LOGIC;	
		CD2_FPGA_CD_INA_SDA 				: INOUT STD_LOGIC;
		CD2_FPGA_CD_INA_SCL 				: OUT STD_LOGIC;
		--ASIC work.I2c_master
		
		FE_INA_SDA							: INOUT STD_LOGIC_VECTOR(7 downto 0);
		FE_INA_SCL 							: OUT STD_LOGIC_VECTOR(7 downto 0);
	
	--COLDATA COMMUNICATION
		CD1_CMOS_MODE 						: OUT STD_LOGIC;
		CD1_PAD_RESET 						: OUT STD_LOGIC;
		CD1_CHIP_ID 						: OUT STD_LOGIC;
		CD2_CMOS_MODE 						: OUT STD_LOGIC;
		CD2_PAD_RESET 						: OUT STD_LOGIC;
		CD2_CHIP_ID 						: OUT STD_LOGIC;
		
		--FC PASS-THRU 
		FASTCOMMAND_IN_P 					: IN STD_LOGIC;	
		CD1_FASTCOMMAND_IN_P 				: OUT STD_LOGIC;
		CD2_FASTCOMMAND_IN_P 				: OUT STD_LOGIC;
	
		--I2CSLAVE		
		I2C_LVDS_SCL_P 						: IN STD_LOGIC;		
		I2C_LVDS_SDA_W2C_P 					: IN STD_LOGIC;
		I2C_LVDS_SDA_C2W_P 					: OUT STD_LOGIC;
		CD1_I2C_LVDS_SDA_C2W_P 				: IN STD_LOGIC;	
		CD2_I2C_LVDS_SDA_C2W_P 				: IN STD_LOGIC;
		CD1_I2C_LVDS_SDA_W2C_P 				: OUT STD_LOGIC;		
		CD2_I2C_LVDS_SDA_W2C_P 				: OUT STD_LOGIC;	
		CD1_I2C_LVDS_SCL_P 					: OUT STD_LOGIC;
		CD2_I2C_LVDS_SCL_P 					: OUT STD_LOGIC;
				
	--COLDATA CONTROL & MONITORING
		CD1_CONTROL						 	: IN STD_LOGIC_VECTOR(4 downto 0);
		CD2_CONTROL							: IN STD_LOGIC_VECTOR(4 downto 0);	
		
		CD1_EFUSE_DIN  					   : OUT STD_LOGIC;--rev.1  
		CD1_EFUSE_CSB  					   : OUT STD_LOGIC;--rev.1
		CD1_EFUSE_SCLK 					   : OUT STD_LOGIC;--rev.1 
		CD1_EFUSE_VDDQ 					   : OUT STD_LOGIC;--rev.1 
		CD1_EFUSE_DOUT 					   : IN STD_LOGIC; --rev.1 
		CD1_EFUSE_PGM  					   : OUT STD_LOGIC;--rev.1

		CD2_EFUSE_DIN  					   : OUT STD_LOGIC;--rev.1  
		CD2_EFUSE_CSB  					   : OUT STD_LOGIC;--rev.1
		CD2_EFUSE_SCLK 					   : OUT STD_LOGIC;--rev.1 
		CD2_EFUSE_VDDQ 					   : OUT STD_LOGIC;--rev.1 
		CD2_EFUSE_DOUT 					   : IN STD_LOGIC; --rev.1 
		CD2_EFUSE_PGM  					   : OUT STD_LOGIC;--rev.1

		CD1_AMON_CSA 						: OUT STD_LOGIC;		
		CD1_AMON_CSB 						: OUT STD_LOGIC;
		CD1_AMON_CSC 						: OUT STD_LOGIC;
		CD1_AMON_INH 						: OUT STD_LOGIC;		
		
		CD2_AMON_CSA 						: OUT STD_LOGIC;	
		CD2_AMON_CSB 						: OUT STD_LOGIC;
		CD2_AMON_CSC 						: OUT STD_LOGIC;
		CD2_AMON_INH 						: OUT STD_LOGIC;
		
		CD1_LOCK							: IN STD_LOGIC;--rev.1
		CD2_LOCK							: IN STD_LOGIC;--rev.1		
		
		--work.ADC_LTC2314
		CD1_MonADC_CS 						: OUT STD_LOGIC;
		CD1_MonADC_SCK 						: OUT STD_LOGIC;
		CD1_MonADC_SDO 						: IN STD_LOGIC;
		
		CD2_MonADC_CS 						: OUT STD_LOGIC;
		CD2_MonADC_SCK 						: OUT STD_LOGIC;
		CD2_MonADC_SDO 						: IN STD_LOGIC;

	--FE ASIC CONTROL & CALIBRATION
		FE_IN_TST_SEL 						: OUT STD_LOGIC_VECTOR(15 downto 0); 
		FE_CALI_CS 							: OUT STD_LOGIC_VECTOR(7 downto 0);
		
		FE_INS_PLS_CS 						: OUT STD_LOGIC_VECTOR(7 downto 0);		

		FE_TEST_INH_ARR					: OUT STD_LOGIC_VECTOR(7 downto 0);		
		FE_TEST_CSA							: OUT STD_LOGIC; 		
		FE_TEST_CSB							: OUT STD_LOGIC; 
		FE_TEST_CSC							: OUT STD_LOGIC; 

		FE_CMN_CSA							: OUT STD_LOGIC; 		
		FE_CMN_CSB							: OUT STD_LOGIC; 
		FE_CMN_CSC							: OUT STD_LOGIC; 
		FE_CMN_INH							: OUT STD_LOGIC; 
		
		EXT_PULSE_CNTL						: OUT STD_LOGIC; 
		
		--work.ADC_LTC2314
		FE_MonADC_CS						: OUT STD_LOGIC; 
		FE_MonADC_SCK						: OUT STD_LOGIC; 
		FE_MonADC_SDO 						: IN STD_LOGIC_VECTOR(7 downto 0);
		
		--AD5683R
		DAC_TP_SYNC							: OUT STD_LOGIC; 
		DAC_TP_SCK							: OUT STD_LOGIC; 
		DAC_TP_DIN							: OUT STD_LOGIC;
		
		
		FE_DAC_TP_SCK						: OUT STD_LOGIC; 
		FE_DAC_TP_SYNC						: OUT STD_LOGIC; 	
		FE_DAC_TP_DIN 						: OUT STD_LOGIC_VECTOR(7 downto 0);		

	--ADC ASIC 
		ADC_POR_NAND 						: OUT STD_LOGIC_VECTOR(7 downto 0);
		
		
		I2C_CD1_ADD_VDD 					: OUT STD_LOGIC; --I2C_ADD0
		I2C_CD1_ADD_GND 					: OUT STD_LOGIC; --I2C_ADD1	
		CD1_ADC_I2C_ADD2 					: OUT STD_LOGIC;
		CD1_ADC_I2C_ADD3 					: OUT STD_LOGIC;		
		
		I2C_CD2_ADD_VDD 					: OUT STD_LOGIC; --I2C_ADD0
		I2C_CD2_ADD_GND 					: OUT STD_LOGIC; --I2C_ADD1
		CD2_ADC_I2C_ADD2 					: OUT STD_LOGIC;
		CD2_ADC_I2C_ADD3 					: OUT STD_LOGIC;
		
		--WORK.COLDADC_RO_CNT 
		ADC_RO_OUT							: IN STD_LOGIC_VECTOR(7 downto 0);
 		
		ADC_CHIP_ACTIVE						: OUT STD_LOGIC_VECTOR(7 downto 0); 		
		
		--CALIBRATION & MONITORING
		--work.ADC_LTC2314
		ADC_TST_SEL 						: OUT STD_LOGIC_VECTOR(7 downto 0);
		
		ADC_SRC_CS_P0					   : OUT STD_LOGIC;
		ADC_SRC_CS_P1					   : OUT STD_LOGIC;
		ADC_SRC_CS_P2					   : OUT STD_LOGIC;
		ADC_SRC_CS_P3					   : OUT STD_LOGIC;
		ADC_SRC_CS_P4					   : OUT STD_LOGIC; --rev.1
		ADC_SRC_CS_P5					   : OUT STD_LOGIC; --rev.1 	 
		ADC_SRC_CS_P6					   : OUT STD_LOGIC;		
		ADC_SRC_CS_P7					   : OUT STD_LOGIC;		
		
		ADC_SRC_CS_P8					   : OUT STD_LOGIC;
		ADC_SRC_CS_P9					   : OUT STD_LOGIC;
		ADC_SRC_CS_PA					   : OUT STD_LOGIC;
		ADC_SRC_CS_PB					   : OUT STD_LOGIC;
		ADC_SRC_CS_PC					   : OUT STD_LOGIC;
		ADC_SRC_CS_PD					   : OUT STD_LOGIC;		
		ADC_SRC_CS_PE					   : OUT STD_LOGIC;		
		ADC_SRC_CS_PF					   : OUT STD_LOGIC;				
		
		ADC_MonADC_CS						: OUT STD_LOGIC; 		
		ADC_MonADC_SCK						: OUT STD_LOGIC; 
		ADC_MonADC_SDO 					: IN STD_LOGIC_VECTOR(7 downto 0);		

		ADC_TEST_INH 						: OUT STD_LOGIC_VECTOR(7 downto 0);		
		
		ADC_TEST_IN_SEL					: OUT STD_LOGIC;

		ADC_TEST_CSA						: OUT STD_LOGIC; 
		ADC_TEST_CSB						: OUT STD_LOGIC; 
		ADC_TEST_CSC						: OUT STD_LOGIC; 

		DAC_ADC_N_SYNC						: OUT STD_LOGIC; 
		DAC_ADC_N_SCK						: OUT STD_LOGIC; 
		DAC_ADC_N_DIN						: OUT STD_LOGIC; 
		DAC_ADC_P_SYNC						: OUT STD_LOGIC; 
		DAC_ADC_P_SCK						: OUT STD_LOGIC; 
		DAC_ADC_P_DIN						: OUT STD_LOGIC; 

		ADC_P_TST_CSA						: OUT STD_LOGIC; 
		ADC_P_TST_CSB						: OUT STD_LOGIC; 
		ADC_P_TST_CSC						: OUT STD_LOGIC; 
		ADC_P_TST_AMON_INH				: OUT STD_LOGIC; 
		ADC_N_TST_CSA						: OUT STD_LOGIC; 
		ADC_N_TST_CSB						: OUT STD_LOGIC; 
		ADC_N_TST_CSC						: OUT STD_LOGIC; 
		ADC_N_TST_AMON_INH				: OUT STD_LOGIC; 
		
		


	--MISC
	
		MISC_U1_IO							: out STD_LOGIC_VECTOR(5 downto 0)


	);

end DUNE_DAT_FPGA;


architecture DUNE_DAT_FPGA_arch of DUNE_DAT_FPGA is


component DAT_PLL
	PORT
	(
		inclk0		: IN STD_LOGIC  := '0';
		c0		: OUT STD_LOGIC ;
		c1		: OUT STD_LOGIC ;
		c2		: OUT STD_LOGIC ;
		c3		: OUT STD_LOGIC ;
		locked		: OUT STD_LOGIC 
	);
end component;


component DAT_PLL2
	PORT
	(
		inclk0		: IN STD_LOGIC  := '0';
		c0				: OUT STD_LOGIC; 
		c1				: OUT STD_LOGIC; 
		c2				: OUT STD_LOGIC 
	);
end component;



SIGNAL	CLK_125MHz		:  STD_LOGIC;
SIGNAL	CLK_100MHz		:  STD_LOGIC;
SIGNAL	CLK_62_5MHz		:  STD_LOGIC;
SIGNAL	CLK_50MHz 		:  STD_LOGIC;
SIGNAL	CLK_25MHz 		:  STD_LOGIC;
SIGNAL	CLK_10MHz 		:  STD_LOGIC;
SIGNAL	CLK_12_5MHz   	:  STD_LOGIC;
SIGNAL	CLK_1M953125Hz   	:  STD_LOGIC;


--SIGNAL	SYS_RESET		:  STD_LOGIC;
SIGNAL	reset 			:  STD_LOGIC;
SIGNAL	start				:  STD_LOGIC;

SIGNAL	WIB_SCL_OUT			: STD_LOGIC;	
SIGNAL	WIB_ADDRESS			: STD_LOGIC_VECTOR(7 downto 0);	
SIGNAL	WIB_DATA_OUT		: STD_LOGIC_VECTOR(7 downto 0);	
SIGNAL	WIB_DATA_IN			: STD_LOGIC_VECTOR(7 downto 0);	
SIGNAL	WIB_WR				: STD_LOGIC;	
SIGNAL	WIB_RD				: STD_LOGIC;	
SIGNAL	WIB_READ_DONE 		: STD_LOGIC;	

SIGNAL	SOCKET_RDOUT_SEL		: STD_LOGIC_VECTOR(2 downto 0);


SIGNAL	I2C_DEV_ADDR			: STD_LOGIC_VECTOR(6 downto 0);
SIGNAL	I2C_NUM_BYTES			: STD_LOGIC_VECTOR(3 downto 0);
SIGNAL	I2C_ADDRESS				: STD_LOGIC_VECTOR(7 downto 0);
SIGNAL	I2C_DIN					: STD_LOGIC_VECTOR(15 downto 0);


SIGNAL	I2C_WR_STRB_S1		   : STD_LOGIC;
SIGNAL	I2C_RD_STRB_S1		   : STD_LOGIC;
SIGNAL	I2C_DOUT_S1				: STD_LOGIC_VECTOR(31 downto 0);

SIGNAL	I2C_WR_STRB_S2		   : STD_LOGIC;
SIGNAL	I2C_RD_STRB_S2		   : STD_LOGIC;
SIGNAL	I2C_DOUT_S2				: STD_LOGIC_VECTOR(31 downto 0);

SIGNAL	I2C_WR_STRB_FE			: STD_LOGIC;
SIGNAL	I2C_RD_STRB_FE			: STD_LOGIC;
SIGNAL	I2C_DOUT_FE				: STD_LOGIC_VECTOR(31 downto 0);

type DOUT_array is array (7 downto 0) of STD_LOGIC_VECTOR(31 downto 0);
SIGNAL	I2C_DOUT_FE_arr		: DOUT_array;
SIGNAL	I2C_WR_STRB_FE_arr	: STD_LOGIC_VECTOR(7 downto 0);
SIGNAL	I2C_RD_STRB_FE_arr	: STD_LOGIC_VECTOR(7 downto 0);

type 	MonADC_data is array (7 downto 0) of STD_LOGIC_VECTOR(11 downto 0);

SIGNAL	cots_adc_start			: STD_LOGIC;

SIGNAL	CD1_MonADC_data		: STD_LOGIC_VECTOR(11 downto 0);
SIGNAL	CD1_MonADC_busy		: STD_LOGIC;
SIGNAL	CD2_MonADC_data		: STD_LOGIC_VECTOR(11 downto 0);
SIGNAL	CD2_MonADC_busy		: STD_LOGIC;

signal 	ADC_MonADC_busy 	 	: STD_LOGIC;
signal 	ADC_MonADC_data  		: STD_LOGIC_VECTOR(11 downto 0);

signal 	ADC_MonADC_busy_arr	: STD_LOGIC_VECTOR(7 downto 0);
signal	ADC_MonADC_data_arr	: MonADC_data;

signal 	FE_MonADC_busy 	 	: STD_LOGIC;
signal 	FE_MonADC_data  		: STD_LOGIC_VECTOR(11 downto 0);

signal 	FE_MonADC_busy_arr 	 	: std_logic_vector(7 downto 0);
signal 	FE_MonADC_data_arr  		: MonADC_data;

type 		DAC_data is array(7 downto 0) of std_logic_vector(15 downto 0);

signal 	FE_DAC_TP_set				: std_logic_vector(7 downto 0);

signal	FE_DAC_TP_data			: std_logic_vector(15 downto 0);
signal	FE_DAC_TP_data_arr	: DAC_data;
--signal	FE_DAC_TP_SYNC_arr	: std_logic_vector(7 downto 0);

signal 	FE_DAC_TP_CMD			: std_logic_vector(3 downto 0);
signal 	DAC_ADC_P_CMD			: std_logic_vector(3 downto 0);
signal 	DAC_ADC_N_CMD			: std_logic_vector(3 downto 0);
signal 	DAC_TP_CMD				: std_logic_vector(3 downto 0);

--signal	DAC_other_set			: std_logic_vector(2 downto 0);
signal	DAC_TP_set				: std_logic;
signal	DAC_ADC_N_set			: std_logic;
signal	DAC_ADC_P_set			: std_logic;


signal	DAC_ADC_P_data			: std_logic_vector(15 downto 0);
signal	DAC_ADC_N_data			: std_logic_vector(15 downto 0);
signal	DAC_TP_data				: std_logic_vector(15 downto 0);

type		ro_cnt_array is array(7 downto 0) of STD_LOGIC_VECTOR(31 downto 0);
signal	ro_cnt_arr				: ro_cnt_array;
signal	ro_cnt					: STD_LOGIC_VECTOR(31 downto 0);
--SIGNAL	ro_start				: STD_LOGIC;
--signal	ro_length100MHz	   : STD_LOGIC_VECTOR(31 downto 0);

--Test pulse generation
SIGNAL	FPGA_TP_EN				: STD_LOGIC;
SIGNAL	ASIC_TP_EN				: STD_LOGIC;
SIGNAL	INT_TP_EN				: STD_LOGIC;
SIGNAL	EXT_TP_EN				: STD_LOGIC;	
SIGNAL   TP_INT_GEN           : STD_LOGIC;
SIGNAL	TP_EXT_GEN				: STD_LOGIC;	
SIGNAL 	TP_SOCKET_EN			: STD_LOGIC_VECTOR(7 downto 0);

SIGNAL	Test_PULSE_WIDTH		: STD_LOGIC_VECTOR(15  downto 0);  
SIGNAL	TP_AMPL					: STD_LOGIC_VECTOR(7 downto 0);
SIGNAL	TP_DLY					: STD_LOGIC_VECTOR(7 downto 0);
SIGNAL	TP_PERIOD				: STD_LOGIC_VECTOR(15 downto 0);

SIGNAL	DAC_CNTL					: STD_LOGIC_VECTOR(12 downto 0);
SIGNAL	ASIC_DAC_CNTL			: STD_LOGIC;
SIGNAL	Test_pulse				: STD_LOGIC;
--SIGNAL	Test_pulse_buffer		: STD_LOGIC_VECTOR(7 downto 0);


SIGNAL	CD1_EFUSE_start		:  STD_LOGIC;	
SIGNAL	CD2_EFUSE_start		:  STD_LOGIC;	
SIGNAL	CD1_EFUSE_DATA		: STD_LOGIC_VECTOR(31 downto 0);
SIGNAL	CD2_EFUSE_DATA		: STD_LOGIC_VECTOR(31 downto 0);

SIGNAL 	CD1_LOCK_OUT			: STD_LOGIC;
SIGNAL 	CD2_LOCK_OUT			: STD_LOGIC;
SIGNAL 	counter1 				: INTEGER RANGE 0 TO 100;
SIGNAL 	counter2 				: INTEGER RANGE 0 TO 100;

--Registers
SIGNAL	reg0_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg1_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg2_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg3_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg4_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg5_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg6_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg7_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg8_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg9_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg10_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg11_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg12_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg13_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg14_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg15_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg16_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg17_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg18_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg19_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg20_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg21_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg22_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg23_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg24_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg25_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg26_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg27_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg28_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg29_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg30_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg31_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg32_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg33_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg34_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg35_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg36_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg37_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg38_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg39_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg40_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg41_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg42_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg43_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg44_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg45_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg46_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg47_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg48_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg49_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg50_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg51_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg52_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg53_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg54_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg55_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg56_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg57_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg58_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg59_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg60_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg61_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg62_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg63_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg64_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg65_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg66_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg67_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg68_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg69_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg70_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg71_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg72_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg73_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg74_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg75_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg76_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg77_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg78_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg79_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg80_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg81_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg82_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg83_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg84_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg85_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg86_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg87_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg88_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg89_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg90_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg91_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg92_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg93_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg94_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);
SIGNAL	reg95_p 			:  STD_LOGIC_VECTOR(7  DOWNTO 0);


SIGNAL	reg_adc				: STD_LOGIC_VECTOR(63 downto 0);
SIGNAL	reg_fe 				: STD_LOGIC_VECTOR(63 downto 0);

SIGNAL	I2C_SDA_c2w		:  STD_LOGIC;
SIGNAL	I2C_SDA_W2C		:  STD_LOGIC;
SIGNAL	I2C_SCL			:  STD_LOGIC;
SIGNAL	CD_sEL			:  STD_LOGIC;

SIGNAL	SYS_RESET				:  STD_LOGIC;
SIGNAL	REG_RESET				:  STD_LOGIC;

begin

TP_INT_GEN <= CLK_1M953125Hz;
TP_EXT_GEN <= '0';
DAC_CNTL(12)	<= '1';

CD1_CLK_64MHZ_SYS_P	<= CLK_64MHZ_SYS_P;
CD2_CLK_64MHZ_SYS_P	<= CLK_64MHZ_SYS_P;

CD1_FASTCOMMAND_IN_P	<= FASTCOMMAND_IN_P;
CD2_FASTCOMMAND_IN_P	<= FASTCOMMAND_IN_P; 					


CD1_I2C_LVDS_SCL_P	<= I2C_SCL;
CD2_I2C_LVDS_SCL_P	<= I2C_SCL;

CD1_I2C_LVDS_SDA_W2C_P 	<= I2C_SDA_W2C;
CD2_I2C_LVDS_SDA_W2C_P 	<= I2C_SDA_W2C;



---------CD master slave select and ADC address swap ---------

CD1_CMOS_MODE 			<= not CD_sEL;
CD1_CHIP_ID 			<= not CD_sEL;

CD2_CMOS_MODE 			<= CD_sEL;
CD2_CHIP_ID 			<= CD_sEL;


I2C_SDA_c2w <= CD1_I2C_LVDS_SDA_C2W_P  when CD_sEL = '0' else
					CD2_I2C_LVDS_SDA_C2W_P;
			
	
	
					
I2C_CD1_ADD_GND 		<= '0';
I2C_CD1_ADD_VDD 		<= '1';
CD1_ADC_I2C_ADD2 		<= CD_sEL;
CD1_ADC_I2C_ADD3 	   <= not CD_sEL;


I2C_CD2_ADD_GND 		<= '0';		
I2C_CD2_ADD_VDD 		<= '1';
CD2_ADC_I2C_ADD2 		<= not CD_sEL;
CD2_ADC_I2C_ADD3 		<= CD_sEL;




--------------------------------------
----- register map -------

--MISC_U1_IO(0) <= I2C_LVDS_SDA_W2C_P;
--MISC_U1_IO(1) <= FASTCOMMAND_IN_P;
--MISC_U1_IO(2) <= CLK_64MHZ_SYS_P;
--MISC_U1_IO(3) <= CLK_62_5MHz;
--MISC_U1_IO(4) <= CLK_100MHz;
--MISC_U1_IO(5 downto 3)	<= reg63_p(2 downto 0);
--MISC_U1_IO(3) <= reset;
--MISC_U1_IO(4) <= SYS_RESET;
--SC_U1_IO(5) <= CLK_10MHze

--MISC_U1_IO(0)	<= FE_CMN_CSA when reg62_p(3) = '0' else  EFUSE_CSB ;
--MISC_U1_IO(1)	<= FE_CMN_CSB when reg62_p(3) = '0' else  EFUSE_DIN ;
--MISC_U1_IO(2)	<= FE_CMN_CSC when reg62_p(3) = '0' else  EFUSE_PGM ;
--MISC_U1_IO(3)	<= '0'        when reg62_p(3) = '0' else  EFUSE_SLCK;
--MISC_U1_IO(4)	<= '0'        when reg62_p(3) = '0' else  EFUSE_VDDQ;
--MISC_U1_IO(5)	<= reg62_p(3) ;

SYS_RESET				<= reg0_p(0);							-- SYSTEM RESET
REG_RESET				<= reg0_p(1);							-- RESISTER RESET
	
CD_sEL				<= reg1_p(0);
CD1_PAD_RESET 		<= not reg1_p(4);
CD2_PAD_RESET 		<= not reg1_p(5);

--CD1_CONTROL <= reg3_o_p (4 downto 0) when reg66_p(0) = '1' else (others => 'Z');
--CD2_CONTROL <= reg2_o_p (4 downto 0) when reg66_p(1) = '1' else (others => 'Z');

reg3_p <= b"000" & CD1_CONTROL;
reg2_p <= b"000" & CD2_CONTROL;

SOCKET_RDOUT_SEL <= reg4_p(2 downto 0);

--INA226 I2C MASTERS
I2C_ADDRESS				<= reg5_p;
I2C_DEV_ADDR 			<= reg6_p(6 downto 0);
I2C_NUM_BYTES			<= reg7_p(3 downto 0);
I2C_DIN					<= reg9_p & reg8_p; 

I2C_WR_STRB_S1		 	<= reg10_p(0);
I2C_RD_STRB_S1			<= reg10_p(1);
I2C_WR_STRB_S2		   <= reg10_p(2);
I2C_RD_STRB_S2		   <= reg10_p(3);
I2C_WR_STRB_FE			<= reg10_p(4);
I2C_RD_STRB_FE			<= reg10_p(5);

reg11_p					<= I2C_DOUT_S1(7 downto 0);
reg12_p					<= I2C_DOUT_S1(15 downto 8);

reg13_p					<= I2C_DOUT_S2(7 downto 0);
reg14_p					<= I2C_DOUT_S2(15 downto 8);

reg15_p					<= I2C_DOUT_FE(7 downto 0);
reg16_p					<= I2C_DOUT_FE(15 downto 8);

--AD7274
cots_adc_start       <= reg17_p(0);


reg18_p					 <= CD1_MonADC_data(7 downto 0);
reg19_p					 <= CD1_MonADC_busy & b"000" & CD1_MonADC_data(11 downto 8);

reg20_p					 <= CD2_MonADC_data(7 downto 0);
reg21_p					 <= CD2_MonADC_busy & b"000" & CD2_MonADC_data(11 downto 8);

reg22_p					 <= ADC_MonADC_data(7 downto 0);
reg23_p					 <= ADC_MonADC_busy & b"000" & ADC_MonADC_data(11 downto 8);

reg24_p					 <= FE_MonADC_data(7 downto 0);
reg25_p					 <= FE_MonADC_busy & b"000" & FE_MonADC_data(11 downto 8);


--MUXES ETC
CD1_AMON_CSA   <= reg26_p(0);	
CD1_AMON_CSB 	<= reg26_p(1);	
CD1_AMON_CSC 	<= reg26_p(2);	
CD1_AMON_INH 	<= reg26_p(3);		

CD2_AMON_CSA 	<= reg26_p(4);		
CD2_AMON_CSB 	<= reg26_p(5);	
CD2_AMON_CSC 	<= reg26_p(6);	
CD2_AMON_INH 	<= reg26_p(7);

ADC_TEST_CSA 	<= reg27_p(0);
ADC_TEST_CSB 	<= reg27_p(1);
ADC_TEST_CSC 	<= reg27_p(2);

FE_TEST_CSA	 	<= reg27_p(4);		
FE_TEST_CSB	 	<= reg27_p(5); 
FE_TEST_CSC	 	<= reg27_p(6);


ADC_TEST_INH 	<= reg28_p;

FE_TEST_INH_ARR	<= reg29_p;

--FE_IN_TST_SEL(7 downto 0) <= reg30_p; --rev.0
--FE_IN_TST_SEL(15 downto 8) <= reg31_p;--rev.0
FE_IN_TST_SEL(7 downto 0) <= not reg30_p; --rev.1
FE_IN_TST_SEL(15 downto 8) <= not reg31_p;--rev.1


FE_CALI_CS(0) <= reg32_p(0) AND (not Test_pulse); --rev v3
FE_CALI_CS(1) <= reg32_p(1) AND (not Test_pulse);--rev v3
FE_CALI_CS(2) <= reg32_p(2) AND (not Test_pulse);--rev v3
FE_CALI_CS(3) <= reg32_p(3) AND (not Test_pulse);--rev v3
FE_CALI_CS(4) <= reg32_p(4) AND (not Test_pulse);--rev v3
FE_CALI_CS(5) <= reg32_p(5) AND (not Test_pulse);--rev v3
FE_CALI_CS(6) <= reg32_p(6) AND (not Test_pulse);--rev v3
FE_CALI_CS(7) <= reg32_p(7) AND (not Test_pulse);--rev v3



ADC_TST_SEL <= reg33_p;

ADC_SRC_CS_P0	<=reg34_p(0); --'1';
ADC_SRC_CS_P1	<=reg34_p(1); --'1';
ADC_SRC_CS_P2	<=reg34_p(2); --'1';
ADC_SRC_CS_P3	<=reg34_p(3); --'1';
ADC_SRC_CS_P4	<=reg34_p(4); --'1';	
ADC_SRC_CS_P5	<=reg34_p(5); --'1';
ADC_SRC_CS_P6	<=reg34_p(6); --'1';	
ADC_SRC_CS_P7	<=reg34_p(7); --'1';		

ADC_SRC_CS_P8	<=reg35_p(0); --'1';
ADC_SRC_CS_P9	<=reg35_p(1); --'1';
ADC_SRC_CS_PA	<=reg35_p(2); --'1';
ADC_SRC_CS_PB	<=reg35_p(3); --'1';
ADC_SRC_CS_PC	<=reg35_p(4); --'1';
ADC_SRC_CS_PD	<=reg35_p(5); --'1';		
ADC_SRC_CS_PE	<=reg35_p(6); --'1';		
ADC_SRC_CS_PF	<=reg35_p(7); --'1';	

ADC_P_TST_CSA 			<= reg36_p(0);
ADC_P_TST_CSB 			<= reg36_p(1);
ADC_P_TST_CSC			<= reg36_p(2);
ADC_P_TST_AMON_INH	<= reg36_p(3);
ADC_N_TST_CSA			<= reg36_p(4);
ADC_N_TST_CSB			<= reg36_p(5);
ADC_N_TST_CSC			<= reg36_p(6);
ADC_N_TST_AMON_INH	<= reg36_p(7);

ADC_TEST_IN_SEL <= reg37_p(0);

--EXT_PULSE_CNTL <=	reg38_p(0) AND (not Test_pulse);	--DAT rev.0
EXT_PULSE_CNTL <=	not reg38_p(0);	--DAT rev.1

	
--DAC, ETC
FE_DAC_TP_set <= reg39_p;

FE_DAC_TP_data(7 downto 0) <= reg40_p;
FE_DAC_TP_data(15 downto 8) <= reg41_p;
FE_DAC_TP_CMD <= "0100" when reg42_p(7) = '1' else "0011";
DAC_TP_CMD 	  <= "0100" when reg42_p(6) = '1' else "0011";
DAC_ADC_N_CMD <= "0100" when reg42_p(5) = '1' else "0011";
DAC_ADC_P_CMD <= "0100" when reg42_p(4) = '1' else "0011";

--DAC_other_set <= reg42_p(2 downto 0);
DAC_TP_set <= reg42_p(2);
DAC_ADC_N_set <= reg42_p(1);
DAC_ADC_P_set <= reg42_p(0);


DAC_ADC_P_data(7 downto 0) <= reg43_p;
DAC_ADC_P_data(15 downto 8) <= reg44_p;

DAC_ADC_N_data(7 downto 0) <= reg45_p;
DAC_ADC_N_data(15 downto 8) <= reg46_p;

DAC_TP_data(7 downto 0) <= reg47_p;
DAC_TP_data(15 downto 8) <= reg48_p;

reg49_p <= ro_cnt(7 downto 0);
reg50_p <= ro_cnt(15 downto 8);
reg51_p <= ro_cnt(23 downto 16);
reg52_p <= ro_cnt(31 downto 24);

ADC_POR_NAND <= reg53_p;
ADC_CHIP_ACTIVE <= reg54_p;


FPGA_TP_EN           <= reg55_p(0);
ASIC_TP_EN           <= reg55_p(1);
INT_TP_EN            <= reg55_p(2); --internal means coming from FPGA or ASIC
EXT_TP_EN            <= reg55_p(3); --external means coming from WIB

--Test pulse gen
--TP_SOCKET_EN			<= reg56_p;
FE_INS_PLS_CS(0) <= reg56_p(0) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(1) <= reg56_p(1) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(2) <= reg56_p(2) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(3) <= reg56_p(3) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(4) <= reg56_p(4) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(5) <= reg56_p(5) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(6) <= reg56_p(6) AND (not Test_pulse); --rev v3
FE_INS_PLS_CS(7) <= reg56_p(7) AND (not Test_pulse); --rev v3

Test_PULSE_WIDTH     <= reg58_p & reg57_p;
--TP_AMPL              <= reg56_p;
TP_AMPL              <= x"00";
TP_DLY               <= reg59_p;
TP_PERIOD				<= reg61_p & reg60_p; 

FE_CMN_CSA	 	<= reg62_p(0);		
FE_CMN_CSB	 	<= reg62_p(1); 
FE_CMN_CSC	 	<= reg62_p(2);
FE_CMN_INH	 	<= reg62_p(3);
--reg 62 bit 4 is used in fw for DAT original revision

--reg 64 & 65 used for CD1/2 MonADC D_SHT, PH_SEL, ADC_CS_POS	

CD1_EFUSE_start						<= reg67_p(0);		 -- bit (0) 0->1 will start EFUSE programming	
CD2_EFUSE_start						<= reg67_p(4);		 -- bit (0) 0->1 will start EFUSE programming	


--reg68_p(0) <= CD1_LOCK_OUT;
--reg68_p(1) <= CD2_LOCK_OUT;
--reg68_p(2) <= CD1_LOCK;
--reg68_p(3) <= CD2_LOCK;

reg_adc(7 downto 0)   <= reg72_p;
reg_adc(15 downto 8)  <= reg73_p;
reg_adc(23 downto 16) <= reg74_p;
reg_adc(31 downto 24) <= reg75_p;
reg_adc(39 downto 32) <= reg76_p;
reg_adc(47 downto 40) <= reg77_p;
reg_adc(55 downto 48) <= reg78_p;
reg_adc(63 downto 56) <= reg79_p;

reg_fe(7 downto 0)   <= reg80_p;
reg_fe(15 downto 8)  <= reg81_p;
reg_fe(23 downto 16) <= reg82_p;
reg_fe(31 downto 24) <= reg83_p;
reg_fe(39 downto 32) <= reg84_p;
reg_fe(47 downto 40) <= reg85_p;
reg_fe(55 downto 48) <= reg86_p;
reg_fe(63 downto 56) <= reg87_p;

CD1_EFUSE_DATA(7 downto 0)	   <= reg88_p;   
CD1_EFUSE_DATA(15 downto 8)	   <= reg89_p;    
CD1_EFUSE_DATA(23 downto 16)   <= reg90_p;    
CD1_EFUSE_DATA(31 downto 24)   <= reg91_p;    
CD2_EFUSE_DATA(7 downto 0)	   <= reg92_p;   
CD2_EFUSE_DATA(15 downto 8)	   <= reg93_p;    
CD2_EFUSE_DATA(23 downto 16)   <= reg94_p;    
CD2_EFUSE_DATA(31 downto 24)   <= reg95_p;    


----------------------------------------------------

--SOCKET_RDOUT_SEL MUXES
	
--FE1/ADC1	
I2C_WR_STRB_FE_arr(0) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"000" else '0';							
I2C_RD_STRB_FE_arr(0) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"000" else '0';							

--FE2/ADC2
I2C_WR_STRB_FE_arr(1) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"001" else '0';							
I2C_RD_STRB_FE_arr(1)	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"001" else '0';							

--FE3/ADC3
I2C_WR_STRB_FE_arr(2) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"010" else '0';							
I2C_RD_STRB_FE_arr(2) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"010" else '0';		

--FE4/ADC4
I2C_WR_STRB_FE_arr(3) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"011" else '0';							
I2C_RD_STRB_FE_arr(3) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"011" else '0';				
	
--FE5/ADC5
I2C_WR_STRB_FE_arr(4) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"100" else '0';							
I2C_RD_STRB_FE_arr(4) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"100" else '0';				

--FE6/ADC6
I2C_WR_STRB_FE_arr(5) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"101" else '0';							
I2C_RD_STRB_FE_arr(5) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"101" else '0';					

--FE5/ADC7
I2C_WR_STRB_FE_arr(6) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"110" else '0';							
I2C_RD_STRB_FE_arr(6) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"110" else '0';					
--FE6/ADC8
I2C_WR_STRB_FE_arr(7) 	<= I2C_WR_STRB_FE when SOCKET_RDOUT_SEL = b"111" else '0';							
I2C_RD_STRB_FE_arr(7) 	<= I2C_RD_STRB_FE when SOCKET_RDOUT_SEL = b"111" else '0';					

I2C_DOUT_FE			<= I2C_DOUT_FE_arr(0)	when SOCKET_RDOUT_SEL = b"000" else 
							I2C_DOUT_FE_arr(1)	when SOCKET_RDOUT_SEL = b"001" else 
							I2C_DOUT_FE_arr(2)	when SOCKET_RDOUT_SEL = b"010" else
							I2C_DOUT_FE_arr(3)	when SOCKET_RDOUT_SEL = b"011" else
							I2C_DOUT_FE_arr(4)	when SOCKET_RDOUT_SEL = b"100" else
							I2C_DOUT_FE_arr(5)	when SOCKET_RDOUT_SEL = b"101" else
							I2C_DOUT_FE_arr(6)	when SOCKET_RDOUT_SEL = b"110" else
							I2C_DOUT_FE_arr(7)	when SOCKET_RDOUT_SEL = b"111" else
							(others => '0');

FE_MonADC_busy 	<= FE_MonADC_busy_arr(0) when SOCKET_RDOUT_SEL = b"000" else 
							FE_MonADC_busy_arr(1) when SOCKET_RDOUT_SEL = b"001" else 
							FE_MonADC_busy_arr(2) when SOCKET_RDOUT_SEL = b"010" else 
							FE_MonADC_busy_arr(3) when SOCKET_RDOUT_SEL = b"011" else 
							FE_MonADC_busy_arr(4) when SOCKET_RDOUT_SEL = b"100" else 
							FE_MonADC_busy_arr(5) when SOCKET_RDOUT_SEL = b"101" else 
							FE_MonADC_busy_arr(6) when SOCKET_RDOUT_SEL = b"110" else 
							FE_MonADC_busy_arr(7) when SOCKET_RDOUT_SEL = b"111" else 
							'0';


FE_MonADC_data   	<= FE_MonADC_data_arr(0) when SOCKET_RDOUT_SEL = b"000" else 
							FE_MonADC_data_arr(1) when SOCKET_RDOUT_SEL = b"001" else 
							FE_MonADC_data_arr(2) when SOCKET_RDOUT_SEL = b"010" else 
							FE_MonADC_data_arr(3) when SOCKET_RDOUT_SEL = b"011" else 
							FE_MonADC_data_arr(4) when SOCKET_RDOUT_SEL = b"100" else 
							FE_MonADC_data_arr(5) when SOCKET_RDOUT_SEL = b"101" else 
							FE_MonADC_data_arr(6) when SOCKET_RDOUT_SEL = b"110" else 
							FE_MonADC_data_arr(7) when SOCKET_RDOUT_SEL = b"111" else 
							(others => '0');


ADC_MonADC_busy 	<= ADC_MonADC_busy_arr(0) when SOCKET_RDOUT_SEL = b"000" else 
							ADC_MonADC_busy_arr(1) when SOCKET_RDOUT_SEL = b"001" else 
							ADC_MonADC_busy_arr(2) when SOCKET_RDOUT_SEL = b"010" else 
							ADC_MonADC_busy_arr(3) when SOCKET_RDOUT_SEL = b"011" else 
							ADC_MonADC_busy_arr(4) when SOCKET_RDOUT_SEL = b"100" else 
							ADC_MonADC_busy_arr(5) when SOCKET_RDOUT_SEL = b"101" else 
							ADC_MonADC_busy_arr(6) when SOCKET_RDOUT_SEL = b"110" else 
							ADC_MonADC_busy_arr(7) when SOCKET_RDOUT_SEL = b"111" else 
							'0';


ADC_MonADC_data  	<= ADC_MonADC_data_arr(0) when SOCKET_RDOUT_SEL = b"000" else 
							ADC_MonADC_data_arr(1) when SOCKET_RDOUT_SEL = b"001" else 
							ADC_MonADC_data_arr(2) when SOCKET_RDOUT_SEL = b"010" else 
							ADC_MonADC_data_arr(3) when SOCKET_RDOUT_SEL = b"011" else 
							ADC_MonADC_data_arr(4) when SOCKET_RDOUT_SEL = b"100" else 
							ADC_MonADC_data_arr(5) when SOCKET_RDOUT_SEL = b"101" else 
							ADC_MonADC_data_arr(6) when SOCKET_RDOUT_SEL = b"110" else 
							ADC_MonADC_data_arr(7) when SOCKET_RDOUT_SEL = b"111" else 
							(others => '0');
							
							
FE_DAC_TP_data_arr(0) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"000" else (others => '0');
FE_DAC_TP_data_arr(1) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"001" else (others => '0');
FE_DAC_TP_data_arr(2) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"010" else (others => '0');
FE_DAC_TP_data_arr(3) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"011" else (others => '0');
FE_DAC_TP_data_arr(4) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"100" else (others => '0');
FE_DAC_TP_data_arr(5) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"101" else (others => '0');
FE_DAC_TP_data_arr(6) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"110" else (others => '0');
FE_DAC_TP_data_arr(7) <= FE_DAC_TP_data ;--when SOCKET_RDOUT_SEL = b"111" else (others => '0');
							

ro_cnt <= 	ro_cnt_arr(0) when SOCKET_RDOUT_SEL = b"000" else 
				ro_cnt_arr(1) when SOCKET_RDOUT_SEL = b"001" else 
				ro_cnt_arr(2) when SOCKET_RDOUT_SEL = b"010" else 
				ro_cnt_arr(3) when SOCKET_RDOUT_SEL = b"011" else 
				ro_cnt_arr(4) when SOCKET_RDOUT_SEL = b"100" else 
				ro_cnt_arr(5) when SOCKET_RDOUT_SEL = b"101" else 
				ro_cnt_arr(6) when SOCKET_RDOUT_SEL = b"110" else 
				ro_cnt_arr(7) when SOCKET_RDOUT_SEL = b"111" else 
				(others => '0');


CD1_LOCK_inst: ENTITY WORK.CD_LOCK_CNT 
  PORT MAP(
	 clk  =>    clk_62_5Mhz, --?
	 reset    => reg69_p(0),
	 lock_in    => CD1_LOCK,
	 lock_cnt   =>  reg68_p(3 downto 0) 
);

CD2_LOCK_inst: ENTITY WORK.CD_LOCK_CNT 
  PORT MAP(
	 clk  =>    clk_62_5Mhz, --?
	 reset    => reg69_p(0),
	 lock_in    => CD2_LOCK,
	 lock_cnt   =>  reg68_p(7 downto 4) 
);

----CD_LOCK signal stretcher
----When CD1/2_LOCK is low, prolong CD1/2_LOCK_OUT by 100 clock cycles
----so that the low-ness can be read by software
--cd_lock_stretcher : process(CLK_62_5MHz, reset)
----	variable counter1 : integer range 0 to 100;
----	variable counter2 : integer range 0 to 100;
--begin
--	if (reset = '1') then	
--		CD1_LOCK_OUT <= CD1_LOCK;
--		CD2_LOCK_OUT <= CD2_LOCK;
--		counter1 <= 0;
--		counter2 <= 0;
--	elsif (CLK_62_5MHz'event  AND  CLK_62_5MHz = '1') then	
--		if (CD1_LOCK = '0') then
--			CD1_LOCK_OUT <= '0';
--			counter1 <= 0;
--		else
--			counter1 <= counter1 + 1;
--			if (counter1 = 100) then
--				CD1_LOCK_OUT <= CD1_LOCK;	
--			end if;					
--		end if;
--		
--		if (CD2_LOCK = '0') then
--			CD2_LOCK_OUT <= '0';
--			counter2 <= 0;
--		else
--			counter2 <= counter2 + 1;
--			if (counter2 = 100) then
--				CD2_LOCK_OUT <= CD2_LOCK;	
--			end if;			
--			
--		end if;		
--		
--		
--		
--	end if;
--end process cd_lock_stretcher;

sys_rst_inst : entity work.sys_rst
PORT MAP(	clk 			=> CLK_50MHz,
				reset_in 	=> SYS_RESET,
				start 		=> start,
				RST_OUT 		=> reset);


DAT_PLL_inst : entity work.DAT_PLL 
	PORT MAP (
		inclk0	 => CLK_64MHZ_SYS_P,
		c0	 => CLK_125MHz,
		c1	 => CLK_100MHz,
		c2	 => CLK_62_5MHz,
		c3	 => CLK_50MHz,
		c4	 => CLK_25MHz,
		locked	 => open
	);

	
DAT_PLL2_inst : entity work.DAT_PLL2 
	PORT MAP (
		inclk0	 => CLK_64MHZ_SYS_P,
		c0	 => CLK_12_5MHz,
		c1	 => CLK_1M953125Hz,
		c2	 => CLK_10MHz
	);

	

	
	
I2CSLAVE : entity work.I2CSLAVE

	port MAP(
		sys_clk			=> CLK_62_5MHz,
		rst				=> reset,
		FPGA_ADDRESS	=> '0',
		I2C_BRD_ADDR	=> b"1100000",
		SDA_IO_IN		=> I2C_LVDS_SDA_W2C_P ,
		SDA_IO_OUT		=> I2C_LVDS_SDA_C2W_P,		
		SCL				=> I2C_LVDS_SCL_P,
		REG_ADDRESS		=> WIB_ADDRESS,
		REG_DOUT			=> WIB_DATA_OUT,
		REG_DIN			=> WIB_DATA_IN,
		REG_WR_STRB		=> WIB_WR,	
		REG_RD_STRB 	=> WIB_RD,
		CD_c2W_IN		=> I2C_SDA_c2w,
		CD_W2C_IN		=> I2C_SDA_W2C,
		CD_I2C_SCL		=> I2C_SCL);
	
	

CD1_INA226_master  : entity work.I2c_master
PORT MAP
(
	rst   	   	=> reset,			
	sys_clk	   	=> CLK_12_5MHz,
	SCL_O         	=> CD1_FPGA_CD_INA_SCL, --toplevel port
	SDA         	=> CD1_FPGA_CD_INA_SDA,					
	I2C_WR_STRB 	=> I2C_WR_STRB_S1, -- 1
	I2C_RD_STRB 	=> I2C_RD_STRB_S1, -- 1
	I2C_DEV_ADDR	=> I2C_DEV_ADDR, --7
	I2C_NUM_BYTES	=> I2C_NUM_BYTES,	--4 
	I2C_ADDRESS		=> I2C_ADDRESS,  -- 8 --used only with WR_STRB 
	I2C_DOUT			=> I2C_DOUT_S1, --16 used
	I2C_DIN			=> x"0000" & I2C_DIN, --16 used
	I2C_BUSY       => open,
	I2C_DEV_AVL		=> open
);

CD2_INA226_master  : entity work.I2c_master
PORT MAP
(
	rst   	   	=> reset,			
	sys_clk	   	=> CLK_12_5MHz,
	SCL_O         	=> CD2_FPGA_CD_INA_SCL, --toplevel port
	SDA         	=> CD2_FPGA_CD_INA_SDA,					
	I2C_WR_STRB 	=> I2C_WR_STRB_S2, -- 1
	I2C_RD_STRB 	=> I2C_RD_STRB_S2, -- 1
	I2C_DEV_ADDR	=> I2C_DEV_ADDR, --7
	I2C_NUM_BYTES	=> I2C_NUM_BYTES,	--4 
	I2C_ADDRESS		=> I2C_ADDRESS,  -- 8 --used only with WR_STRB 
	I2C_DOUT			=> I2C_DOUT_S2, --16 used
	I2C_DIN			=> x"0000" & I2C_DIN, --16 used
	I2C_BUSY       => open,
	I2C_DEV_AVL		=> open
);

gen_FE_INA: for i in 0 to 7 generate
	FE_INA226_master  : entity work.I2c_master
	PORT MAP
	(
		rst   	   	=> reset,			
		sys_clk	   	=> CLK_12_5MHz,
	--	SCL_O         	=> FE1_INA_SCL, --toplevel port
	--	SDA         	=> FE1_INA_SDA,
		SCL_O         	=> FE_INA_SCL(i), --toplevel port
		SDA         	=> FE_INA_SDA(i),					
		I2C_WR_STRB 	=> I2C_WR_STRB_FE_arr(i), -- 1
		I2C_RD_STRB 	=> I2C_RD_STRB_FE_arr(i), -- 1
		I2C_DEV_ADDR	=> I2C_DEV_ADDR, --7
		I2C_NUM_BYTES	=> I2C_NUM_BYTES,	--4 
		I2C_ADDRESS		=> I2C_ADDRESS,  -- 8 --used only with WR_STRB 
		I2C_DOUT			=> I2C_DOUT_FE_arr(i), --16 used
		I2C_DIN			=> x"0000" & I2C_DIN, --16 used
		I2C_BUSY       => open,
		I2C_DEV_AVL		=> open
	);
end generate gen_FE_INA;


--CD1_EFUSE_DATA regs 88-95
--CD1/2_EFUSE_START reg67

CD1_EFUSE_COLDATA_inst :  entity work.EFUSE_COLDATA
	PORT MAP
	(
		clk     		=> CLK_62_5MHz,
		reset       => reset,			
		start			=> CD1_EFUSE_start,
		EFUSE_DATA	=> CD1_EFUSE_DATA,
		EFUSE_CSB	=> CD1_EFUSE_CSB,
        EFUSE_DIN 	=> CD1_EFUSE_DIN,
        EFUSE_PGM	=> CD1_EFUSE_PGM,
        EFUSE_SLCK  => CD1_EFUSE_SCLK, 
        EFUSE_VDDQ	=> CD1_EFUSE_VDDQ,	
		BuSY			=> open
	);

CD2_EFUSE_COLDATA_inst :  entity work.EFUSE_COLDATA
	PORT MAP
	(
		clk     		=> CLK_62_5MHz,
		reset       => reset,			
		start			=> CD2_EFUSE_start,
		EFUSE_DATA	=> CD2_EFUSE_DATA,
		EFUSE_CSB	=> CD2_EFUSE_CSB,
        EFUSE_DIN 	=> CD2_EFUSE_DIN,
        EFUSE_PGM	=> CD2_EFUSE_PGM,
        EFUSE_SLCK  => CD2_EFUSE_SCLK, 
        EFUSE_VDDQ	=> CD2_EFUSE_VDDQ,	
		BuSY			=> open
	);


CD1_MonADC_inst : entity work.ADC_AD7274
  PORT MAP
  (
    clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
    reset     => reset,                    -- reset, active high reset
    start     => cots_adc_start,                    -- enable signal for i2c bus.
	 
	 D_SHT		=> reg64_p(1 downto 0),
	 PH_SEL		=> reg64_p(3 downto 2),
	 ADC_CS_POS	=> reg64_p(5 downto 4),

	 ADC_SDO  => CD1_MonADC_SDO,	                  	 -- 2.5V pin  			
	 ADC_SCK	 => CD1_MonADC_SCK,                    	 -- 2.5V pin				
	 ADC_CS	 => CD1_MonADC_CS,                    	 -- 2.5V pin			
	 DATA_OUT => CD1_MonADC_data,
	 busy     => CD1_MonADC_busy,		
	 rdy		 => open	
	);
	
	
CD2_MonADC_inst : entity work.ADC_AD7274
  PORT MAP
  (
    clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
    reset     => reset,                    -- reset, active high reset
    start     => cots_adc_start,                    -- enable signal for i2c bus.
	 
	 D_SHT		=> reg65_p(1 downto 0),
	 PH_SEL		=> reg65_p(3 downto 2),
	 ADC_CS_POS	=> reg65_p(5 downto 4),


	 ADC_SDO  => CD2_MonADC_SDO,	                  	 -- 2.5V pin  			
	 ADC_SCK	 => CD2_MonADC_SCK,                    	 -- 2.5V pin				
	 ADC_CS	 => CD2_MonADC_CS,                    	 -- 2.5V pin			
	 DATA_OUT => CD2_MonADC_data,
	 busy     => CD2_MonADC_busy,		
	 rdy		 => open	
	);
	
	
--reg_adc tied to regs 72-29

ADC1_MonADC_inst : entity work.ADC_AD7274
  PORT MAP
  (
    clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
    reset     => reset,                    -- reset, active high reset
    start     => cots_adc_start,                    -- enable signal for i2c bus.
	 
	 D_SHT		=> reg_adc(1 downto 0),
	 PH_SEL		=> reg_adc(3 downto 2),
	 ADC_CS_POS	=> reg_adc(5 downto 4),

	 ADC_SDO  => ADC_MonADC_SDO(0),	                  	 -- 2.5V pin  			
	 ADC_SCK	 => ADC_MonADC_SCK,                    	 -- 2.5V pin				
	 ADC_CS	 => ADC_MonADC_CS,                    	 -- 2.5V pin			
	 DATA_OUT => ADC_MonADC_data_arr(0),
	 busy     => ADC_MonADC_busy_arr(0),		
	 rdy		 => open	
	);
	

gen_ADC_MonADC: for i in 7 downto 1 generate
	ADC_MonADC_inst : entity work.ADC_AD7274
	  PORT MAP
	  (
		 clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
		 reset     => reset,                    -- reset, active high reset
		 start     => cots_adc_start,                    -- enable signal for i2c bus.
		 
		 D_SHT		=> reg_adc(8*i+1 downto 8*i),
		 PH_SEL		=> reg_adc(8*i+3 downto 8*i+2),
		 ADC_CS_POS	=> reg_adc(8*i+5 downto 8*i+4),
	
		 ADC_SDO  => ADC_MonADC_SDO(i),	                  	 -- 2.5V pin  			
		 ADC_SCK	 => open,                    	 -- 2.5V pin				
		 ADC_CS	 => open,                    	 -- 2.5V pin				
		 DATA_OUT => ADC_MonADC_data_arr(i),
		 busy     => ADC_MonADC_busy_arr(i),		
		 rdy		 => open	
		);
end generate gen_ADC_MonADC;

--reg_fe regs 80-87

FE1_MonADC_inst : entity work.ADC_AD7274
  PORT MAP
  (
    clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
    reset     => reset,                    -- reset, active high reset
    start     => cots_adc_start,                    -- enable signal for i2c bus.
	 
	 D_SHT		=> reg_fe(1 downto 0),
	 PH_SEL		=> reg_fe(3 downto 2),
	 ADC_CS_POS	=> reg_fe(5 downto 4),

	 ADC_SDO  => FE_MonADC_SDO(0),	                  	 -- 2.5V pin  			
	 ADC_SCK	 => FE_MonADC_SCK,                    	 -- 2.5V pin				
	 ADC_CS	 => FE_MonADC_CS,                    	 -- 2.5V pin			
	 DATA_OUT => FE_MonADC_data_arr(0),
	 busy     => FE_MonADC_busy_arr(0),		
	 rdy		 => open	
	);
	

gen_FE_MonADC : for i in 7 downto 1 generate
	FE_MonADC_inst : entity work.ADC_AD7274
	  PORT MAP
	  (
		 clk       => CLK_25MHz,                       -- system clock 40MHz, can be used for sclk directly
		 reset     => reset,                    -- reset, active high reset
		 start     => cots_adc_start,                    -- enable signal for i2c bus.
		 
		 D_SHT		=> reg_fe(8*i+1 downto 8*i),
		 PH_SEL		=> reg_fe(8*i+3 downto 8*i+2),
		 ADC_CS_POS	=> reg_fe(8*i+5 downto 8*i+4),
	
		 ADC_SDO  => FE_MonADC_SDO(i),	                  	 -- 2.5V pin  			
		 ADC_SCK	 => open,                    	 -- 2.5V pin				
		 ADC_CS	 => open,                    	 -- 2.5V pin			
		 DATA_OUT => FE_MonADC_data_arr(i),
		 busy     => FE_MonADC_busy_arr(i),		
		 rdy		 => open	
		);
end generate gen_FE_MonADC;

--All 8 DACs are configurated at the same time with the same value actually. 
FE1_DAC_TP_inst : entity work.DAC8411 --AD5683R
	PORT MAP
	(
	 	 clk         	=> CLK_25MHz,         
		 reset			=> reset,	
		 start			=> FE_DAC_TP_set(0),
		 DATA				=> FE_DAC_TP_data_arr(0),
		 CMD				=> FE_DAC_TP_CMD,
		 SCLK				=> FE_DAC_TP_SCK,
		 DIN				=> FE_DAC_TP_DIN(0),
		 SYNC				=> FE_DAC_TP_SYNC
	);

gen_FE_DAC_TP : for i in 7 downto 1 generate
	FE_DAC_TP_inst : entity work.DAC8411 --AD5683R
		PORT MAP
		(
			 clk         	=> CLK_25MHz,         
			 reset			=> reset,	
			 start			=> FE_DAC_TP_set(0),
			 DATA				=> FE_DAC_TP_data_arr(i),
		     CMD				=> FE_DAC_TP_CMD,
			 SCLK				=> open,
			 DIN				=> FE_DAC_TP_DIN(i),
			 SYNC				=> open
		);
end generate gen_FE_DAC_TP;

DAC_ADC_P_inst : entity work.DAC8411 --AD5683R
	PORT MAP
	(
	 	 clk         	=> CLK_25MHz,         
		 reset			=> reset,	
		 start			=> DAC_ADC_P_set,
		 --start			=> DAC_other_set(0),
		 DATA				=> DAC_ADC_P_data,
		 CMD				=> DAC_ADC_P_CMD,
		 SCLK				=> DAC_ADC_P_SCK,
		 DIN				=> DAC_ADC_P_DIN,
		 SYNC				=> DAC_ADC_P_SYNC
	);

DAC_ADC_N_inst : entity work.DAC8411 --AD5683R
	PORT MAP
	(
	 	 clk         	=> CLK_25MHz,         
		 reset			=> reset,	
--		 start			=> DAC_other_set(1),
		 start			=> DAC_ADC_N_set,
		 DATA				=> DAC_ADC_N_data,
		 CMD				=> DAC_ADC_N_CMD,
		 SCLK				=> DAC_ADC_N_SCK,
		 DIN				=> DAC_ADC_N_DIN,
		 SYNC				=> DAC_ADC_N_SYNC
	);

DAC_TP_inst : entity work.DAC8411 --AD5683R
	PORT MAP
	(
	 	 clk         	=> CLK_25MHz,         
		 reset			=> reset,	
--		 start			=> DAC_other_set(2),
		 start			=> DAC_TP_set,
		 DATA				=> DAC_TP_data,
		 CMD				=> DAC_TP_CMD,
		 SCLK				=> DAC_TP_SCK,
		 DIN				=> DAC_TP_DIN,
		 SYNC				=> DAC_TP_SYNC
	);


gen_ro_cnt: for i in 7 downto 0 generate	
	ro_inst: ENTITY WORK.COLDADC_RO_CNT 
	  PORT MAP(
		 clk  =>    clk_100Mhz, --?
		 reset    => reset,
--		 ro_start => reg63_p(0),
--		 ro_cntx10ns => reg95_p(7 downto 0) & reg94_p(7 downto 0) & reg93_p(7 downto 0) & reg92_p(7 downto 0),
		 ro_in    => ADC_RO_OUT(i),
		 ro_cnt   =>  ro_cnt_arr(i)  
	);
end generate gen_ro_cnt;


TST_PULSE_GEN_inst : entity work.SBND_TST_PULSE 
	PORT MAP 
	(
		sys_rst 				=> reset,	
		clk					=> CLK_62_5MHz,
		FPGA_TP_EN			=> FPGA_TP_EN, --reg
		ASIC_TP_EN			=> ASIC_TP_EN,	--reg	
		INT_TP_EN			=> INT_TP_EN,  --reg --internal means coming from FPGA or ASIC
		EXT_TP_EN			=> EXT_TP_EN,  --reg --external means coming from WIB
		TP_EXT_GEN			=> TP_EXT_GEN, --coming from PWM module --WIB calibration. not used
		LA_SYNC		 		=> TP_INT_GEN, --coming from ProtoDUNE_RDOUT module --<= clk_2Mhz;
		TP_WIDTH				=> Test_PULSE_WIDTH,
		TP_AMPL				=> b"00" & TP_AMPL & b"00", --not used
		TP_DLY				=>	x"00" & TP_DLY,
		TP_FREQ				=> TP_PERIOD,	 
		DAC_CNTL				=> DAC_CNTL(11 DOWNTO 0), --not used
		ASIC_DAC_CNTL		=> ASIC_DAC_CNTL,
		Test_pulse			=> Test_pulse
	);

DUNE_DAT_Registers_inst :  entity work.DUNE_DAT_Registers
	PORT MAP
	(
		--rst         => reset or REG_RESET,	
		rst         => reset,	
		clk         => CLK_62_5MHz,

		BOARD_ID		=> x"0A", --16bit
		VERSION_ID	=> x"2B",
		
		
		WIB_data       =>	WIB_DATA_IN,
		WIB_WR_address => WIB_ADDRESS,
		WIB_RD_address => WIB_ADDRESS,
		WIB_WR    	 	=> WIB_WR,
		WIB_data_out	=> WIB_DATA_OUT,
			
		
		reg0_i 	=> reg0_p,
		reg1_i 	=> reg1_p,		 
		reg2_i 	=> reg2_p,		 
		reg3_i 	=> reg3_p,
		reg4_i 	=> reg4_p,
		reg5_i 	=> reg5_p,
		reg6_i 	=> reg6_p,
		reg7_i 	=> reg7_p,
		reg8_i 	=> reg8_p,
		reg9_i 	=> reg9_p,		 
		reg10_i 	=> reg10_p,
		reg11_i 	=> reg11_p,		
		reg12_i 	=> reg12_p,
		reg13_i 	=> reg13_p,
		reg14_i 	=> reg14_p,	
		reg15_i 	=> reg15_p,	
		reg16_i 	=> reg16_p,
		reg17_i 	=> reg17_p,
		reg18_i 	=> reg18_p,
		reg19_i 	=> reg19_p,		 
		reg20_i  => reg20_p,
		reg21_i 	=> reg21_p,
		reg22_i 	=> reg22_p,
		reg23_i 	=> reg23_p,
		reg24_i 	=> reg24_p,
		reg25_i 	=> reg25_p,	
		reg26_i 	=> reg26_p,
		reg27_i 	=> reg27_p,
		reg28_i 	=> reg28_p,
		reg29_i 	=> reg29_p,		 
		reg30_i  => reg30_p,	
		reg31_i 	=> reg31_p,
		reg32_i 	=> reg32_p,
		reg33_i 	=> reg33_p,
		reg34_i 	=> reg34_p,
		reg35_i 	=> reg35_p,	
		reg36_i 	=> reg36_p,
		reg37_i 	=> reg37_p,
		reg38_i 	=> reg38_p,
		reg39_i 	=> reg39_p,			 		 
		reg40_i 	=> reg40_p,	
		reg41_i 	=> reg41_p,
		reg42_i 	=> reg42_p,
		reg43_i 	=> reg43_p,
		reg44_i 	=> reg44_p,
		reg45_i 	=> reg45_p,	
		reg46_i 	=> reg46_p,
		reg47_i 	=> reg47_p,
		reg48_i 	=> reg48_p,
		reg49_i 	=> reg49_p,		 
		reg50_i  => reg50_p,	
		reg51_i 	=> reg51_p,
		reg52_i 	=> reg52_p,
		reg53_i 	=> reg53_p,
		reg54_i 	=> reg54_p,
		reg55_i 	=> reg55_p,	
		reg56_i 	=> reg56_p,
		reg57_i 	=> reg57_p,
		reg58_i 	=> reg58_p,
		reg59_i 	=> reg59_p,	
		reg60_i 	=> reg60_p,	
		reg61_i 	=> reg61_p,
		reg62_i 	=> reg62_p,
		reg63_i 	=> reg63_p,
		reg64_i 	=> reg64_p,
		reg65_i 	=> reg65_p,	
		reg66_i 	=> reg66_p,
		reg67_i 	=> reg67_p,
		reg68_i 	=> reg68_p,
		reg69_i 	=> reg69_p,	
		reg70_i 	=> reg70_p,	
		reg71_i 	=> reg71_p,
		reg72_i 	=> reg72_p,
		reg73_i 	=> reg73_p,
		reg74_i 	=> reg74_p,
		reg75_i 	=> reg75_p,	
		reg76_i 	=> reg76_p,
		reg77_i 	=> reg77_p,
		reg78_i 	=> reg78_p,
		reg79_i 	=> reg79_p,	
		reg80_i 	=> reg80_p,	
		reg81_i 	=> reg81_p,
		reg82_i 	=> reg82_p,
		reg83_i 	=> reg83_p,
		reg84_i 	=> reg84_p,
		reg85_i 	=> reg85_p,	
		reg86_i 	=> reg86_p,
		reg87_i 	=> reg87_p,
		reg88_i 	=> reg88_p,
		reg89_i 	=> reg89_p,	
		reg90_i 	=> reg90_p,
		reg91_i 	=> reg91_p,
		reg92_i 	=> reg92_p,
		reg93_i 	=> reg93_p,
		reg94_i 	=> reg94_p,
		reg95_i 	=> reg95_p,

		
		reg0_o 	=> reg0_p,
		reg1_o 	=> reg1_p,		 
		reg2_o 	=> open,		 
		reg3_o   => open,
		reg4_o 	=> reg4_p,
		reg5_o 	=> reg5_p,
		reg6_o 	=> reg6_p,
		reg7_o 	=> reg7_p,
		reg8_o 	=> reg8_p,
		reg9_o 	=> reg9_p,
		reg10_o 	=> reg10_p,
		reg11_o 	=> open,
		reg12_o 	=> open,
		reg13_o 	=> open,
		reg14_o 	=> open,
		reg15_o 	=> open,
		reg16_o 	=> open,
		reg17_o 	=> reg17_p,
		reg18_o 	=> open,
		reg19_o 	=> open,
		reg20_o 	=> open,
		reg21_o 	=> open,
		reg22_o 	=> open,
		reg23_o 	=> open,
		reg24_o 	=> open,
		reg25_o 	=> open,
		reg26_o 	=> reg26_p,
		reg27_o 	=> reg27_p,
		reg28_o 	=> reg28_p,
		reg29_o 	=> reg29_p,	 
		reg30_o 	=> reg30_p,
		reg31_o 	=> reg31_p,
		reg32_o 	=> reg32_p,
		reg33_o 	=> reg33_p,
		reg34_o 	=> reg34_p,
		reg35_o 	=> reg35_p,
		reg36_o 	=> reg36_p,
		reg37_o 	=> reg37_p,
		reg38_o 	=> reg38_p,
		reg39_o 	=> reg39_p,	
		reg40_o 	=> reg40_p,	
		reg41_o 	=> reg41_p,
		reg42_o 	=> reg42_p,
		reg43_o 	=> reg43_p,
		reg44_o 	=> reg44_p,
		reg45_o 	=> reg45_p,
		reg46_o 	=> reg46_p,
		reg47_o 	=> reg47_p,
		reg48_o 	=> reg48_p,
		reg49_o 	=> open,		 
		reg50_o  => open,	
		reg51_o 	=> open,
		reg52_o 	=> open,
		reg53_o 	=> reg53_p,
		reg54_o 	=> reg54_p,
		reg55_o 	=> reg55_p,
		reg56_o 	=> reg56_p,
		reg57_o 	=> reg57_p,
		reg58_o 	=> reg58_p,
		reg59_o 	=> reg59_p,
		reg60_o 	=> reg60_p,
		reg61_o 	=> reg61_p,
		reg62_o 	=> reg62_p, 
		reg63_o 	=> reg63_p,
		reg64_o 	=> reg64_p,
		reg65_o 	=> reg65_p,
		reg66_o 	=> reg66_p,
		reg67_o 	=> reg67_p,
		reg68_o 	=> open,
		reg69_o 	=> reg69_p,
		reg70_o 	=> reg70_p,
		reg71_o 	=> reg71_p,
		reg72_o 	=> reg72_p,
		reg73_o 	=> reg73_p,
		reg74_o 	=> reg74_p,
		reg75_o 	=> reg75_p,	
		reg76_o 	=> reg76_p,
		reg77_o 	=> reg77_p,
		reg78_o 	=> reg78_p,
		reg79_o 	=> reg79_p,	
		reg80_o 	=> reg80_p,	
		reg81_o 	=> reg81_p,
		reg82_o 	=> reg82_p,
		reg83_o 	=> reg83_p,
		reg84_o 	=> reg84_p,
		reg85_o 	=> reg85_p,	
		reg86_o 	=> reg86_p,
		reg87_o 	=> reg87_p,
		reg88_o 	=> reg88_p,
		reg89_o 	=> reg89_p,	
		reg90_o 	=> reg90_p,
		reg91_o 	=> reg91_p,
		reg92_o 	=> reg92_p,
		reg93_o 	=> reg93_p,
		reg94_o 	=> reg94_p,
		reg95_o 	=> reg95_p
		
	);

end DUNE_DAT_FPGA_arch;

--/////////////////////////////////////////////////////////////////////
--////                              
--////  File: ADC_ad7274.VHD            
--////                                                                                                                                      
--////  Author: Jack Fried			                  
--////          jfried@bnl.gov	              
--////  Created: 08/03/2015
--////  Description:  
--////					
--////
--/////////////////////////////////////////////////////////////////////
--////
--//// Copyright (C) 2015 Brookhaven National Laboratory
--////
--/////////////////////////////////////////////////////////////////////


LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_arith.all;
USE ieee.std_logic_unsigned.all;


--  Entity Declaration

ENTITY EFUSE_COLDATA IS

	PORT
	(
		clk     		: IN STD_LOGIC;	-- 62.5MHz clock		
		reset       : IN STD_LOGIC;			
		start			: IN STD_LOGIC;	-- single sampl
		
		
		EFUSE_DATA	: IN STD_LOGIC_VECTOR(31 downto 0);  -- ONLY (bits 31..1) will be programmed 
		EFUSE_CSB	: OUT STD_LOGIC;  -- MISC_U1_IO(0) 
      EFUSE_DIN 	: OUT STD_LOGIC;  -- MISC_U1_IO(1)
      EFUSE_PGM	: OUT STD_LOGIC;  -- MISC_U1_IO(2)
      EFUSE_SLCK  : OUT STD_LOGIC;  -- MISC_U1_IO(3)
      EFUSE_VDDQ	: OUT STD_LOGIC;   -- MISC_U1_IO(4) 
		
		BuSY			: OUT STD_LOGIC 	

	);
END EFUSE_COLDATA;


ARCHITECTURE behavior OF EFUSE_COLDATA IS



  type state_type is (
		S_IDLE,
		S_Start_EFUSE,
		S_Start_EFUSE_DATA_set,
		S_Start_EFUSE_CHECK,
		S_Start_EFUSE_DONE
		);

  signal state: state_type;
  
  signal	CLK_CNT			: STD_LOGIC_VECTOR(15 downto 0);
  signal EFUSE_DATA_s	: STD_LOGIC_VECTOR(31 downto 0);  
  signal	start_S1			: STD_LOGIC;  
  signal	start_S2			: STD_LOGIC;  
  signal BIT_CNT		   : STD_LOGIC_VECTOR(7 downto 0);
begin

	
process(clk,reset) 
  begin
     if (clk'event AND clk = '1') then
			start_S1	<= start;
			start_S2	<= start_S1;			
     end if;
end process;	
	
	
	 
  process(clk,reset) 
  begin
     if (reset = '1') then
	
			EFUSE_CSB	<= '1';  -- MISC_U1_IO(0) 
			EFUSE_DIN 	<= '1';  -- MISC_U1_IO(1)
			EFUSE_PGM	<= '0';  -- MISC_U1_IO(2)
			EFUSE_SLCK  <= '0';  -- MISC_U1_IO(3)
			EFUSE_VDDQ	<= '0';  -- MISC_U1_IO(4) 
			busy        <= '0';
			CLK_CNT 		<=	x"0000";
			BIT_CNT		<= x"00";
			state 		<= S_IDLE;
     elsif (clk'event AND clk = '1') then
     CASE state IS
     when S_IDLE =>	 
	  
			busy        <= '0';
			EFUSE_CSB	<= '1';  -- MISC_U1_IO(0) 
			EFUSE_DIN 	<= '1';  -- MISC_U1_IO(1)
			EFUSE_PGM	<= '0';  -- MISC_U1_IO(2)
			EFUSE_SLCK  <= '0';  -- MISC_U1_IO(3)
			EFUSE_VDDQ	<= '0';  -- MISC_U1_IO(4) 
			busy        <= '0';
			BIT_CNT		<= x"00";
			CLK_CNT 		<=	x"0000";
			if (start_S1 = '1' AND start_S2 = '0' ) then
				busy         	<= '1';
				--EFUSE_DATA_s	<= EFUSE_DATA(31 downto 1) & '1';	
				EFUSE_DATA_s	<= EFUSE_DATA; --10142024, all bits be programmed
				EFUSE_DIN 		<= '0';  -- MISC_U1_IO(1)
				EFUSE_PGM		<= '1';  -- MISC_U1_IO(2)
				EFUSE_VDDQ		<= '1';  -- MISC_U1_IO(4) 			
				state 			<= S_Start_EFUSE ;


         end if;	
     when S_Start_EFUSE =>
			CLK_CNT 		<= CLK_CNT + 1;
			if(CLK_CNT  = 457) then
				EFUSE_CSB	<= '0';  -- MISC_U1_IO(0) 
			end if;
			if(CLK_CNT  = 614) then
				EFUSE_PGM		<= '0';   -- MISC_U1_IO(0) 
			end if;
			if(CLK_CNT  >= 761) then
				CLK_CNT 		<=	x"0000";
				state 		<= S_Start_EFUSE_DATA_set;
				EFUSE_PGM	<= EFUSE_DATA_s(0);
				EFUSE_DATA_s(30 downto 0) <= EFUSE_DATA_s(31 downto 1);
				BIT_CNT		<= BIT_CNT + 1;
			end if;	
     when S_Start_EFUSE_DATA_set =>
			CLK_CNT 		<= CLK_CNT + 1;
			if(CLK_CNT  = 20) then
				EFUSE_SLCK  <= '1';
			elsif(CLK_CNT  = 334) then
				EFUSE_SLCK  <= '0';
			elsif(CLK_CNT  = 491) then
				EFUSE_PGM	<= EFUSE_DATA_s(0);
				EFUSE_DATA_s(30 downto 0) <= EFUSE_DATA_s(31 downto 1);
				BIT_CNT		<= BIT_CNT + 1;
			elsif(CLK_CNT  = 530) then
				CLK_CNT 		<=	x"0000";
				state 		<= S_Start_EFUSE_CHECK;
			end if;
	  when S_Start_EFUSE_CHECK =>
			if(BIT_CNT >= 33) then
				state 		<= S_Start_EFUSE_DONE;
				EFUSE_CSB	<= '1';  -- MISC_U1_IO(0) 
				CLK_CNT 		<=	x"0000";
			else
				state 		<= S_Start_EFUSE_DATA_set;
			end if;	
				
 	  when S_Start_EFUSE_DONE =>
			CLK_CNT 		<= CLK_CNT + 1;
			if(CLK_CNT >= 52) then
			   	state 	<= S_IDLE;
			end if;	
	  when others =>	
			state <= S_idle;		
      end case;  
     end if;
end process;




	
END behavior;

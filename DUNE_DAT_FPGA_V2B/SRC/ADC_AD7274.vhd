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

ENTITY ADC_AD7274 IS

	PORT
	(
		clk     		: IN STD_LOGIC;	--128MHz   2MSps				
		reset       : IN STD_LOGIC;			
		start			: IN STD_LOGIC;	-- single sampl
		D_SHT			: IN STD_LOGIC_VECTOR(1 downto 0);
		PH_SEL		: IN STD_LOGIC_VECTOR(1 downto 0);
		ADC_CS_POS	: IN STD_LOGIC_VECTOR(1 downto 0);
		ADC_SDO     : IN STD_LOGIC;			
		ADC_SCK		: OUT STD_LOGIC;				
		ADC_CS		: OUT STD_LOGIC;					
		DATA_OUT		: OUT STD_LOGIC_VECTOR(11 downto 0);
		busy  		: OUT STD_LOGIC;	
		rdy			: OUT STD_LOGIC 	-- pulse 	when cont_sampl  : level when single sample

	);
END ADC_AD7274;


ARCHITECTURE behavior OF ADC_AD7274 IS



  type state_type is (
		S_IDLE,
		S_ADC_READ_CLK_H1,
		S_ADC_READ_CLK_H2,
		S_ADC_READ_CLK_L1,
		S_ADC_READ_CLK_L2,
		S_ADC_DONE
		);

  signal state: state_type;
  signal	CLK_CNT			: STD_LOGIC_VECTOR(7 downto 0);
  signal Data 	  	  	 	: STD_LOGIC_VECTOR(15 downto 0);
  signal Data1 	  	 	: STD_LOGIC_VECTOR(15 downto 0);  
  signal Data2 	  	 	: STD_LOGIC_VECTOR(15 downto 0);  
  signal Data3 	  	 	: STD_LOGIC_VECTOR(15 downto 0);  
  signal Data4 	  	 	: STD_LOGIC_VECTOR(15 downto 0);   
  signal RDY_o			 	: STD_LOGIC;
  signal RDY_DLY1		 	: STD_LOGIC;
  signal	start_S1			: STD_LOGIC;  
  signal	start_S2			: STD_LOGIC;  
begin

	
process(clk,reset) 
  begin
     if (clk'event AND clk = '1') then
			RDY_DLY1 <= RDY_o;			
			RDY		<= RDY_DLY1;
			start_S1	<= start;
			start_S2	<= start_S1;			
     end if;
end process;	
	
	 
  process(clk,reset) 
  begin
     if (reset = '1') then
		ADC_CS		<= '1';
		ADC_SCK		<= '1';
		RDY_o			<= '0';
		DATA_OUT		<= (others=>'0');
		DATA			<= X"0000";
		CLK_CNT 		<=	x"00";
		busy         <= '0';
     elsif (clk'event AND clk = '1') then
     CASE state IS
     when S_IDLE =>	 
			ADC_CS			<= '1';
			ADC_SCK			<= '1';
			CLK_CNT 			<=	x"00";
			busy         <= '0';
			if (start_S1 = '1' AND start_S2 = '0' ) then
			  state 			<= S_ADC_READ_CLK_H1 ;
			  DATA			<= X"0000";			  
			  RDY_o 			<= '0';
			  busy         <= '1';
			  if(ADC_CS_POS = 0) then
					ADC_CS			<= '0';
				end if;
         end if;	
     when S_ADC_READ_CLK_H1 =>
			CLK_CNT 		<= CLK_CNT + 1;
			if((ADC_CS_POS = 0) or (ADC_CS_POS = 1)) then
				ADC_CS		<= '0';
			end if;
			ADC_SCK		<= '1';
			state 		<= S_ADC_READ_CLK_H2;
     when S_ADC_READ_CLK_H2 =>
  			ADC_CS		<= '0';
			state 					 <= S_ADC_READ_CLK_L1;			
			if (CLK_CNT >  14) then    
				ADC_CS		<= '1';	
				state 		<= S_ADC_DONE;						
				if(PH_SEL = b"00") then
					Data		<= DATA1;
				elsif (PH_SEL = b"01") then
					Data		<= DATA2;
				elsif (PH_SEL = b"10") then
					Data		<= DATA3;
				else	
					Data		<= DATA4;
				end if;
			end if;
    when S_ADC_READ_CLK_L1 =>
			ADC_SCK		<= '0';
			state 		<= S_ADC_READ_CLK_L2 ; 	
    when S_ADC_READ_CLK_L2 =>
			state 		<= S_ADC_READ_CLK_H1;
	when S_ADC_DONE =>
			RDY_o 	<= '1';
			busy         <= '0';
			if (D_SHT = b"00") then	
				DATA_OUT		<= DATA(11 downto 0);
			elsif (D_SHT = b"01") then	
				DATA_OUT		<= DATA(12 downto 1);
			elsif (D_SHT = b"10") then	
				DATA_OUT		<= DATA(13 downto 2);
			else
				DATA_OUT		<= DATA(14 downto 3);
			end if;
			state 	<= S_IDLE;	
	 when others =>	
			state <= S_idle;		
      end case;  
     end if;
end process;




  process(clk,reset) 
  begin
     if (clk'event AND clk = '1') then
			if(state = S_ADC_READ_CLK_H1 ) then	  
	  			Data1(0) 	<= ADC_SDO;
				Data1(15 downto 1)	 <= Data1(14 downto 0);
			elsif(state = S_ADC_READ_CLK_H2 ) then
				Data2(0) 				<= ADC_SDO;
				Data2(15 downto 1)	<= Data2(14 downto 0);
			elsif(state =  S_ADC_READ_CLK_L1) then
				Data3(0) 		<= ADC_SDO;
				Data3(15 downto 1)	 <= Data3(14 downto 0);	 
			elsif(state =  S_ADC_READ_CLK_L2) then
				Data4(0) 				 <= ADC_SDO;
				Data4(15 downto 1)	 <= Data4(14 downto 0);				
			end if;
		end if;
end process;	
	

	
END behavior;

--/////////////////////////////////////////////////////////////////////
--////                              
--////  File: I2C_slave_32bit.VHD          
--////                                                                                                                                      
--////  Author: Jack Fried			                  
--////          jfried@bnl.gov	              
--////  Created: 07/22/2013
--////  Description:  32 bit I2C slave interface
--////					
--////
--/////////////////////////////////////////////////////////////////////
--////
--//// Copyright (C) 2013 Brookhaven National Laboratory
--////
--/////////////////////////////////////////////////////////////////////

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.STD_LOGIC_arith.all;
use IEEE.STD_LOGIC_unsigned.all;




--  Entity Declaration

ENTITY I2CSLAVE IS

	PORT
	(
		rst   	   : IN 	STD_LOGIC;				
		sys_clk	   : IN 	STD_LOGIC;
		FPGA_ADDRESS: IN 	STD_LOGIC;		
		I2C_BRD_ADDR: IN 	STD_LOGIC_VECTOR(6 downto 0);		
		SCL         : IN 	STD_LOGIC;
		SDA_IO_IN   : IN 	STD_LOGIC;										
		SDA_IO_OUT  : OUT	STD_LOGIC;										
		REG_ADDRESS	: OUT STD_LOGIC_VECTOR(7 downto 0);
		REG_DOUT		: IN  STD_LOGIC_VECTOR(7 downto 0);
		REG_DIN		: OUT STD_LOGIC_VECTOR(7 downto 0);
		REG_WR_STRB : OUT STD_LOGIC;
		REG_RD_STRB : OUT STD_LOGIC;
		
		CD_c2W_IN	: IN STD_LOGIC;
		CD_W2C_IN	: OUT STD_LOGIC;
		CD_I2C_SCL	: OUT STD_LOGIC
		
		
		
	);
	
END I2CSLAVE;


ARCHITECTURE behavior OF I2CSLAVE  IS





  type i2c_state_typ is ( s_idle , s_get_addr,	  s_send_addr_ack, 	  s_wait_ack,
									s_read_reg_addr, 	 s_send_reg_addr_ack ,   s_wait_addr_ack,																					
 									s_read_data , 		 s_send_data_ack , 		s_wait_data_ack ,
									s_write_data , 	 s_get_wait_data_ack, 	s_get_data_ack);
							 
							 						 
							 
  signal I2C_STATE : i2c_state_typ;

	
	SIGNAL SDA_OUT			: std_logic;
	SIGNAL SDA_IN			: STD_LOGIC_VECTOR( 1 downto 0);
	SIGNAL SCL_IN			: STD_LOGIC_VECTOR( 1 downto 0);	
	
	SIGNAL I2C_start		: std_logic;
	SIGNAL I2C_stop		: std_logic;
	
	
	SIGNAL SDA_rise		: std_logic;
	SIGNAL SDA_fall		: std_logic;
	
	SIGNAL SCL_rise		: std_logic;
	SIGNAL SCL_fall		: std_logic;
	

	SIGNAL I2C_busy 		: std_logic;
	SIGNAL I2C_bit_cnt 	: integer range 0 to 31;
	SIGNAL I2C_addr 		: STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_reg_addr  : STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_reg_data  : STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_data 		: STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_read 		: std_logic;
	SIGNAL I2C_write 		: std_logic;
	SIGNAL I2C_dout 		: STD_LOGIC_VECTOR(7 downto 0);	

	
	SIGNAL SDA_I			: std_logic;
	SIGNAL SDA_O			: std_logic;
	SIGNAL SDA_OE			: std_logic;
	
	SIGNAL CHIP_IO_SEL	: std_logic;
	SIGNAL I2C_chip_SEL			: std_logic_VECTOR(3 downto 0);
	SIGNAL I2C_addr_in	: STD_LOGIC_VECTOR(3 downto 0);	
	
begin



	CD_W2C_IN	<= SDA_IO_IN;
	SDA_I			<= SDA_IO_IN;
	CD_I2C_SCL	<= SCL;
	
	
	SDA_IO_OUT	<= SDA_OUT  		when (CHIP_IO_SEL = '0')   else 
						CD_c2W_IN;

	
--REG_DIN	<= x"76";
	
	process(sys_clk) 
	begin
		if rising_edge( sys_clk ) then	

			SDA_IN(0) <= SDA_IO_IN;
			SDA_IN(1) <= SDA_IN(0);
			SCL_IN(0) <= SCL;
			SCL_IN(1) <= SCL_IN(0);

		end if;
	end process;	


	SDA_fall		<=	(not SDA_IN(0)) and SDA_IN(1);
	SDA_rise		<= SDA_IN(0) and (not SDA_IN(1));
	SCL_fall		<=	(not SCL_IN(0)) and SCL_IN(1);
	SCL_rise		<= SCL_IN(0) and (not SCL_IN(1));
	
	I2C_start 	<= '1' when ( SDA_fall = '1' ) and ( SCL = '1' ) else '0'; 
	I2C_stop 	<= '1' when ( SDA_rise = '1' ) and ( SCL  = '1' ) else '0';	
	

     process( sys_clk , rst )
       begin
         if ( rst = '1' ) then
				SDA_OUT			<= '1';
				I2C_STATE 		<= s_idle;
				I2C_busy 		<= '0';
				I2C_bit_cnt 	<= 0;
				I2C_addr 		<= ( others => '0' );
				I2C_reg_addr 	<= ( others => '0' );
				I2C_reg_data 	<= ( others => '0' );
				I2C_data 		<= ( others => '0' );
				I2C_read 		<= '0';
				I2C_write 		<= '0';
				REG_WR_STRB 	<= '0';
				REG_RD_STRB		<= '0';
				I2C_dout 		<=  ( others => '0' );
				REG_ADDRESS		<=  ( others => '0' );
  			   REG_DIN		   <= x"00";
				CHIP_IO_SEL		<= '0';
         elsif rising_edge( sys_clk ) then
	        case I2C_STATE is
           ----------------------
           when s_idle =>
				I2C_busy 		<= '0';
				SDA_OUT	 		<= '1';
				I2C_bit_cnt 	<= 0;
				REG_WR_STRB 	<= '0';
				REG_RD_STRB		<= '0';
				if ( I2C_start  = '1' ) then
					I2C_STATE 		<= s_get_addr;
					I2C_busy 		<= '1';
				else
					I2C_STATE <= s_idle;
				end if;
           ----------------------
           when s_get_addr =>
             SDA_OUT <= '1';
             if ( I2C_stop = '0' ) then
               if ( SCL_rise = '1' ) then
                 if ( I2C_bit_cnt < 8 ) then               
                   I2C_addr 		<= I2C_addr( 6 downto 0 ) & SDA_IO_IN;
                   I2C_bit_cnt	<= I2C_bit_cnt + 1;  
                   I2C_STATE 		<= s_get_addr;
                 elsif( I2C_bit_cnt = 8 ) then
                   I2C_addr 		<= I2C_addr( 6 downto 0 ) & SDA_IO_IN;
                   I2C_bit_cnt 	<= 0; 
                   I2C_STATE 		<= s_send_addr_ack;                 
                 end if;
               elsif ( SCL_fall = '1' ) and ( I2C_bit_cnt = 8 ) then
                 I2C_STATE 	<= s_send_addr_ack;
                 I2C_bit_cnt 	<= 0;               
               else
                 I2C_STATE 	<= s_get_addr;
               end if;
             else
               I2C_STATE 	<= s_idle;
             end if;
           -----------------------      
           when s_send_addr_ack =>
             if ( I2C_addr(7 downto 1) = I2C_BRD_ADDR ) then  
               SDA_OUT 			<= '0';
					I2C_addr_in		<= I2C_addr(7 downto 4);			
               if ( SCL_rise = '1' ) then
						CHIP_IO_SEL	<= '0';
                 I2C_STATE 	<= s_wait_ack;
               end if;
             else
					CHIP_IO_SEL	<= '1';
               I2C_STATE <= s_idle;
             end if;        
           -----------------------     
           when s_wait_ack =>
				 I2C_data		<= REG_DOUT;
			--	 if (I2C_addr(0) = '1' ) then
			--		REG_RD_STRB		<= '1';
			--	 end if;
             if ( SCL_fall = '1' ) then
				 
					I2C_STATE 	<= s_read_reg_addr;
--						if ( I2C_addr(0) = '0' ) then
--						  I2C_STATE 	<= s_read_reg_addr;
--						elsif ( I2C_addr(0) = '1' ) then
--						  REG_RD_STRB	<= '0';
--						  I2C_STATE 	<= s_write_data;             
--						end if;	
             else
               I2C_STATE <= s_wait_ack;
             end if;
           -----------------------       


			  
           when s_read_reg_addr =>  
             SDA_OUT 	<= '1';
             if ( I2C_stop = '0' ) then
               if ( SCL_rise = '1' ) then
                 if ( I2C_bit_cnt < 8 ) then               
                   I2C_reg_addr(7 downto 0) 	<= I2C_reg_addr( 6 downto 0 ) & SDA_IO_IN;
                   I2C_bit_cnt 	<= I2C_bit_cnt + 1; 
                   I2C_STATE 		<= s_read_reg_addr;  
                 elsif ( I2C_bit_cnt = 8 ) then
                   I2C_reg_addr(7 downto 0)  <= I2C_reg_addr( 6 downto 0 ) & SDA_IO_IN;                                                    
                   I2C_bit_cnt <= 0;
                   I2C_STATE <= s_send_reg_addr_ack;
                 end if;    
					elsif ( SCL_fall = '1' ) and ( I2C_bit_cnt = 8 ) then
                 I2C_STATE 	<= s_send_reg_addr_ack;
                 I2C_bit_cnt 	<= 0;               				
               else
                 I2C_STATE <= s_read_reg_addr;
               end if;
             else
               I2C_STATE <= s_idle;
             end if;
           -----------------------  
           when s_send_reg_addr_ack =>  
				 REG_ADDRESS 	<= I2C_reg_addr;    
             SDA_OUT 		<= '0';				 
             if ( SCL_rise = '1' ) then
               I2C_STATE 	<= s_wait_addr_ack;
             end if;                  
           -----------------------
           when s_wait_addr_ack =>
             if ( SCL_fall = '1' ) then
               I2C_STATE 	<= s_read_data ;
				   I2C_data		<= REG_DOUT;	
					SDA_OUT 		<= '1';   	
	
					if ( I2C_addr(0) = '0' ) then
					  I2C_STATE 	<= s_read_data;
					else
					  I2C_STATE 	<= s_write_data;             
					end if;	
	
             else
               I2C_STATE 	<= s_wait_addr_ack;
             end if;  
				 
		
          ------------------------  
           when s_read_data =>
             if ( I2C_stop = '0' ) then
						if ( SCL_rise = '1' ) then
						  if ( I2C_bit_cnt < 8 ) then               
							 I2C_reg_data(7 downto 0) <= I2C_reg_data( 6 downto 0 ) & SDA_IO_IN;
							 I2C_bit_cnt <= I2C_bit_cnt + 1; 
							 I2C_STATE <= s_read_data;  
						  elsif ( I2C_bit_cnt = 8 ) then
							 I2C_reg_data(7 downto 0) <= I2C_reg_data( 6 downto 0 ) & SDA_IO_IN;                                                    
							 I2C_bit_cnt <= 0;
							 I2C_STATE <= s_send_data_ack;
						  end if;   
						elsif ( SCL_fall = '1' ) and ( I2C_bit_cnt = 8 ) then
						  I2C_STATE 	<= s_send_data_ack;
						  I2C_bit_cnt 	<= 0;     					
			
		
						else
						  I2C_STATE <= s_read_data;
						end if;        
	          else					
					I2C_STATE <= s_idle;
             end if;
          when s_send_data_ack =>  
					REG_DIN		<= I2C_reg_data;
               SDA_OUT 		<= '0';			 
             if ( SCL_rise = '1' ) then
					REG_DIN		<= I2C_reg_data;
               I2C_STATE 	<= s_wait_data_ack;
             end if;                  
           -----------------------
           when s_wait_data_ack =>
 				 REG_DIN		<= I2C_reg_data;
             if ( SCL_fall = '1' ) then
               I2C_STATE 		<= s_idle;
					SDA_OUT 			<= '1';   
					REG_WR_STRB 	<= '1';
             else
               I2C_STATE <= s_wait_data_ack;
             end if;  				 
			------------------------------------	
			
			
			

				 
           -----------------------    
           when s_write_data =>
             if ( I2C_stop = '0' ) then
               SDA_OUT 		<= I2C_data( 7 );               
               if ( SCL_fall = '1' ) then
                 if ( I2C_bit_cnt < 7 ) then
                   I2C_data(7 downto 0) 		<= I2C_data( 6 downto 0 ) & '0';
                   I2C_bit_cnt 	<= I2C_bit_cnt + 1;
                   I2C_STATE 		<= s_write_data;
                 elsif ( I2C_bit_cnt = 7 ) then
                   I2C_bit_cnt 	<= 0;
                   I2C_STATE 		<= s_get_wait_data_ack;
                 end if;
               end if;
             else
               I2C_STATE <= s_idle;
             end if;
           ----------------------- 
           when s_get_wait_data_ack =>
             SDA_OUT <= '1';
             if ( SCL_rise = '1' ) then
				  if ( SDA_IO_IN = '0' ) then
						I2C_STATE <= s_get_data_ack;
					ELSe
						I2C_STATE <= s_idle;
					END IF;
             else
               I2C_STATE <= s_get_wait_data_ack;
             end if;
           -----------------------
           when s_get_data_ack =>
             SDA_OUT <= '1';
             if ( SCL_fall = '1' ) then
                 I2C_STATE <= s_idle;
             else
               I2C_STATE <= s_get_data_ack;
             end if;
				 
		 
           -------------------------  
           when others => I2C_STATE <= s_idle;
           end case;   
			  if(I2C_STATE /= s_idle and I2C_start  = '1')then
					SDA_OUT	 		<= '1';
					I2C_bit_cnt 	<= 0;
					I2C_STATE 		<= s_get_addr;
					I2C_busy 		<= '1';
					REG_WR_STRB 	<= '0';
			 end if;
         end if;
       end process ;
	


	
END behavior;

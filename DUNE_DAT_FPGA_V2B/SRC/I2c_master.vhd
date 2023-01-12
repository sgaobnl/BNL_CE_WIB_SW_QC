--/////////////////////////////////////////////////////////////////////
--////                              
--////  File: I2c_master.VHD
--////                                                                                                                                      
--////  Author: Jack Fried                                        
--////          jfried@bnl.gov                
--////  Created:  07/25/2013
--////  Modified: 07/25/2013
--////  Description:  
--////                                  
--////
--/////////////////////////////////////////////////////////////////////
--////
--//// Copyright (C) 2014 Brookhaven National Laboratory
--////
--/////////////////////////////////////////////////////////////////////


library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.STD_LOGIC_arith.all;
use IEEE.STD_LOGIC_unsigned.all;





--  Entity Declaration

ENTITY I2c_master IS
			generic ( 
			
							ACK_DISABLE 	: STD_LOGIC := '1';  -- set to one  to disable the reqirment for the slave to send an ACK response 
							SCL_WIDTH  		: integer := 35 --added to slow down
						);			 
	PORT
	(
		rst   	   	: IN 	STD_LOGIC;				
		sys_clk	   	: IN 	STD_LOGIC;		
		
		SCL_O         	: OUT 	STD_LOGIC;
		SDA         	: INOUT 	STD_LOGIC;						
		I2C_WR_STRB 	: IN STD_LOGIC;
		I2C_RD_STRB 	: IN STD_LOGIC;
		I2C_DEV_ADDR	: IN  STD_LOGIC_VECTOR(6 downto 0);		
		I2C_NUM_BYTES	: IN  STD_LOGIC_VECTOR(3 downto 0);	  --I2C_NUM_BYTES --  For Writes 0 = address only,  1 = address + 1byte , 2 =  address + 2 bytes .... up to 4 bytes
																			  --I2C_NUM_BYTES --  For Reads  0 = read 1 byte,   1 = read 1 byte,  2 = read 2 bytes  ..  up to 4 bytes
		I2C_ADDRESS		: IN  STD_LOGIC_VECTOR(7 downto 0);	  -- used only with WR_STRB
		I2C_DOUT			: OUT STD_LOGIC_VECTOR(31 downto 0);	
		I2C_DIN			: IN  STD_LOGIC_VECTOR(31 downto 0);
		I2C_BUSY       : OUT	STD_LOGIC;
		I2C_DEV_AVL		: OUT STD_LOGIC
	);
	
END I2c_master;


ARCHITECTURE behavior OF I2c_master IS




  type i2c_state_typ is (s_idle ,s_send_start ,s_send_addr_1 ,s_send_addr_2 ,s_send_addr_3 ,s_addr_ack_1 ,s_addr_ack_2 ,s_addr_ack_3 ,s_addr_ack_4, 
								 s_WRTIE_DATA_1 ,s_WRTIE_DATA_2 ,s_WRTIE_DATA_3 ,s_WRITE_ack_1 ,s_WRITE_ack_2 ,s_WRITE_ack_3 ,s_WRITE_ack_4, 
								 S_READ_DATA_1 ,S_READ_DATA_2 ,S_READ_DATA_3 ,S_READ_DATA_4 ,s_READ_ack_1 ,s_READ_ack_2 ,s_READ_ack_3 ,s_READ_ack_4 ,S_I2C_STOP,S_I2C_STOP_2,s_done );
					 
  signal I2C_STATE : i2c_state_typ;

	
	
	SIGNAL SDA_OUT					: std_logic;
	SIGNAL I2C_bit_cnt 			: integer range 31 downto 0;
	SIGNAL SCL_CNT 				: integer range 127 downto 0;		
	SIGNAL BYTE_CNT 				: STD_LOGIC_VECTOR(3 downto 0);	
	SIGNAL I2C_RD_WR				: std_logic;
	SIGNAL I2C_WR_STRB_sync 	: STD_LOGIC;
	SIGNAL I2C_RD_STRB_sync 	: STD_LOGIC;	
	SIGNAL I2C_addr 				: STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_ack					: STD_LOGIC;	
	SIGNAL I2C_data 				: STD_LOGIC_VECTOR(7 downto 0);	
	SIGNAL I2C_DOUT_T				: STD_LOGIC_VECTOR(31 downto 0);	
	SIGNAL SCL						: STD_LOGIC;	
	
	
	
begin
	
	SDA		<= '0' when SDA_OUT ='0' else 'Z';
	SCL_O		<= '0' when SCL = '0' else '1';
	
	I2C_DEV_AVL		<= NOT I2C_ack;
	process(sys_clk) 
	begin
		if (sys_clk'event  AND  sys_clk = '1') then	
		
			I2C_WR_STRB_sync		<= I2C_WR_STRB;
			I2C_RD_STRB_sync		<= I2C_RD_STRB;
		end if;
	end process;	



     process( sys_clk , rst )
       begin
         if ( rst = '1' ) then
				SDA_OUT			<= 'Z';
				SCL				<= '1';
				I2C_BUSY 		<= '0';
				I2C_bit_cnt 	<= 7;
				SCL_CNT			<= 0;
				BYTE_CNT			<= ( others => '0' );
				I2C_ack			<= '1';
				I2C_addr 		<= ( others => '0' );
				I2C_DOUT			<= ( others => '0' );
				I2C_data			<= ( others => '0' );
				I2C_RD_WR		<= '0';
				I2C_STATE 		<= s_idle;				
				I2C_DOUT_T 		<= ( others => '0' );

         elsif rising_edge( sys_clk ) then
	        case I2C_STATE is
           ----------------------
           when s_idle =>
				I2C_busy 		<= '0';
				SDA_OUT	 		<= 'Z';
				SCL				<= '1';
				I2C_bit_cnt 	<= 7;
				SCL_CNT			<= 0;
				BYTE_CNT			<= ( others => '0' );
				if 	(I2C_RD_STRB_sync = '1' ) then
					I2C_RD_WR		<= '1';
					I2C_busy 		<= '1';
					I2C_addr			<= I2C_DEV_ADDR & '1';
					I2C_STATE 		<= s_send_start;
					I2C_DOUT_T 		<= ( others => '0' );
				elsif(I2C_WR_STRB_sync = '1') then
					I2C_RD_WR		<= '0';
					I2C_busy 		<= '1';
					I2C_addr			<= I2C_DEV_ADDR & '0';
					I2C_data			<= I2C_ADDRESS;
					I2C_STATE 		<= s_send_start;
				else
					I2C_STATE <= s_idle;
				end if;
           ----------------------
           when s_send_start =>	
					SDA_OUT	 	<= '0';
					SCL			<= '1';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_send_start;
					else  
						SCL_CNT		<= 0;
						SCL			<= '0';
						I2C_STATE 	<= s_send_addr_1;
					end if;
          --####################
          --## SEND DEV ADDRESS 
          --####################
	         when s_send_addr_1 =>	
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						SCL			<= '0';
						I2C_STATE 	<= s_send_addr_1;
					else  
						SCL_CNT		<= 0;
						SCL			<= '0';
						SDA_OUT	 	<= I2C_addr(I2C_bit_cnt);
						I2C_STATE 	<= s_send_addr_2;
					end if;				
	         when s_send_addr_2 =>	
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_send_addr_2;
					else  
						SCL_CNT		<= 0;
						I2C_STATE 	<= s_send_addr_3;
					end if;				
					
	         when s_send_addr_3 =>	
            if (SCL_CNT < SCL_WIDTH*2 ) then
              SCL				<= '1';
              SCL_CNT		<= SCL_CNT + 1;
              I2C_STATE 	<= s_send_addr_3;
            else  
              SCL_CNT		<= 0;             
              if ( I2C_bit_cnt >= 1 ) then
                I2C_bit_cnt 	<= I2C_bit_cnt - 1;
                I2C_STATE 		<= s_send_addr_1;
              else            
                I2C_STATE 		<= s_addr_ack_1;                
              end if;                                          
            end if;					
									
			 --####################
          --#### ACKNOWLEDGE ###
          --####################
          when s_addr_ack_1 =>
			 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_addr_ack_1;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_STATE 	<= s_addr_ack_2;
					end if;

          when s_addr_ack_2 => 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_addr_ack_2;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_STATE 	<= s_addr_ack_3;
					end if;
          when s_addr_ack_3 => 
					SCL			<= '1';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_addr_ack_3;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_ack		<= sda;
						I2C_STATE 	<= s_addr_ack_4;
					end if;
          when s_addr_ack_4 => 
						if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_addr_ack_4;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						SCL			<= '0';
						IF (I2C_ack = '0') THEN
							I2C_bit_cnt	<= 7;
							if(I2C_RD_WR	= '0') then 
								I2C_STATE 	<= s_WRTIE_DATA_1;
							else
								BYTE_CNT		<= x"1";
								I2C_STATE 	<= S_READ_DATA_1;
							end if;
						else --no response 
							SDA_OUT	 		<= 'Z'; 
							SCL				<= '1';
							I2C_STATE 		<= s_DONE;		
						end if;
	
					end if;


          --####################
          --## SEND DATA 
          --####################
	         when s_WRTIE_DATA_1 =>	
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						SCL			<= '0';
						I2C_STATE 	<= s_WRTIE_DATA_1;
					else  
						SCL_CNT		<= 0;
						SCL			<= '0';
						SDA_OUT	 	<= I2C_data(I2C_bit_cnt);
						I2C_STATE 	<= s_WRTIE_DATA_2;
					end if;				
	         when s_WRTIE_DATA_2 =>	
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_WRTIE_DATA_2;
					else  
						SCL_CNT		<= 0;
						I2C_STATE 	<= s_WRTIE_DATA_3;
					end if;				
					
	         when s_WRTIE_DATA_3 =>	
            if (SCL_CNT < SCL_WIDTH*2 ) then
              SCL				<= '1';
              SCL_CNT		<= SCL_CNT + 1;
              I2C_STATE 	<= s_WRTIE_DATA_3;
            else  
              SCL_CNT		<= 0;             
              if ( I2C_bit_cnt >= 1 ) then
                I2C_bit_cnt 	<= I2C_bit_cnt - 1;
                I2C_STATE 		<= s_WRTIE_DATA_1;
              else            
                I2C_STATE 		<= s_WRITE_ack_1;                
              end if;                                          
            end if;					
								
			 --####################
          --#### ACKNOWLEDGE ###
          --####################
          when s_WRITE_ack_1 =>
			 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_WRITE_ack_1;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_STATE 	<= s_WRITE_ack_2;
					end if;

          when s_WRITE_ack_2 => 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_WRITE_ack_2;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_STATE 	<= s_WRITE_ack_3;
					end if;
          when s_WRITE_ack_3 => 
					SCL			<= '1';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_WRITE_ack_3;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						I2C_ack		<= sda;
						I2C_STATE 	<= s_WRITE_ack_4;
					end if;
          when s_WRITE_ack_4 => 
						if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_WRITE_ack_4;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						SCL			<= '0';
						IF (I2C_ack = '0') THEN
							BYTE_CNT	<= BYTE_CNT	 + 1;
							IF(I2C_NUM_BYTES = BYTE_CNT) THEN
								SDA_OUT	 	<= '0';
								SCL			<= '1';
								I2C_STATE 	<= S_I2C_STOP;	
							ELSIF(BYTE_CNT	= X"0") THEN
								I2C_data		<= I2C_DIN(7 DOWNTO 0);
								I2C_STATE 	<= s_WRTIE_DATA_1;
							ELSIF(BYTE_CNT	= X"1") THEN
								I2C_data		<= I2C_DIN(15 DOWNTO 8);
								I2C_STATE 	<= s_WRTIE_DATA_1;	
							ELSIF(BYTE_CNT	= X"2") THEN
								I2C_data		<= I2C_DIN(23 DOWNTO 16);
								I2C_STATE 	<= s_WRTIE_DATA_1;
							ELSIF(BYTE_CNT	= X"3") THEN
								I2C_data		<= I2C_DIN(31 DOWNTO 24);
								I2C_STATE 	<= s_WRTIE_DATA_1;
							ELSE
								SDA_OUT	 	<= 'Z';
								SCL			<= '1';
								I2C_STATE 	<= s_idle;	
							END IF;	

						else
							SDA_OUT	 	<= 'Z';
							SCL			<= '1';
							I2C_STATE 	<= s_done;		
						end if;
	
					end if;


          --####################
          --## READ DATA 
          --####################


        when S_READ_DATA_1 =>	 
					SCL			<= '0';
					SDA_OUT	 	<= 'Z';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_READ_DATA_1;
					else  
						SCL_CNT		<= 0;
						I2C_STATE 	<= S_READ_DATA_2;
					end if;
          when S_READ_DATA_2 => 
					SCL			<= '0';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_READ_DATA_2;
					else  
						SCL_CNT		<= 0;
						I2C_STATE 	<= S_READ_DATA_3;
					end if;
          when S_READ_DATA_3 => 
					SCL			<= '1';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_READ_DATA_3;
					else  
						SCL_CNT		<= 0;
						I2C_data(I2C_bit_cnt)	<= SDA;
						I2C_STATE 					<= S_READ_DATA_4;
					end if;
          when S_READ_DATA_4 => 
						if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_READ_DATA_4;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= 'Z';
						SCL			<= '0';
	              if ( I2C_bit_cnt >= 1 ) then
							I2C_bit_cnt 	<= I2C_bit_cnt - 1;
							I2C_STATE 		<= S_READ_DATA_1;
						else            
							I2C_STATE <= s_READ_ack_1;                
						end if;                                		
					end if;


			 --####################
          --#### ACKNOWLEDGE ###
          --####################
          when s_READ_ack_1 =>			 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_READ_ack_1;
					else  
						SCL_CNT		<= 0;
						IF((I2C_NUM_BYTES <= X"1") OR (I2C_NUM_BYTES = BYTE_CNT)) THEN
							SDA_OUT	 	<= 'Z';
						else
							SDA_OUT	 	<= '0';
						end if;
						IF(BYTE_CNT	= X"1") THEN
							I2C_DOUT_T(7 DOWNTO 0)			<= I2C_data;
						ELSIF(BYTE_CNT	= X"2") THEN
							I2C_DOUT_T(15 DOWNTO 8)			<= I2C_data;
						ELSIF(BYTE_CNT	= X"3") THEN
							I2C_DOUT_T(23 DOWNTO 16)		<= I2C_data;
						ELSIF(BYTE_CNT	= X"4") THEN
							I2C_DOUT_T(31 DOWNTO 24)		<= I2C_data;
						ELSE
							I2C_DOUT_T <= x"deadbeef";
						END IF;	
						I2C_STATE 	<=s_READ_ack_2;						
					end if;
          when s_READ_ack_2 => 
					SCL			<= '0';
					I2C_bit_cnt	<= 7;
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<=s_READ_ack_2;
					else  
						SCL_CNT		<= 0;
						SCL			<= '1';
						I2C_STATE 	<= s_READ_ack_3;
					end if;
          when s_READ_ack_3 => 
					SCL			<= '1';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_READ_ack_3;
					else  
						SCL_CNT		<= 0;
						I2C_STATE 	<= s_READ_ack_4;
					end if;
          when s_READ_ack_4 => 
						if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= s_READ_ack_4;
					else  
						SDA_OUT	 	<= 'Z';
						SCL_CNT		<= 0;
						SCL			<= '0';
						BYTE_CNT		<= BYTE_CNT	 + 1;
						I2C_STATE 	<= S_READ_DATA_1;	
						IF((I2C_NUM_BYTES <= X"1") OR (I2C_NUM_BYTES = BYTE_CNT)) THEN
								I2C_STATE 	<= S_I2C_STOP;	
								SCL_CNT		<= 0;
						END IF;
					end if;
					
				--######################
          --######## STOP ########
          --######################    

				when S_I2C_STOP => 
					I2C_DOUT		<= I2C_DOUT_T;
					SCL			<= '0';
					SDA_OUT	 	<= '0';
					if (SCL_CNT < (SCL_WIDTH + SCL_WIDTH)) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_I2C_STOP ;
					else  
						SCL_CNT		<= 0;
						SCL			<= '1';
				--		SDA_OUT	 	<= '1';
						I2C_STATE 	<= S_I2C_STOP_2;	
					end if;	
					
				when S_I2C_STOP_2 => 
					I2C_DOUT		<= I2C_DOUT_T;
					SCL			<= '1';
					SDA_OUT	 	<= '0';
					if (SCL_CNT < SCL_WIDTH ) then
						SCL_CNT		<= SCL_CNT + 1;
						I2C_STATE 	<= S_I2C_STOP_2 ;
					else  
						SCL_CNT		<= 0;
						SDA_OUT	 	<= '1';
						I2C_STATE 	<= s_done;	
					end if;	

					
				when s_done => 
					I2C_busy 		<= '0';
					SDA_OUT	 		<= 'Z';
					SCL				<= '1';
					I2C_bit_cnt 	<= 7;
					SCL_CNT			<= 0;
					BYTE_CNT			<= ( others => '0' );
					if 	(I2C_RD_STRB_sync = '1' ) OR (I2C_WR_STRB_sync = '1') then
						I2C_STATE 		<= s_done;
					else
						I2C_STATE <= s_idle;
					end if;
           when others => I2C_STATE <= s_idle;
           end case;   
         end if;
       end process ;
	


	
END behavior;





















----/////////////////////////////////////////////////////////////////////
----////                              
----////  File: I2c_master.VHD
----////                                                                                                                                      
----////  Author: Jack Fried                                        
----////          jfried@bnl.gov                
----////  Created:  07/25/2013
----////  Modified: 07/25/2013
----////  Description:  
----////                                  
----////
----/////////////////////////////////////////////////////////////////////
----////
----//// Copyright (C) 2014 Brookhaven National Laboratory
----////
----/////////////////////////////////////////////////////////////////////
--
--
--library IEEE;
--use IEEE.STD_LOGIC_1164.all;
--use IEEE.STD_LOGIC_arith.all;
--use IEEE.STD_LOGIC_unsigned.all;
--
--
--
--
--
----  Entity Declaration
--
--ENTITY I2c_master IS
--			generic ( 
--			
--							ACK_DISABLE 	: STD_LOGIC := '1';  -- set to one  to disable the reqirment for the slave to send an ACK response 
--							SCL_WIDTH  		: integer := 10
--						);			 
--	PORT
--	(
--		rst   	   	: IN 	STD_LOGIC;				
--		sys_clk	   	: IN 	STD_LOGIC;		
--		
--		SCL_O         	: OUT 	STD_LOGIC;
--		SDA_I         	: IN STD_LOGIC;						
--      SDA_O         	: OUT STD_LOGIC;						
--		I2C_WR_STRB 	: IN STD_LOGIC;
--		I2C_RD_STRB 	: IN STD_LOGIC;
--		I2C_DEV_ADDR	: IN  STD_LOGIC_VECTOR(6 downto 0);		
--		I2C_NUM_BYTES	: IN  STD_LOGIC_VECTOR(3 downto 0);	  --I2C_NUM_BYTES --  For Writes 0 = address only,  1 = address + 1byte , 2 =  address + 2 bytes .... up to 4 bytes
--																			  --I2C_NUM_BYTES --  For Reads  0 = read 1 byte,   1 = read 1 byte,  2 = read 2 bytes  ..  up to 4 bytes
--		I2C_ADDRESS		: IN  STD_LOGIC_VECTOR(7 downto 0);	  -- used only with WR_STRB
--		I2C_DOUT			: OUT STD_LOGIC_VECTOR(31 downto 0);	
--		I2C_DIN			: IN  STD_LOGIC_VECTOR(31 downto 0);
--		I2C_BUSY       : OUT	STD_LOGIC;
--		I2C_DEV_AVL		: OUT STD_LOGIC
--	);
--	
--END I2c_master;
--
--
--ARCHITECTURE behavior OF I2c_master IS
--
--
--
--
--  type i2c_state_typ is (s_idle ,s_send_start ,s_send_addr_1 ,s_send_addr_2 ,s_send_addr_3 ,s_addr_ack_1 ,s_addr_ack_2 ,s_addr_ack_3 ,s_addr_ack_4, 
--								 s_WRTIE_DATA_1 ,s_WRTIE_DATA_2 ,s_WRTIE_DATA_3 ,s_WRITE_ack_1 ,s_WRITE_ack_2 ,s_WRITE_ack_3 ,s_WRITE_ack_4, 
--								 S_READ_DATA_1 ,S_READ_DATA_2 ,S_READ_DATA_3 ,S_READ_DATA_4 ,s_READ_ack_1 ,s_READ_ack_2 ,s_READ_ack_3 ,s_READ_ack_4 ,S_I2C_STOP,S_I2C_STOP_2,s_done );
--					 
--  signal I2C_STATE : i2c_state_typ;
--
--	
--	
--	SIGNAL SDA_OUT					: std_logic;
--	SIGNAL I2C_bit_cnt 			: integer range 31 downto 0;
--	SIGNAL SCL_CNT 				: integer range 127 downto 0;		
--	SIGNAL BYTE_CNT 				: STD_LOGIC_VECTOR(3 downto 0);	
--	SIGNAL I2C_RD_WR				: std_logic;
--	SIGNAL I2C_WR_STRB_sync 	: STD_LOGIC;
--	SIGNAL I2C_RD_STRB_sync 	: STD_LOGIC;	
--	SIGNAL I2C_addr 				: STD_LOGIC_VECTOR(7 downto 0);	
--	SIGNAL I2C_ack					: STD_LOGIC;	
--	SIGNAL I2C_data 				: STD_LOGIC_VECTOR(7 downto 0);	
--	SIGNAL I2C_DOUT_T				: STD_LOGIC_VECTOR(31 downto 0);	
--	SIGNAL SCL						: STD_LOGIC;	
--	SIGNAL SDA						: STD_LOGIC;		
--	
--	
--begin
--	
----	SDA		<= '0' when SDA_OUT ='0' else '1';
--	
--	SDA_O	<= SDA_OUT;
--	SDA		<= SDA_I;
--	
--	SCL_O		<= '0' when SCL = '0' else '1';
--	
--	I2C_DEV_AVL		<= NOT I2C_ack;
--	process(sys_clk) 
--	begin
--		if (sys_clk'event  AND  sys_clk = '1') then	
--		
--			I2C_WR_STRB_sync		<= I2C_WR_STRB;
--			I2C_RD_STRB_sync		<= I2C_RD_STRB;
--		end if;
--	end process;	
--
--
--
--     process( sys_clk , rst )
--       begin
--         if ( rst = '1' ) then
--				SDA_OUT			<= '1';
--				SCL				<= '1';
--				I2C_BUSY 		<= '0';
--				I2C_bit_cnt 	<= 7;
--				SCL_CNT			<= 0;
--				BYTE_CNT			<= ( others => '0' );
--				I2C_ack			<= '1';
--				I2C_addr 		<= ( others => '0' );
--				I2C_DOUT			<= ( others => '0' );
--				I2C_data			<= ( others => '0' );
--				I2C_RD_WR		<= '0';
--				I2C_STATE 		<= s_idle;				
--				I2C_DOUT_T 		<= ( others => '0' );
--
--         elsif rising_edge( sys_clk ) then
--	        case I2C_STATE is
--           ----------------------
--           when s_idle =>
--				I2C_busy 		<= '0';
--				SDA_OUT	 		<= '1';
--				SCL				<= '1';
--				I2C_bit_cnt 	<= 7;
--				SCL_CNT			<= 0;
--				BYTE_CNT			<= ( others => '0' );
--				if 	(I2C_RD_STRB_sync = '1' ) then
--					I2C_RD_WR		<= '1';
--					I2C_busy 		<= '1';
--					I2C_addr			<= I2C_DEV_ADDR & '1';
--					I2C_STATE 		<= s_send_start;
--					I2C_DOUT_T 		<= ( others => '0' );
--				elsif(I2C_WR_STRB_sync = '1') then
--					I2C_RD_WR		<= '0';
--					I2C_busy 		<= '1';
--					I2C_addr			<= I2C_DEV_ADDR & '0';
--					I2C_data			<= I2C_ADDRESS;
--					I2C_STATE 		<= s_send_start;
--				else
--					I2C_STATE <= s_idle;
--				end if;
--           ----------------------
--           when s_send_start =>	
--					SDA_OUT	 	<= '0';
--					SCL			<= '1';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_send_start;
--					else  
--						SCL_CNT		<= 0;
--						SCL			<= '0';
--						I2C_STATE 	<= s_send_addr_1;
--					end if;
--          --####################
--          --## SEND DEV ADDRESS 
--          --####################
--	         when s_send_addr_1 =>	
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						SCL			<= '0';
--						I2C_STATE 	<= s_send_addr_1;
--					else  
--						SCL_CNT		<= 0;
--						SCL			<= '0';
--						SDA_OUT	 	<= I2C_addr(I2C_bit_cnt);
--						I2C_STATE 	<= s_send_addr_2;
--					end if;				
--	         when s_send_addr_2 =>	
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_send_addr_2;
--					else  
--						SCL_CNT		<= 0;
--						I2C_STATE 	<= s_send_addr_3;
--					end if;				
--					
--	         when s_send_addr_3 =>	
--            if (SCL_CNT < SCL_WIDTH*2 ) then
--              SCL				<= '1';
--              SCL_CNT		<= SCL_CNT + 1;
--              I2C_STATE 	<= s_send_addr_3;
--            else  
--              SCL_CNT		<= 0;             
--              if ( I2C_bit_cnt >= 1 ) then
--                I2C_bit_cnt 	<= I2C_bit_cnt - 1;
--                I2C_STATE 		<= s_send_addr_1;
--              else            
--                I2C_STATE 		<= s_addr_ack_1;                
--              end if;                                          
--            end if;					
--									
--			 --####################
--          --#### ACKNOWLEDGE ###
--          --####################
--          when s_addr_ack_1 =>
--			 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_addr_ack_1;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_STATE 	<= s_addr_ack_2;
--					end if;
--
--          when s_addr_ack_2 => 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_addr_ack_2;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_STATE 	<= s_addr_ack_3;
--					end if;
--          when s_addr_ack_3 => 
--					SCL			<= '1';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_addr_ack_3;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_ack		<= sda;
--						I2C_STATE 	<= s_addr_ack_4;
--					end if;
--          when s_addr_ack_4 => 
--						if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_addr_ack_4;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						SCL			<= '0';
--						IF (I2C_ack = '0') THEN
--							I2C_bit_cnt	<= 7;
--							if(I2C_RD_WR	= '0') then 
--								I2C_STATE 	<= s_WRTIE_DATA_1;
--							else
--								BYTE_CNT		<= x"1";
--								I2C_STATE 	<= S_READ_DATA_1;
--							end if;
--						else
--							SDA_OUT	 		<= '1';
--							SCL				<= '1';
--							I2C_STATE 		<= s_DONE;		
--						end if;
--	
--					end if;
--
--
--          --####################
--          --## SEND DATA 
--          --####################
--	         when s_WRTIE_DATA_1 =>	
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						SCL			<= '0';
--						I2C_STATE 	<= s_WRTIE_DATA_1;
--					else  
--						SCL_CNT		<= 0;
--						SCL			<= '0';
--						SDA_OUT	 	<= I2C_data(I2C_bit_cnt);
--						I2C_STATE 	<= s_WRTIE_DATA_2;
--					end if;				
--	         when s_WRTIE_DATA_2 =>	
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_WRTIE_DATA_2;
--					else  
--						SCL_CNT		<= 0;
--						I2C_STATE 	<= s_WRTIE_DATA_3;
--					end if;				
--					
--	         when s_WRTIE_DATA_3 =>	
--            if (SCL_CNT < SCL_WIDTH*2 ) then
--              SCL				<= '1';
--              SCL_CNT		<= SCL_CNT + 1;
--              I2C_STATE 	<= s_WRTIE_DATA_3;
--            else  
--              SCL_CNT		<= 0;             
--              if ( I2C_bit_cnt >= 1 ) then
--                I2C_bit_cnt 	<= I2C_bit_cnt - 1;
--                I2C_STATE 		<= s_WRTIE_DATA_1;
--              else            
--                I2C_STATE 		<= s_WRITE_ack_1;                
--              end if;                                          
--            end if;					
--								
--			 --####################
--          --#### ACKNOWLEDGE ###
--          --####################
--          when s_WRITE_ack_1 =>
--			 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_WRITE_ack_1;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_STATE 	<= s_WRITE_ack_2;
--					end if;
--
--          when s_WRITE_ack_2 => 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_WRITE_ack_2;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_STATE 	<= s_WRITE_ack_3;
--					end if;
--          when s_WRITE_ack_3 => 
--					SCL			<= '1';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_WRITE_ack_3;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_ack		<= sda;
--						I2C_STATE 	<= s_WRITE_ack_4;
--					end if;
--          when s_WRITE_ack_4 => 
--						if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_WRITE_ack_4;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						SCL			<= '0';
--						IF (I2C_ack = '0') THEN
--							BYTE_CNT	<= BYTE_CNT	 + 1;
--							IF(I2C_NUM_BYTES = BYTE_CNT) THEN
--								SDA_OUT	 	<= '0';
--								SCL			<= '1';
--								I2C_STATE 	<= S_I2C_STOP;	
--							ELSIF(BYTE_CNT	= X"0") THEN
--								I2C_data		<= I2C_DIN(7 DOWNTO 0);
--								I2C_STATE 	<= s_WRTIE_DATA_1;
--							ELSIF(BYTE_CNT	= X"1") THEN
--								I2C_data		<= I2C_DIN(15 DOWNTO 8);
--								I2C_STATE 	<= s_WRTIE_DATA_1;	
--							ELSIF(BYTE_CNT	= X"2") THEN
--								I2C_data		<= I2C_DIN(23 DOWNTO 16);
--								I2C_STATE 	<= s_WRTIE_DATA_1;
--							ELSIF(BYTE_CNT	= X"3") THEN
--								I2C_data		<= I2C_DIN(31 DOWNTO 24);
--								I2C_STATE 	<= s_WRTIE_DATA_1;
--							ELSE
--								SDA_OUT	 	<= '1';
--								SCL			<= '1';
--								I2C_STATE 	<= s_idle;	
--							END IF;	
--
--						else
--							SDA_OUT	 	<= '1';
--							SCL			<= '1';
--							I2C_STATE 	<= s_done;		
--						end if;
--	
--					end if;
--
--
--          --####################
--          --## READ DATA 
--          --####################
--
--
--        when S_READ_DATA_1 =>	 
--					SCL			<= '0';
--					SDA_OUT	 	<= '1';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_READ_DATA_1;
--					else  
--						SCL_CNT		<= 0;
--						I2C_STATE 	<= S_READ_DATA_2;
--					end if;
--          when S_READ_DATA_2 => 
--					SCL			<= '0';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_READ_DATA_2;
--					else  
--						SCL_CNT		<= 0;
--						I2C_STATE 	<= S_READ_DATA_3;
--					end if;
--          when S_READ_DATA_3 => 
--					SCL			<= '1';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_READ_DATA_3;
--					else  
--						SCL_CNT		<= 0;
--						I2C_data(I2C_bit_cnt)	<= SDA;
--						I2C_STATE 					<= S_READ_DATA_4;
--					end if;
--          when S_READ_DATA_4 => 
--						if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_READ_DATA_4;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						SCL			<= '0';
--	              if ( I2C_bit_cnt >= 1 ) then
--							I2C_bit_cnt 	<= I2C_bit_cnt - 1;
--							I2C_STATE 		<= S_READ_DATA_1;
--						else            
--							I2C_STATE <= s_READ_ack_1;                
--						end if;                                		
--					end if;
--
--
--			 --####################
--          --#### ACKNOWLEDGE ###
--          --####################
--          when s_READ_ack_1 =>			 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_READ_ack_1;
--					else  
--						SCL_CNT		<= 0;
--						IF((I2C_NUM_BYTES <= X"1") OR (I2C_NUM_BYTES = BYTE_CNT)) THEN
--							SDA_OUT	 	<= '1';
--						else
--							SDA_OUT	 	<= '0';
--						end if;
--						IF(BYTE_CNT	= X"1") THEN
--							I2C_DOUT_T(7 DOWNTO 0)			<= I2C_data;
--						ELSIF(BYTE_CNT	= X"2") THEN
--							I2C_DOUT_T(15 DOWNTO 8)			<= I2C_data;
--						ELSIF(BYTE_CNT	= X"3") THEN
--							I2C_DOUT_T(23 DOWNTO 16)		<= I2C_data;
--						ELSIF(BYTE_CNT	= X"4") THEN
--							I2C_DOUT_T(31 DOWNTO 24)		<= I2C_data;
--						ELSE
--							I2C_DOUT_T <= x"deadbeef";
--						END IF;	
--						I2C_STATE 	<=s_READ_ack_2;						
--					end if;
--          when s_READ_ack_2 => 
--					SCL			<= '0';
--					I2C_bit_cnt	<= 7;
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<=s_READ_ack_2;
--					else  
--						SCL_CNT		<= 0;
--						SCL			<= '1';
--						I2C_STATE 	<= s_READ_ack_3;
--					end if;
--          when s_READ_ack_3 => 
--					SCL			<= '1';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_READ_ack_3;
--					else  
--						SCL_CNT		<= 0;
--						I2C_STATE 	<= s_READ_ack_4;
--					end if;
--          when s_READ_ack_4 => 
--						if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= s_READ_ack_4;
--					else  
--						SDA_OUT	 	<= '1';
--						SCL_CNT		<= 0;
--						SCL			<= '0';
--						BYTE_CNT		<= BYTE_CNT	 + 1;
--						I2C_STATE 	<= S_READ_DATA_1;	
--						IF((I2C_NUM_BYTES <= X"1") OR (I2C_NUM_BYTES = BYTE_CNT)) THEN
--								I2C_STATE 	<= S_I2C_STOP;	
--								SCL_CNT		<= 0;
--						END IF;
--					end if;
--					
--				--######################
--          --######## STOP ########
--          --######################    
--
--				when S_I2C_STOP => 
--					I2C_DOUT		<= I2C_DOUT_T;
--					SCL			<= '0';
--					SDA_OUT	 	<= '0';
--					if (SCL_CNT < (SCL_WIDTH + SCL_WIDTH)) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_I2C_STOP ;
--					else  
--						SCL_CNT		<= 0;
--						SCL			<= '1';
--				--		SDA_OUT	 	<= '1';
--						I2C_STATE 	<= S_I2C_STOP_2;	
--					end if;	
--					
--				when S_I2C_STOP_2 => 
--					I2C_DOUT		<= I2C_DOUT_T;
--					SCL			<= '1';
--					SDA_OUT	 	<= '0';
--					if (SCL_CNT < SCL_WIDTH ) then
--						SCL_CNT		<= SCL_CNT + 1;
--						I2C_STATE 	<= S_I2C_STOP_2 ;
--					else  
--						SCL_CNT		<= 0;
--						SDA_OUT	 	<= '1';
--						I2C_STATE 	<= s_done;	
--					end if;	
--
--					
--				when s_done => 
--					I2C_busy 		<= '0';
--					SDA_OUT	 		<= '1';
--					SCL				<= '1';
--					I2C_bit_cnt 	<= 7;
--					SCL_CNT			<= 0;
--					BYTE_CNT			<= ( others => '0' );
--					if 	(I2C_RD_STRB_sync = '1' ) OR (I2C_WR_STRB_sync = '1') then
--						I2C_STATE 		<= s_done;
--					else
--						I2C_STATE <= s_idle;
--					end if;
--           when others => I2C_STATE <= s_idle;
--           end case;   
--         end if;
--       end process ;
--	
--
--
--	
--END behavior;

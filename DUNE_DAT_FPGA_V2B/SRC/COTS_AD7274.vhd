--------------------------------------------------------------------------------
--
--   FileName:         coldadc_i2c_master.vhd
--   Dependencies:     none
--   Brookhaven national Lab
--
--   Version History
--   Version 1.0 03/20/2019 JunbinZhang
--   Version 1.1 02/13/2023 Jack Fried

--------------------------------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;

ENTITY COTS_AD7274 IS
--  GENERIC(
--    input_clk : INTEGER := 100_000_000; --input clock speed from user logic in Hz
--    fsclk     : INTEGER := 48_000_000); --sampling fsclk 
  PORT(
    clk         : IN     STD_LOGIC;                    -- system clock 40MHz, can be used for sclk directly
    reset       : IN     STD_LOGIC;                    -- reset, active high reset
    start       : IN     STD_LOGIC;                    --

	 ADC_OUT     : OUT STD_LOGIC_VECTOR(11 downto 0);   -- data output 12 bit.
	 busy        : OUT STD_LOGIC;                       -- busy output
	 CSn         : OUT STD_LOGIC;                    	 -- 2.5V pin
	 SCLK        : OUT STD_LOGIC;                    	 -- 2.5V pin
	 SDATA       : IN  STD_LOGIC	                  	 -- 2.5V pin
	
);                   
END COTS_AD7274;


ARCHITECTURE logic OF COTS_AD7274 IS
  
  TYPE machine IS(IDLE, LEADZ1,LEADZ2, CONV,TAILZ1,TAILZ2, QUIT, DONE); --needed states
  SIGNAL state         : machine;                        --state machine
  signal sclk_ena      : std_logic;
  signal bit_cnt       : INTEGER RANGE 0 TO 15 := 0;      --tracks bit number in transaction
  signal	 rdy			  : STD_LOGIC; 	                   -- ready
  signal	 DATA_OUT	  :STD_LOGIC_VECTOR(11 downto 0);   -- data output 12-bit
  
  
  signal start_s1       : STD_LOGIC; 
  signal start_s2       : STD_LOGIC; 
  
  
  --signal busy          : std_logic;
BEGIN  
  
  
   process(clk)
   begin
	   if(clk'event and clk = '1') then
  
		start_s1	<= start;
		start_s2	<= start_s1;
  
      end if;
  end process; 
  
  
  
  SCLK <= clk when (sclk_ena='1') else '0';
  --state machine for Read out
  process(clk, reset)
  begin
      if(reset = '1') then
        state <= IDLE;
        CSn <= '1';
		  sclk_ena <= '0';
		  rdy <= '0';
		  bit_cnt <= 0;
		  DATA_OUT <= (others => '0');
		  busy <= '1';
      elsif(clk'event and clk = '1') then
         case state is 
				when IDLE =>
					--rdy <= '0';
					if(start_s2 = '1') then
						busy <= '1';
						CSn <= '0';
						sclk_ena <= '1';
						state <= LEADZ1;
					else
						busy <= '0';
						CSn <= '1';
						sclk_ena <= '0';
						state <= IDLE;
					end if;
				when LEADZ1 =>         --
					state <= LEADZ2;
				when LEADZ2 =>         --2 leading zeros
					state <= CONV;
				when CONV =>
					if (bit_cnt > 11) then
						bit_cnt <= 0;
						rdy <= '1';
						state <= TAILZ1;
					else
						DATA_OUT(11-bit_cnt)<= SDATA;
						bit_cnt <= bit_cnt + 1;
						state <= CONV;						
					end if;
				when TAILZ1 =>
					rdy <= '0';
					state <= TAILZ2;
				when TAILZ2 =>        --2 tailing zeros
						state <= QUIT;
						CSn <= '1';
						sclk_ena <= '0';					
					
				when QUIT =>
					if(bit_cnt < 2) then
						state <= QUIT;
						bit_cnt <= bit_cnt + 1;
					else
						bit_cnt <= 0;
						state <= DONE;
						busy <= '0';
					end if;
					
				when DONE =>
					if(start_s2 = '1') then
						state <= DONE;
					else
						state <= IDLE;
					end if;
					
				when others => state <= IDLE;                        
			end case;
      end if;
  end process; 
  
  
  process(clk, reset)
  begin
		if(reset = '1') then
			ADC_OUT <= (others => '0');
		elsif(clk'event and clk = '1') then
			if(rdy = '1') then
				ADC_OUT <= DATA_OUT;
			end if;
		end if;
  end process;
END logic;

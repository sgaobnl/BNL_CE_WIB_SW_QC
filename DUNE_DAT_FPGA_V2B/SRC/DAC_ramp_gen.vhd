library ieee;
use ieee.std_logic_1164.all;
--USE ieee.std_logic_arith.all;
--USE ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

entity DAC_ramp_gen is
	port 
	(		
		clk						: IN STD_LOGIC; 
		reset					: IN STD_LOGIC;
		enable					: IN STD_LOGIC; 
		delay					: IN STD_LOGIC_VECTOR(7 downto 0);	
		counter_out				: OUT STD_LOGIC_VECTOR(15 downto 0);	
		start_out				: OUT STD_LOGIC 
	);
end DAC_ramp_gen;

architecture Behavioral of DAC_ramp_gen is

type state_t is (IDLE, PROGRAM, WAITING); --DONE??
signal state : state_t;

--sync signals
signal enable_s1, enable_s2 : std_logic;
signal adc_counter : unsigned(15 downto 0);
signal delay_s : unsigned(7 downto 0);
signal delay_counter : unsigned(7 downto 0);
constant dac_programming_delay : unsigned(7 downto 0) := x"1B"; 

begin


sync: process(clk)
begin
   if(clk'event and clk = '1') then

	enable_s1	<= enable;
	enable_s2	<= enable_s1;
	delay_s		<= unsigned(delay) - 1;
	if (unsigned(delay) = x"00") then --prevent 0 -> FF
		delay_s <= x"00";
	end if;
  end if;
end process sync; 

state_mchn: process(clk, reset)
begin
	if(reset = '1') then 
  
		state <= IDLE;
		adc_counter <= x"0000";
		start_out <= '0';
		delay_counter <= x"00";
		--should I set DACs to 0??
		
	elsif(clk'event and clk = '1') then	
		counter_out <= std_logic_vector(adc_counter);
		
		case state is
			when IDLE =>

				start_out <= '0';
				delay_counter <= x"00";
				adc_counter <= x"0000";
				if (enable_s2 = '1') then								
					state <= PROGRAM;
				else
					state <= IDLE;					
				end if;
			when PROGRAM =>
				if (delay_counter = x"00") then
					start_out <= '1';
					state <= PROGRAM;
				elsif (delay_counter >= dac_programming_delay) then
					start_out <= '0';
					state <= WAITING;
				else
					start_out <= '0';
					state <= PROGRAM;
				end if;
				delay_counter <= delay_counter + 1;
				
			when WAITING =>
				if (delay_counter >= delay_s) then 
					delay_counter <= x"00";
					if (enable_s2 = '1') then
						adc_counter <= adc_counter + 1; 
						state <= PROGRAM;					
					else
						adc_counter <= x"0000";					
						state <= IDLE;
					end if;
				else
					delay_counter <= delay_counter + 1;
					--adc_counter <= adc_counter; --?
					state <= WAITING;
				end if;
				
				start_out <= '0';
		end case;
	end if;
end process state_mchn;

end Behavioral;
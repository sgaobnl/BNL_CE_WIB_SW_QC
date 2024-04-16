LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.numeric_std.all;
--USE ieee.std_logic_arith.all;
--USE ieee.std_logic_unsigned.all;

ENTITY signal_delayer IS

PORT
(
	clk		: in std_logic;
	sig1_i	: in std_logic;
	sig2_i	: in std_logic;
	sig1_o	: out std_logic;
	sig2_o	: out std_logic;
	
	delay1	: in std_logic_vector(5 downto 0) := "000000";
	delay2	: in std_logic_vector(5 downto 0) := "000000"
);
END signal_delayer;
	
ARCHITECTURE Behavioral OF signal_delayer IS

signal delay1_pipe : std_logic_vector(63 downto 0);
signal delay2_pipe : std_logic_vector(63 downto 0);

begin

delay1_pipe(0) <= sig1_i;
delay2_pipe(0) <= sig2_i;

delay_gen: for i in 1 to 63 generate
	process(clk)
	begin	
		if(clk'event and clk = '1') then
			delay1_pipe(i) <= delay1_pipe(i-1);
			delay2_pipe(i) <= delay2_pipe(i-1);
		end if;	
	end process;
end generate delay_gen;

sig1_o <= delay1_pipe(to_integer(unsigned(delay1)));
sig2_o <= delay2_pipe(to_integer(unsigned(delay2)));

end Behavioral;	
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
ENTITY version_reg IS
    PORT (
        data_out    : OUT STD_LOGIC_VECTOR(11 downto 0);
        Date_s      : OUT STD_LOGIC_VECTOR(31 downto 0);   -- YEAR MONTH DAY
        Time_s      : OUT STD_LOGIC_VECTOR(23 downto 0)   -- Hour MIN SEC
      );
END version_reg;
ARCHITECTURE rtl OF version_reg IS
BEGIN
    data_out <= X"299";
    Date_s <= X"20240731";
    Time_s <= X"160544";     
END rtl;

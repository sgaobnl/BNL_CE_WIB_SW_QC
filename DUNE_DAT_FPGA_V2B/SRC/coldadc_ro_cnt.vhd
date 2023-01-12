--------------------------------------------------------------------------------
--
--   FileName:         coldadc_i2c_master.vhd
--   Dependencies:     none
--   Brookhaven national Lab
--
--   Version History
--   Version 1.0 03/20/2019 JunbinZhang
-- 
--------------------------------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;

ENTITY COLDADC_RO_CNT IS
  PORT(
    clk     : IN     STD_LOGIC;  
    reset       : IN     STD_LOGIC;                    -- reset, active high reset
    ro_in       : IN     STD_LOGIC;  
    ro_cnt     : OUT STD_LOGIC_VECTOR(31 downto 0) 
);                   
END COLDADC_RO_CNT;


ARCHITECTURE logic OF COLDADC_RO_CNT IS
  
  signal ro_cnt_reg	  :STD_LOGIC_VECTOR(31 downto 0);  
  signal s1_cnt_reg	  :STD_LOGIC_VECTOR(31 downto 0);  
  signal s1_reg	  :STD_LOGIC;  
  signal s1_reg_1r	  :STD_LOGIC;  
  signal s1_reg_2r	  :STD_LOGIC;  
BEGIN  
  process(ro_in, reset)
  begin
      if(reset = '1') then
          ro_cnt_reg <=x"00000000";
          s1_reg_1r <= '0';
          s1_reg_2r <= '0';
      elsif(ro_in'event and ro_in = '1') then
		    s1_reg_1r <= s1_reg;
          s1_reg_2r <= s1_reg_1r;
          if (s1_reg_2r = '0') and (s1_reg_1r = '1') then
             ro_cnt_reg <=x"00000000";
          elsif (s1_reg_2r = '1') and (s1_reg_1r = '0') then
             ro_cnt <= ro_cnt_reg;
          else
             ro_cnt_reg <= ro_cnt_reg + 1;
          end if;
      end if;
  end process; 
 
  process(clk, reset)
  begin
      if(reset = '1') then
          s1_cnt_reg <=x"00000000";
      elsif(clk'event and clk = '1') then
          if s1_cnt_reg = x"0000007f" then
              s1_reg <= '1';
              s1_cnt_reg <= s1_cnt_reg + 1;
          elsif s1_cnt_reg >= x"05F5E17f" then
              s1_reg <= '0';
              s1_cnt_reg <=x"00000000";
          else
              s1_cnt_reg <= s1_cnt_reg + 1;
          end if;
      end if;
  end process; 
  
END logic;

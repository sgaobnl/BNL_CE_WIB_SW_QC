--------------------------------------------------------------------------------
--
--   FileName:         coldadc_i2c_master.vhd
--   Dependencies:     none
--   Brookhaven national Lab
--
--   Version History
--   Version 1.0 03/20/2019 JunbinZhang
--   Version 1.1 02/29/2024 Jillian Donohue - added input signal synchronization
--------------------------------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;

ENTITY CD_LOCK_CNT IS
  PORT(
    clk     : IN     STD_LOGIC; 
    reset       : IN     STD_LOGIC;                    -- reset, active high reset
    lock_in       : IN     STD_LOGIC;  
    lock_cnt     : OUT STD_LOGIC_VECTOR(3 downto 0) 
);                   
END CD_LOCK_CNT;


ARCHITECTURE logic OF CD_LOCK_CNT IS
  
  signal lock_cnt_reg	  :STD_LOGIC_VECTOR(3 downto 0);  
  signal lock_cnt_reg2	  :STD_LOGIC_VECTOR(3 downto 0);  
  
BEGIN  
  lock_counter : process(lock_in, reset) 
  begin
      if(reset = '1') then
          lock_cnt_reg <=x"0";
      elsif(lock_in'event and lock_in = '0') then --falling edge
          if lock_cnt_reg < x"f" then 
            lock_cnt_reg <= lock_cnt_reg + 1;
          end if;
      end if;
  end process lock_counter; 
 
  sync_counter : process(clk) --s1_cnt_reg counts to 1 second
  begin
      if(clk'event and clk = '1') then  --100mhz clock
          lock_cnt_reg2 <= lock_cnt_reg; 
          lock_cnt <= lock_cnt_reg2; 
      end if;
  end process sync_counter; 
  
END logic;

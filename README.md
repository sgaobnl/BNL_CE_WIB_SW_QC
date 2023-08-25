# Update WIB system time 
If powershell on windows machine is used as terminal. 
```
 $cdate = get-date
 $wibdate = "date -s '$cdate'"
ssh root@192.168.121.1  $wibdate
```

# Login WIB
open an terminal
```
ssh root@192.168.121.1
```
pwd: fpga

# BNL_CE_WIB_SW_QC
 
These scripts are developed for standalone WIB operation on WIB 

## Compile
```
find . -type f -exec touch {} +
(optional: if the computer time is wrong)
```

```
mkdir build
make
```
## Available scripts
#### 1. Set up PLL timing and I2C phase adjustment
```
python3 wib_startup.py
```
It adjusts the i2c phase by 300 steps

#### 2. Power on/off FEMBs (Optional, this step can be skipped )
```
python3 top_femb_powering.py <on/off> <on/off> <on/off> <on/off>
```
The four arguments correspond to the four slots 

e.g.  Turn FEMBs on WIB slot 0 and 1 on
```
python3 top_femb_powering.py on on off off 
```

#### 3. Data taking using PLL timing
```
python3 top_chkout_pls_fake_timing.py <slot lists> save <number of events>
```
e.g.   save 10 times of spy buffer for FEMBs on WIB slot 0 and 1
```
python3 top_chkout_pls_fake_timing.py 0 1 save 10 
```

#### 3. Data decoder at the server 
```
python3 rd_demo_raw_hermes.py <file_path/file_name>   
```
e.g.
```
python3 rd_demo_raw_hermes.py tmp_data/Raw_25_08_2023_14_22_54.bin
```
It is better to transfer the data to the server through scp command and then perform data analysis on the server side. 




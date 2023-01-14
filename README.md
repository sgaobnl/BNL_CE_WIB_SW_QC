# BNL_CE_WIB_SW_QC
 
These scripts are developed for standalone WIB operation on WIB at CERN

note: 

at CERN, the FEMBs are always on;

the DAQ doesn't reconfigure WIB for every run, so we need to reconfigure the WIB back to its start status

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
#### 3. FEMBs quick checkout
Generate a report that includes pulse response at 200 mV 14mV/fC 2us, power consumption, and ColdADC monitoring data

Use time master
```
python3 quick_checkout.py <slot lists> save <number of events>
```
e.g. take data from four fembs and record 10 events
```
python3 quick_checkout.py 0 1 2 3 save 10
```
#### 4. Data taking using PLL timing
```
python3 top_chkout_pls_fake_timing.py <slot lists> save <number of events>
```
#### 5. Data taking using the time master
```
python3 top_chkout_pls_ptc_timing.py <slot lists> save <number of events>
```
#### 6. Data decoder for 4. and 5.
```
python3 rd_demo_raw.py <file_path/file_name>   
```
e.g.
```
python3 rd_demo_raw.py tmp_data/Raw_19_06_2021_23_37_10.bin
```

## Run quick checkout test
#### step 0 (optional: only run if encounter i2c errors and use PLL clock)
```
python3 wib_startup.py
```
#### step 1: power on the FEMBs if they are off
```
python3 top_femb_powering.py <on/off> <on/off> <on/off> <on/off>
```
#### step 2: run the quick checkout test (use time master, can be changed to PLL clock)
```
python3 top_chkout_pls_fake_timing.py <slot lists> save <number of events>
```
#### step 3: check the reports, saved at reports/

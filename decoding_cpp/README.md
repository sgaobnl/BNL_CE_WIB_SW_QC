# Installing & using decoding_cpp

## WIB (Linux)
 1. root@dune-wib:~/BNL_CE_WIB_SW_QC/decoding_cpp# make
 2. root@dune-wib:~/BNL_CE_WIB_SW_QC# python3 rd_demo_dunedaq.py tmp_data/Raw_27_06_2021_05_49_53.bin 0
	 - You may need to transfer Python wheels of missing packages over to the WIB. 
		 1. Go to the package page on pypi.org (or another Python package distribution site).
		 2. In the “built distributions” section, look for a .whl file with “cp37” (Python 3.7), “linux”, and “aarch64” or “arm64” in it. Download it and transfer the file to the WIB.
		 3. python3 pip install wheel_file.whl
## Windows
 1. ...\BNL_CE_WIB_SW_QC\decoding_cpp>pip install -r requirements.txt
 2. ...\BNL_CE_WIB_SW_QC\decoding_cpp>python setup.py build --build-lib=./build
	 - There will be a lot of warnings, but it should be fine.
 3. ...\BNL_CE_WIB_SW_QC>python rd_demo_dunedaq.py tmp_data/Raw_27_06_2021_05_49_53.bin 0

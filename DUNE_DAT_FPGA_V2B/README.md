# DUNE_DAT_FPGA_V2B
This subfolder is the project folder for the DAT firmware. The main project file is DUNE_DAT_FPGA.qpf, the toplevel file is DUNE_DAT_FPGA.vhd, and the bitfile is output_files/DUNE_DAT_FPGA.sof. SOFs (SRAM Object File) have to be reprogrammed every time the FPGA power cycles. The DAT FPGA will also already be programmed with output_files/DUNE_DAT_FPGA_femb.pof (included for reference), which it will use on power-up before being programmed. The POF file has basic FEMB functionality.
To open the project, open DUNE_DAT_FPGA.qpf in Quartus Prime Standard Edition 17.1. See the main repo README for compilation and programming instructions.
## Firmware structure
You can view the overall file structure by selecting Hierarchy in the Project Navigator pane.

The top level consists of these sub entities:
 - Many pass-through signals to/from COLDATAs
 - Various PLLs
 - Reset manager
 - Register bank (see dat_sw/src/dat_util.h for mapping list)
	 - Socket select muxes & demuxes: Most components have 8 instances so the data written to or read from them would take up a lot of registers. Instead of creating a much larger register bank, I reserved a single register (SOCKET_RDOUT_SEL) indicating which socket you're referring to when you try to write to or read from a particular LArASIC or ADC's power monitor/monitoring ADC/etc. Registers that have multiplexers feeding into them or demultiplexers being fed by them are:
		 - FE/ADC INA226 read & write strobes (I2C address, write data, etc is also shared between the INA226 controllers)
		 - FE/ADC INA226 output data
		 - FE & ADC AD7274 busy flags
		 - FE & ADC AD7274 output data
		 - FE DAC data
		 - Ring oscillator counts
 - I2C slave to communicate with WIB
 - INA226 (power monitor) I2C controllers
 - AD7274 (Monitoring ADC) SPI controllers
 - AD5683R (DAC) SPI controllers
 - ADC Ring oscillator counters
 - Test pulse generator
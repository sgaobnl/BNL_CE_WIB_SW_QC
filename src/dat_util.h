extern "C" {
	
//DAT
//8-bit register index in DAT FPGA

//See also firmware README: https://github.com/jdonohue-bnl/bnl-dat-fw-sw/blob/main/DUNE_DAT_FPGA_V2B/README.md

	extern constexpr uint8_t DAT_CD_CONFIG				= 1;
	extern constexpr uint8_t DAT_CD1_CONTROL			= 2;
	extern constexpr uint8_t DAT_CD2_CONTROL			= 3;
	extern constexpr uint8_t DAT_SOCKET_SEL				= 4;
	//INA226 Power Monitors
	extern constexpr uint8_t DAT_INA226_REG_ADDR		= 5;
	extern constexpr uint8_t DAT_INA226_DEVICE_ADDR		= 6; //7 bits max
	extern constexpr uint8_t DAT_INA226_NUM_BYTES		= 7; //4 bits max
	extern constexpr uint8_t DAT_INA226_DIN_MSB			= 8; 
	extern constexpr uint8_t DAT_INA226_DIN_LSB			= 9; // this order appears to contradict firmware but it's correct
													// according to how i2c_master.vhd currently operates
	extern constexpr uint8_t DAT_INA226_STRB			= 10; //see fw for bit details
	extern constexpr uint8_t DAT_INA226_CD1_DOUT_MSB	= 11; //see DIN_LSB note^
	extern constexpr uint8_t DAT_INA226_CD1_DOUT_LSB	= 12;
	extern constexpr uint8_t DAT_INA226_CD2_DOUT_MSB	= 13;
	extern constexpr uint8_t DAT_INA226_CD2_DOUT_LSB	= 14;
	extern constexpr uint8_t DAT_INA226_FE_DOUT_MSB		= 15;
	extern constexpr uint8_t DAT_INA226_FE_DOUT_LSB		= 16;
	
	//AD7274 Monitoring ADCs
	extern constexpr uint8_t DAT_MONADC_START			= 17; //a '1' triggers all ADCs to start a conversion	
	
	extern constexpr uint8_t DAT_CD1_MONADC_DATA_LSB		= 18;
	extern constexpr uint8_t DAT_CD1_MONADC_DATA_MSB_BUSY	= 19; //msBit of this is the busy flag, ls4 bits are the 4 msbits of data
	extern constexpr uint8_t DAT_CD2_MONADC_DATA_LSB		= 20;
	extern constexpr uint8_t DAT_CD2_MONADC_DATA_MSB_BUSY	= 21; //msBit of this is the busy flag, ls4 bits are the 4 msbits of data	
	extern constexpr uint8_t DAT_ADC_MONADC_DATA_LSB		= 22;
	extern constexpr uint8_t DAT_ADC_MONADC_DATA_MSB_BUSY	= 23; //msBit of this is the busy flag, ls4 bits are the 4 msbits of data
	extern constexpr uint8_t DAT_FE_MONADC_DATA_LSB			= 24;
	extern constexpr uint8_t DAT_FE_MONADC_DATA_MSB_BUSY	= 25; //msBit of this is the busy flag, ls4 bits are the 4 msbits of data
	
	//Muxes and switches
	extern constexpr uint8_t DAT_CD_AMON_SEL				= 26;
	extern constexpr uint8_t DAT_ADC_FE_TEST_SEL			= 27;
	extern constexpr uint8_t DAT_ADC_TEST_SEL_INHIBIT		= 28;
	extern constexpr uint8_t DAT_FE_TEST_SEL_INHIBIT		= 29;
	extern constexpr uint8_t DAT_FE_IN_TST_SEL_LSB			= 30;
	extern constexpr uint8_t DAT_FE_IN_TST_SEL_MSB			= 31;
	extern constexpr uint8_t DAT_FE_CALI_CS					= 32;
	extern constexpr uint8_t DAT_ADC_TST_SEL				= 33;
	extern constexpr uint8_t DAT_ADC_SRC_CS_P_LSB			= 34; //currently not implemented in fw
	extern constexpr uint8_t DAT_ADC_SRC_CS_P_MSB			= 35; // ^
	extern constexpr uint8_t DAT_ADC_PN_TST_SEL				= 36;
	extern constexpr uint8_t DAT_ADC_TEST_IN_SEL			= 37;
	extern constexpr uint8_t DAT_EXT_PULSE_CNTL				= 38;
	
	//AD5683R DACs
	extern constexpr uint8_t DAT_FE_DAC_TP_SET				= 39; //writing 0x1<<X triggers DAC[X] (0 to 7)
	extern constexpr uint8_t DAT_FE_DAC_TP_DATA_LSB			= 40; 
	extern constexpr uint8_t DAT_FE_DAC_TP_DATA_MSB			= 41;
	extern constexpr uint8_t DAT_DAC_OTHER_SET				= 42; //0x1 triggers DAC_ADC_P, 0x2 (0x1<<1) triggers DAC_ADC_N,
																  //0x4 (0x1<<2) triggers DAC_TP
	extern constexpr uint8_t DAT_DAC_ADC_P_DATA_LSB			= 43;	
	extern constexpr uint8_t DAT_DAC_ADC_P_DATA_MSB			= 44;
	extern constexpr uint8_t DAT_DAC_ADC_N_DATA_LSB			= 45;	
	extern constexpr uint8_t DAT_DAC_ADC_N_DATA_MSB			= 46;
	extern constexpr uint8_t DAT_DAC_TP_DATA_LSB			= 47;
	extern constexpr uint8_t DAT_DAC_TP_DATA_MSB			= 48;
	
	
	extern constexpr uint8_t DAT_ADC_RING_OSC_COUNT_B0		= 49;
	extern constexpr uint8_t DAT_ADC_RING_OSC_COUNT_B1		= 50;
	extern constexpr uint8_t DAT_ADC_RING_OSC_COUNT_B2		= 51;
	extern constexpr uint8_t DAT_ADC_RING_OSC_COUNT_B3		= 52;
	
	extern constexpr uint8_t DAT_ADC_POR_NAND				= 53;
	extern constexpr uint8_t DAT_ADC_CHIP_ACTIVE			= 54;
		
	//TEST PULSE GEN
	extern constexpr uint8_t DAT_TEST_PULSE_EN				= 55; 	//bit 0 = FPGA_TP_EN, 1 = ASIC_TP_EN, 
																	    //2 = INT_TP_EN (FPGA or ASIC pulse), 3 = EXT_TP_EN (WIB pulse)
	extern constexpr uint8_t DAT_TEST_PULSE_SOCKET_EN		= 56; //enable test pulse for each socket
	extern constexpr uint8_t DAT_TEST_PULSE_WIDTH_LSB		= 57; 
	extern constexpr uint8_t DAT_TEST_PULSE_WIDTH_MSB		= 58; 
	extern constexpr uint8_t DAT_TEST_PULSE_DELAY			= 59;
	extern constexpr uint8_t DAT_TEST_PULSE_PERIOD_LSB		= 60; 	
	extern constexpr uint8_t DAT_TEST_PULSE_PERIOD_MSB		= 61; 
	extern constexpr uint8_t DAT_FE_CMN_SEL		     	= 62;
	extern constexpr uint8_t DAT_MISC_IO    			= 63;
	
	
/////INA226 Internal register map
	extern constexpr uint8_t DAT_INA226_CONFIG			= 0x0;
	extern constexpr uint8_t DAT_INA226_SHUNT_V			= 0x1;
	extern constexpr uint8_t DAT_INA226_BUS_V			= 0x2;
	extern constexpr uint8_t DAT_INA226_POWER			= 0x3;
	extern constexpr uint8_t DAT_INA226_CURRENT			= 0x4;
	extern constexpr uint8_t DAT_INA226_CALIB			= 0x5;
	extern constexpr uint8_t DAT_INA226_MASK_ENABLE		= 0x6;
	extern constexpr uint8_t DAT_INA226_ALERT_LIM		= 0x7;
	extern constexpr uint8_t DAT_INA226_MANUF_ID		= 0xFE;
	extern constexpr uint8_t DAT_INA226_DIE_ID			= 0xFF;
	
	void datpower_poke(uint8_t dev_addr, uint8_t reg_addr, uint16_t data, uint8_t cd, uint8_t fe);
	uint16_t datpower_peek(uint8_t dev_addr, uint8_t reg_addr, uint8_t cd, uint8_t fe);
	
	double datpower_getvoltage(uint8_t addr, uint8_t cd, uint8_t fe);
	double datpower_getcurrent(uint8_t addr, uint8_t cd, uint8_t fe);
	
	void dat_monadc_trigger();
	bool dat_monadc_busy(uint8_t cd, uint8_t adc, uint8_t fe);
	uint16_t dat_monadc_getdata(uint8_t cd, uint8_t adc, uint8_t fe);
	
	//void dat_set_dac(float val, uint8_t fe, uint8_t adc, uint8_t fe_cal);
	void dat_set_dac(uint16_t val, uint8_t fe, uint8_t adc, uint8_t fe_cal);
	void dat_set_pulse(uint8_t en, uint16_t period, uint16_t width, float amplitude);
}

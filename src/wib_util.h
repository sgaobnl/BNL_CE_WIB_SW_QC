

extern "C" {	
#include "io_reg.h"

///////////////FROM WIB.H:

	//Selectable I2C busses for /dev/i2c-0
	constexpr uint8_t I2C_SI5344            = 0;
	constexpr uint8_t I2C_SI5342            = 1;
	constexpr uint8_t I2C_QSFP              = 2;
	constexpr uint8_t I2C_PL_FEMB_PWR       = 3;
	constexpr uint8_t I2C_PL_FEMB_EN        = 4;
	constexpr uint8_t I2C_SENSOR            = 5;
	constexpr uint8_t I2C_PL_FEMB_PWR2      = 6;
	constexpr uint8_t I2C_LTC2977           = 7;
	constexpr uint8_t I2C_PL_FEMB_PWR3      = 8;
	constexpr uint8_t I2C_FLASH             = 9;
	constexpr uint8_t I2C_ADN2814           = 10;

	//Memory base addresses of AXI interfaces
	constexpr size_t CTRL_REGS              = 0xA00C0000;
	//constexpr size_t DAQ_SPY_0              = 0xA0100000;
	//constexpr size_t DAQ_SPY_1              = 0xA0200000;
	constexpr size_t DAQ_HISTOGRAM 				 = 0xA00C8000; /// <- ADC QC firmware
	constexpr size_t DAQ_SPY_FEMB0_CD0           = 0x440000000; ///new fw, these replace DAQ_SPY_0
	constexpr size_t DAQ_SPY_FEMB0_CD1           = 0x440100000; ///and DAQ_SPY_1
	constexpr size_t DAQ_SPY_FEMB1_CD0           = 0x440200000;
	constexpr size_t DAQ_SPY_FEMB1_CD1           = 0x440300000;
	constexpr size_t DAQ_SPY_FEMB2_CD0           = 0x440400000;
	constexpr size_t DAQ_SPY_FEMB2_CD1           = 0x440500000;
	constexpr size_t DAQ_SPY_FEMB3_CD0           = 0x440600000;
	constexpr size_t DAQ_SPY_FEMB3_CD1           = 0x440700000;
	
	

	//32bit register index in CTRL_REGS
	constexpr size_t REG_TIMING             = 0x0000/4;
	constexpr size_t REG_FW_CTRL            = 0x0004/4;
	constexpr size_t REG_FAKE_TIME_CTRL     = 0x000C/4;
	constexpr size_t REG_TIMING_CMD_0       = 0x0010/4;
	constexpr size_t REG_TIMING_CMD_1       = 0x0014/4;
	constexpr size_t REG_FAKE_TIME_L        = 0x0018/4;
	constexpr size_t REG_FAKE_TIME_H        = 0x001C/4;
	constexpr size_t REG_DAQ_SPY_REC        = 0x0024/4;
	constexpr size_t REG_FELIX_CTRL         = 0x0038/4;
	constexpr size_t REG_DAQ_SPY_STATUS     = 0x0080/4;
	constexpr size_t REG_FW_TIMESTAMP       = 0x0088/4;
	constexpr size_t REG_BACKPLANE_ADDR     = 0x008C/4;
	constexpr size_t REG_ENDPOINT_STATUS    = 0x0090/4;

	//Size of a DAQ spy buffer
	//constexpr size_t DAQ_SPY_SIZE           = 0x00100000;
	constexpr size_t DAQ_SPY_SIZE           	 = 0x40000; ///new fw, replaces old DAQ_SPY_SIZE
	constexpr size_t HIST_MEM_SIZE				 = 0x8000; /// <- ADC QC firmware

	////////////FROM FEMB_3ASIC.H:

	// Fast Command AXI registers
	constexpr uint32_t REG_FAST_CMD_CODE       = 0x0000/4;
	constexpr uint32_t REG_FAST_CMD_ACT_DELAY  = 0x0004/4;

	// COLDATA I2C AXI registers
	constexpr uint32_t REG_COLD_I2C_START      = 0x0000/4;
	constexpr uint32_t REG_COLD_I2C_CTRL       = 0x0004/4;

	// Fast Command bits
	constexpr uint8_t FAST_CMD_RESET    = 1;
	constexpr uint8_t FAST_CMD_ACT      = 2;
	constexpr uint8_t FAST_CMD_SYNC     = 4;
	constexpr uint8_t FAST_CMD_EDGE     = 8;
	constexpr uint8_t FAST_CMD_IDLE     = 16;
	constexpr uint8_t FAST_CMD_EDGE_ACT = 32;

	// Fast Command Act commands
	constexpr uint8_t ACT_IDLE              = 0x00;
	constexpr uint8_t ACT_LARASIC_PULSE     = 0x01;
	constexpr uint8_t ACT_SAVE_TIME         = 0x02;
	constexpr uint8_t ACT_SAVE_STATUS       = 0x03;
	constexpr uint8_t ACT_CLEAR_SAVE        = 0x04;
	constexpr uint8_t ACT_RESET_COLDADC     = 0x05;
	constexpr uint8_t ACT_RESET_LARASIC     = 0x06;
	constexpr uint8_t ACT_RESET_LARASIC_SPI = 0x07;
	constexpr uint8_t ACT_PROGRAM_LARASIC   = 0x08;

	// COLDATA I2C control bit packing scheme
	constexpr uint32_t COLD_I2C_CHIP_ADDR   = 23; //4 // 0x07800000;
	constexpr uint32_t COLD_I2C_REG_PAGE    = 20; //3 // 0x00700000;
	constexpr uint32_t COLD_I2C_RW          = 19; //1 // 0x00080000;
	constexpr uint32_t COLD_I2C_ACK1        = 18; //1 // 0x00040000;
	constexpr uint32_t COLD_I2C_REG_ADDR    = 10; //8 // 0x0003FC00;
	constexpr uint32_t COLD_I2C_ACK2        =  9; //1 // 0x00000200;
	constexpr uint32_t COLD_I2C_DATA        =  1; //8 // 0x000001FE;
	constexpr uint32_t COLD_I2C_ACK3        =  0; //1 // 0x00000001;

	// COLDATA I2C delay
	constexpr uint32_t COLD_I2C_DELAY = 60; //microseconds
	
	//io_reg_t coldata_i2c[8];
	
	////////////////FROM FEMB_3ASIC.CC:
	constexpr size_t CD_I2C_ADDR[] = { 0xA0010000, 0xA0040000, 0xA0050000, 0xA0060000, 0xA0070000, 0xA0080000, 0xA0090000, 0xA00A0000 };

	// for all coldata chips
	constexpr size_t CD_FASTCMD_ADDR = 0xA0030000;
	static io_reg_t coldata_fast_cmd;

	//NEW FUNCTIONS:
	uint32_t peek(size_t addr);
	void poke(size_t addr, uint32_t value);

	uint32_t wib_peek(size_t addr);
	void wib_poke(size_t addr, uint32_t value);

    uint8_t cdpeek(uint8_t femb_idx,  uint8_t chip_addr, uint8_t reg_page, uint8_t reg_addr);
	
    void cdpoke(uint8_t femb_idx, uint8_t chip_addr, uint8_t reg_page, uint8_t reg_addr, uint8_t data);
	
	uint8_t i2cread(uint8_t bus, uint8_t chip, uint8_t reg);
	void i2cwrite(uint8_t bus, uint8_t chip, uint8_t reg, uint8_t data);
	void i2cselect(uint8_t device);	
	
	void bufread(char* dest, size_t buf_num);
	
	//sensors
	double read_ltc2990(uint8_t slave, bool differential, uint8_t ch);
	double read_ltc2991(uint8_t bus, uint8_t slave, bool differential, uint8_t ch);
	double read_ad7414(uint8_t slave);
	double read_ltc2499(uint8_t ch);
    double read_ina226_c(uint8_t slave);
    double read_ina226_v(uint8_t slave);

    bool femb_power_reg_ctrl(uint8_t femb_id, uint8_t regulator_id, double voltage);
    bool femb_power_config(uint8_t femb_id, double dc2dc_o1, double dc2dc_o2, double dc2dc_o3, double dc2dc_o4 ); //, double ldo_a0, double ldo_a1);
    bool all_femb_bias_ctrl(bool bias   );
    bool femb_power_en_ctrl(int femb_id, uint8_t dc2dco1, uint8_t dc2dco2, uint8_t dc2dco3, uint8_t dc2dco4, uint8_t bias  );

	bool script_cmd(char* line);
	//bool script(char* script, bool file=true);
} 

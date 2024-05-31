extern "C" {
#include <stdio.h>
#include <stdint.h>

#include "dat_util.h"
#include "wib_util.h"

void datpower_poke(uint8_t dev_addr, uint8_t reg_addr, uint16_t data, uint8_t cd, uint8_t fe) {
	if (cd > 1 && fe > 7) {		
		printf("datpower_poke: Either cd (0 or 1) or fe (0-7) must be specified. cd=%d, fe=%d\n", cd, fe); //CD has priority if both are >= 0
		return;
	}

	
	
	// printf("cd = 0x%x, fe = 0x%x, dev_addr = 0x%x, reg_addr = 0x%x, data = 0x%x\n", cd, fe, dev_addr, reg_addr, data);
	
	if (cd > 1) cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, fe); 
	

	cdpoke(0, 0xC, 0, DAT_INA226_DEVICE_ADDR, dev_addr); 
	cdpoke(0, 0xC, 0, DAT_INA226_NUM_BYTES, 0x2); 
	cdpoke(0, 0xC, 0, DAT_INA226_REG_ADDR, reg_addr); 
	uint8_t data_msb = (data & 0xFF00) >> 8;
	uint8_t data_lsb = data & 0xFF;
	cdpoke(0, 0xC, 0, DAT_INA226_DIN_MSB, data_msb); 
	cdpoke(0, 0xC, 0, DAT_INA226_DIN_LSB, data_lsb); 
	
	uint8_t strb = 0x1; //I2C_WR_STRB
	if (cd == 1) strb = strb << 2;//0x4
	else if (fe <= 7) strb = strb << 4;//0x10
	// printf("Strobing 0x%x\n",strb);
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, strb); 
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, 0x0); 
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, 0x0); 
}

uint16_t datpower_peek(uint8_t dev_addr, uint8_t reg_addr, uint8_t cd, uint8_t fe) {
	if (cd > 1 && fe > 7) {
		printf("datpower_peek: Either cd (0 or 1) or fe (0-7) must be specified\n"); //CD has priority if both are >= 0
		return (uint16_t)(-1);
	}	
	// printf("cd = 0x%x, fe = 0x%x, dev_addr = 0x%x, reg_addr = 0x%x\n", cd, fe, dev_addr, reg_addr);
	
	if (cd > 1) cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, fe);
	
	cdpoke(0, 0xC, 0, DAT_INA226_DEVICE_ADDR, dev_addr); 
	cdpoke(0, 0xC, 0, DAT_INA226_NUM_BYTES, 0x2); 
	cdpoke(0, 0xC, 0, DAT_INA226_REG_ADDR, reg_addr); 

	uint8_t strb = 0x2; //I2C_RD_STRB
	if (cd == 1) strb = strb << 2;//0x8
	else if (fe <= 7) strb = strb << 4;//0x20
	// printf("Strobing 0x%x\n",strb);
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, strb); 
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, 0x0); 
	cdpoke(0, 0xC, 0, DAT_INA226_STRB, 0x0); 
	
	uint8_t dout_msb_reg;
	if (cd == 0) dout_msb_reg = DAT_INA226_CD1_DOUT_MSB;
	if (cd == 1) dout_msb_reg = DAT_INA226_CD2_DOUT_MSB;
	else if (fe <= 7) dout_msb_reg = DAT_INA226_FE_DOUT_MSB;
	uint8_t rd_msb = cdpeek(0, 0XC, 0, dout_msb_reg); 
	uint8_t rd_lsb = cdpeek(0, 0XC, 0, dout_msb_reg + 1); 
	
	uint16_t rd_reg = (rd_msb << 8) | rd_lsb;
	return rd_reg;
}

double datpower_getvoltage(uint8_t addr, uint8_t cd, uint8_t fe) {
	double V_LSB = 1.25e-3;
	double I_LSB = 0.01e-3; //amps
	double R = 0.1; //ohms
	double cal = 0.00512/(I_LSB*R);
	char name[3];
	

	//Write calibration reg
	datpower_poke(addr, DAT_INA226_CALIB, int(cal), cd, fe);
	//Write config reg
	datpower_poke(addr, DAT_INA226_CONFIG, 0x41FF, cd, fe);
	//wait till conversion is completed
	datpower_poke(addr, DAT_INA226_MASK_ENABLE, 0x0, cd, fe); //poke in order to peek
	int ready = 0x0;
	for (int i = 0; i < 20 && ready != 0x8; i++) {
		int reg = datpower_peek(addr, DAT_INA226_MASK_ENABLE, cd, fe);
		ready = reg & 0x8;
		// print(hex(reg))
	}
	if (ready != 0x8) printf("datpower_getvoltage: %s %d addr 0x%x timed out checking for CVRF", (cd <= 1)? "CD":"FE", (cd <= 1)? cd:fe, addr);            
		// reg_addr_reg = wib.cdpeek(0, 0XC, 0, DAT_INA226_REG_ADDR)
		// print("DAT_INA226_REG_ADDR =",hex(reg_addr_reg))
	//Read Bus voltage, Current, Power (need to poke first in order to read)
	datpower_poke(addr, DAT_INA226_BUS_V, 0xAAAA, cd, fe);
	uint16_t bus_voltage_reg = datpower_peek(addr, DAT_INA226_BUS_V, cd, fe);
	return bus_voltage_reg*V_LSB;

	// datpower_poke(addr, DAT_INA226_CURRENT, 0xAAAA, cd, fe)
	// current_reg = datpower_peek(addr, DAT_INA226_CURRENT, cd, fe)
	// current = current_reg*I_LSB 

	// datpower_poke(addr, DAT_INA226_POWER, 0xAAAA, cd, fe)
	// power_reg = datpower_peek(addr, DAT_INA226_POWER, cd, fe)
	// power = power_reg*25*I_LSB 

	// print (cd_name[cd], name[i], "Bus V (V)=",  bus_voltage, "V", hex(bus_voltage_reg)) //0x40 nominal vals: 1.19 V
	// print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  //9.2 mA
	// print("Power (mW)=",  power*1e+3, "mW", hex(power_reg), '\n')                          //11 mW
	//CD_VDDA_P - Datasheet voltage says 1.1 V - So all good

}

double datpower_getcurrent(uint8_t addr, uint8_t cd, uint8_t fe) {
	double V_LSB = 1.25e-3;
	double I_LSB = 0.01e-3; //amps
	double R = 0.1; //ohms
	double cal = 0.00512/(I_LSB*R);
	char name[3];
	

	//Write calibration reg
	datpower_poke(addr, DAT_INA226_CALIB, int(cal), cd, fe);
	//Write config reg
	datpower_poke(addr, DAT_INA226_CONFIG, 0x41FF, cd, fe);
	//wait till conversion is completed
	datpower_poke(addr, DAT_INA226_MASK_ENABLE, 0x0, cd, fe); //poke in order to peek
	int ready = 0x0;
	for (int i = 0; i < 20 && ready != 0x8; i++) {
		int reg = datpower_peek(addr, DAT_INA226_MASK_ENABLE, cd, fe);
		ready = reg & 0x8;
		// print(hex(reg))
	}
	if (ready != 0x8) printf("datpower_getcurrent: %s %d addr 0x%x timed out checking for CVRF", (cd <= 1)? "CD":"FE", (cd <= 1)? cd:fe, addr);            
		// reg_addr_reg = wib.cdpeek(0, 0XC, 0, DAT_INA226_REG_ADDR)
		// print("DAT_INA226_REG_ADDR =",hex(reg_addr_reg))
	//Read Bus voltage, Current, Power (need to poke first in order to read)
	// datpower_poke(addr, DAT_INA226_BUS_V, 0xAAAA, cd, fe);
	// uint16_t bus_voltage_reg = datpower_peek(addr, DAT_INA226_BUS_V, cd, fe);
	// return bus_voltage_reg*V_LSB;

	datpower_poke(addr, DAT_INA226_CURRENT, 0xAAAA, cd, fe);
	//uint16_t current_reg = datpower_peek(addr, DAT_INA226_CURRENT, cd, fe);
	int16_t current_reg = datpower_peek(addr, DAT_INA226_CURRENT, cd, fe);
	return current_reg*I_LSB;
}	

void dat_monadc_trigger() {
	cdpoke(0, 0xC, 0, DAT_MONADC_START, 1);
	cdpoke(0, 0xC, 0, DAT_MONADC_START, 0);
}


bool dat_monadc_busy(uint8_t cd, uint8_t adc, uint8_t fe) {
	uint8_t busy_reg;
	if (cd == 0) busy_reg = DAT_CD1_MONADC_DATA_MSB_BUSY;
	else if (cd == 1) busy_reg = DAT_CD2_MONADC_DATA_MSB_BUSY;
	else if (adc <= 7) {
		busy_reg = DAT_ADC_MONADC_DATA_MSB_BUSY;		
		cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, adc);
	} else if (fe <= 7) {
		busy_reg = DAT_FE_MONADC_DATA_MSB_BUSY;
		cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, fe);
	} else {
		printf("dat_monadc_busy: no valid arguments.\nValid arguments: cd 0 or 1, adc 0-7, fe 0-7. cd = %d, adc = %d, fe = %d\n", cd, adc, fe);
		return false;
	}
	
	
	return cdpeek(0, 0xC, 0, busy_reg) & 0x80;
}

uint16_t dat_monadc_getdata(uint8_t cd, uint8_t adc, uint8_t fe) {
	uint8_t msb_reg, lsb_reg;
	if (cd == 0) {
		msb_reg = DAT_CD1_MONADC_DATA_MSB_BUSY;
		lsb_reg = DAT_CD1_MONADC_DATA_LSB;
	} else if (cd == 1) {
		msb_reg = DAT_CD2_MONADC_DATA_MSB_BUSY;
		lsb_reg = DAT_CD2_MONADC_DATA_LSB;
	} else if (adc <= 7) {
		msb_reg = DAT_ADC_MONADC_DATA_MSB_BUSY;
		lsb_reg = DAT_ADC_MONADC_DATA_LSB;
		
		cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, adc);
	} else if (fe <= 7) {
		msb_reg = DAT_FE_MONADC_DATA_MSB_BUSY;
		lsb_reg = DAT_FE_MONADC_DATA_LSB;
		
		cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, fe);
	} else {
		printf("dat_monadc_getdata: no valid arguments.\nValid arguments: cd 0 or 1, adc 0-7, fe 0-7. cd = %d, adc = %d, fe = %d\n", cd, adc, fe);
		return (uint16_t)(-1);
	}

	
	return ((cdpeek(0, 0xC, 0, msb_reg) & 0x7F) << 8) | cdpeek(0, 0xC, 0, lsb_reg);
}

//void dat_set_dac(float val, uint8_t fe, uint8_t adc, uint8_t fe_cal) {
void dat_set_dac(uint16_t val, uint8_t fe, uint8_t adc, uint8_t fe_cal) {
	//uint16_t val_int = (uint16_t)(val*65536/2.5);
	uint16_t val_int = val;
	uint8_t dac_lsb = val_int & 0xFF;
	uint8_t dac_msb = (val_int & 0xFF00) >> 8; 
	uint8_t msb_reg, lsb_reg, set_reg;
	uint8_t set_val = 0x1;
	
	if ((fe <= 7) && (fe >= 0)) {
		msb_reg = DAT_FE_DAC_TP_DATA_MSB;
		lsb_reg = DAT_FE_DAC_TP_DATA_LSB;
		set_reg = DAT_FE_DAC_TP_SET;
		set_val = set_val << fe;
		
		cdpoke(0, 0xC, 0, DAT_SOCKET_SEL, fe);
	} else if (adc == 0) { //ADC_P
		msb_reg = DAT_DAC_ADC_P_DATA_MSB;
		lsb_reg = DAT_DAC_ADC_P_DATA_LSB;
		set_reg = DAT_DAC_OTHER_SET;
		set_val = set_val << 0;
	} else if (adc == 1) { //ADC_N
		msb_reg = DAT_DAC_ADC_N_DATA_MSB;
		lsb_reg = DAT_DAC_ADC_N_DATA_LSB;
		set_reg = DAT_DAC_OTHER_SET;
		set_val = set_val << 1;
	} else if (fe_cal == 0) {
		msb_reg = DAT_DAC_TP_DATA_MSB;
		lsb_reg = DAT_DAC_TP_DATA_LSB;
		set_reg = DAT_DAC_OTHER_SET;
		set_val = set_val << 2;		
	} else {
		printf("dat_set_dac: no valid arguments.\nValid arguments: fe 0-7, adc 0 or 1, fe_cal 0. fe = %d, adc = %d, fe_cal = %d\n", fe, adc, fe_cal);
		return;
	}
	
	cdpoke(0, 0xC, 0, lsb_reg, dac_lsb);
	cdpoke(0, 0xC, 0, msb_reg, dac_msb);	
	
	cdpoke(0, 0xC, 0, set_reg, set_val);
	cdpoke(0, 0xC, 0, set_reg, 0x0);
}

void dat_set_pulse(uint8_t en, uint16_t period, uint16_t width, float amplitude) {
//en[0]=1 enables pulser for ASIC 0
	
	//program in period & width 
	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_PERIOD_LSB, period&0xFF);
	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_PERIOD_MSB, (period&0xFF00)>>8);	
	
	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_WIDTH_LSB, width&0xFF);
	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_WIDTH_MSB, (width&0xFF00)>>8);

	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_DELAY, 0x0); //delay not relevant if you're not using ASIC_DAC_CNTL
	
	//program DACs with amplitude and turn them on (only those being used)
	for(int i = 0; i < 8; i++) {
		if (en & 1<<i > 0) dat_set_dac(amplitude, i, -1, -1);
		else dat_set_dac(0.0, i, -1, -1);
	}
	//finally enable pulses
	cdpoke(0, 0xC, 0, DAT_TEST_PULSE_SOCKET_EN, en);
	
	if (en > 0) cdpoke(0, 0xC, 0, DAT_TEST_PULSE_EN, 0x7); //turn on FPGA_TP_EN, ASIC_TP_EN, INT_TP_EN
	else cdpoke(0, 0xC, 0, DAT_TEST_PULSE_EN, 0x0);
}


}

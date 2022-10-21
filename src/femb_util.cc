#include "femb_util.h"

#include "wib_util.h"

bool femb_power_reg_ctrl(uint8_t femb_id, uint8_t regulator_id, double voltage) {
    uint8_t chip;
    uint8_t reg;
    uint8_t buffer[2];
    uint32_t DAC_value;

	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");

    switch (regulator_id) {
        case 0:
        case 1:
        case 2:
        case 3:
            i2cselect(I2C_PL_FEMB_PWR2);   // SET I2C mux to 0x06 for FEMB DC2DC DAC access
            DAC_value   = (uint32_t) ((voltage * -482.47267) + 2407.15);
            reg         = (uint8_t) (0x10 | ((regulator_id & 0x0f) << 1));
            buffer[0]   = (uint8_t) (DAC_value >> 4) & 0xff;
            buffer[1]   = (uint8_t) (DAC_value << 4) & 0xf0;
            switch(femb_id) {
                case 0:
                    chip = 0x4C;
                    break;
                case 1:
                    chip = 0x4D;
                    break;
                case 2:
                    chip = 0x4E;
                    break;
                case 3:
                    chip = 0x4F;
                    break;
                default:
                    return false;
            }
            break;
        case 4:
            i2cselect(I2C_PL_FEMB_PWR3);   // SET I2C mux to 0x08 for FEMB LDO DAC access
            chip = 0x4C;
            reg  = (0x10 | ((femb_id & 0x0f) << 1));
            DAC_value   = (uint32_t) ((voltage * -819.9871877) + 2705.465);
            buffer[0]   = (uint8_t) (DAC_value >> 4) & 0xff;
            buffer[1]   = (uint8_t) (DAC_value << 4) & 0xf0;
            break;
        case 5:
            i2cselect(I2C_PL_FEMB_PWR3);   // SET I2C mux to 0x08 for FEMB LDO DAC access
            chip = 0x4D;
            reg  = (0x10 | ((femb_id & 0x0f) << 1));
            DAC_value   = (uint32_t) ((voltage * -819.9871877) + 2705.465);
            buffer[0]   = (uint8_t) (DAC_value >> 4) & 0xff;
            buffer[1]   = (uint8_t) (DAC_value << 4) & 0xf0;
            break;
        default:
            printf("femb_power_reg_ctrl: Unknown regulator_id\n");
			return false;
    }


	i2c_block_write(&i2c_bus,chip,reg,buffer,2);
//	printf("Debug femb_power_reg_ctrl:\n");
//	printf("Wrote values 0x%x and 0x%x\n",buffer[0],buffer[1]);
//	i2c_block_read(&i2c_bus,chip,reg,buffer,2);
//	printf("Read back values 0x%x and 0x%x\n",buffer[0],buffer[1]);
	i2c_free(&i2c_bus);
    return true;
}

void femb_power_en_ctrl(int femb_idx, uint8_t port_en) {
    //PWR_BIAS_EN enabled if any FEMB regulator is ON


    if (port_en != 0x0) {//if (port_en != 0x0 || frontend_power[0] || frontend_power[1] || frontend_power[2] || frontend_power[3]) {
        if (i2cread(pwr, 0x22, 0x5) != 0x1) {
            i2cwrite(pwr, 0x22, 0x5, 0x1);
            usleep(100000);
        }
    } else {
        if (i2cread(pwr, 0x22, 0x5) != 0x0) {
            i2cwrite(pwr, 0x22, 0x5, 0x0);
            usleep(100000);
        }
    }
    uint8_t i2c_addr;
    uint8_t i2c_reg;
    switch (femb_idx) {
        case 0:
            i2c_addr = 0x23;
            i2c_reg = 0x4;
            break;
        case 1:
            i2c_addr = 0x23;
            i2c_reg = 0x5;
            break;
        case 2:
            i2c_addr = 0x23;
            i2c_reg = 0x6;
            break;
        case 3:
            i2c_addr = 0x22;
            i2c_reg = 0x4;
            break;
        default:
            return;
    }
    i2cwrite(pwr, i2c_addr, i2c_reg, port_en);
    usleep(100000);
	//printf("Debug femb_power_en_ctrl:\n");
	//printf("i2cread(pwr, 0x22, 0x5) = 0x%x\n",i2cread(pwr, 0x22, 0x5));
	//printf("i2cread(pwr, 0x%x, 0x%x)= 0x%x\n",i2c_addr, i2c_reg,i2cread(pwr, i2c_addr, i2c_reg));
    //frontend_power[femb_idx] = port_en != 0; // FEMB is "ON" if any regulators are ON
    return;//return true;
}

bool femb_power_config(double dc2dc_o1, double dc2dc_o2, double dc2dc_o3, double dc2dc_o4, double ldo_a0, double ldo_a1) {
	bool success = true;
    for (int i = 0; i <= 3; i++) {
        success &= femb_power_reg_ctrl(i, 0, dc2dc_o1); //dc2dc_O1
        success &= femb_power_reg_ctrl(i, 1, dc2dc_o2); //dc2dc_O2
        success &= femb_power_reg_ctrl(i, 2, dc2dc_o3); //dc2dc_O2
        success &= femb_power_reg_ctrl(i, 3, dc2dc_o4); //dc2dc_O2
        success &= femb_power_reg_ctrl(i, 4, ldo_a0); //ldo_A0
        success &= femb_power_reg_ctrl(i, 5, ldo_a1); //ldo_A1
    }


    // configure all pins as outputs for regulator enablers
    i2cwrite(pwr, 0x23, 0xC, 0);
    i2cwrite(pwr, 0x23, 0xD, 0);
    i2cwrite(pwr, 0x23, 0xE, 0);
    i2cwrite(pwr, 0x22, 0xC, 0);
    i2cwrite(pwr, 0x22, 0xD, 0);
    i2cwrite(pwr, 0x22, 0xE, 0);


    return success;
}

/* bool reset_frontend() {
    bool success = true;
    printf("Disabling front end power\n");
    femb_power_en_ctrl(0,0x0);
    femb_power_en_ctrl(1,0x0);
    femb_power_en_ctrl(2,0x0);
    femb_power_en_ctrl(3,0x0);
    femb_power_config();
    if (!pll_initialized) {
        success &= reset_timing_endpoint();
    }
    femb_rx_mask(0xFFFF); //all disabled
    printf("Resetting FEMB receiver\n");
    femb_rx_reset();
    if (!felix_initialized) {
        printf("Resetting FELIX transmitter\n");
        felix_tx_reset();
    }
    frontend_initialized = true;
    return success;
} */


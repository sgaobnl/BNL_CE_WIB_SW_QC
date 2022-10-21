extern "C" {

#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/i2c.h>

bool femb_power_reg_ctrl(uint8_t femb_id, uint8_t regulator_id, double voltage);
void femb_power_en_ctrl(int femb_idx, uint8_t port_en);
bool femb_power_config(double dc2dc_o1, double dc2dc_o2, double dc2dc_o3, double dc2dc_o4, double ldo_a0, double ldo_a1);
}

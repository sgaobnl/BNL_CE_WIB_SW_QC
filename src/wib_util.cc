
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

#include "wib_util.h"
#include "wib_i2c.h"
#include "sensors.h"
#include "io_reg.h"

#include <linux/i2c-dev.h>
#include <i2c/smbus.h>


//functions
uint32_t peek(size_t addr) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;

    int fd = open("/dev/mem",O_RDWR|O_SYNC);	
	
	void *ptr = mmap(NULL,sysconf(_SC_PAGESIZE),PROT_READ|PROT_WRITE,MAP_SHARED,fd, page_addr);
    close(fd);
	if (ptr == MAP_FAILED) 
        return -1; //otherwise mmap will segfault
	
	uint32_t val = *((uint32_t*)((char*)ptr+page_offset));
    munmap(ptr,sysconf(_SC_PAGESIZE));
	
	//printf("Register 0x%016X was read as 0x%08X\n",addr,val);

	return val;
}

void poke(size_t addr, uint32_t val) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;

    int fd = open("/dev/mem",O_RDWR);
    void *ptr = mmap(NULL,sysconf(_SC_PAGESIZE),PROT_READ|PROT_WRITE,MAP_SHARED,fd, page_addr);
	close(fd);//"After mmap() call has returned, fd can be closed immediately without invalidating the mapping.
	
	if (ptr == MAP_FAILED) return;
    *((uint32_t*)((char*)ptr+page_offset)) = val;
    
    munmap(ptr,sysconf(_SC_PAGESIZE));
//	printf("Register 0x%016X was set to 0x%08X\n",addr,val);
}

uint32_t wib_peek(size_t addr) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;
    io_reg_t wib_reg;
	io_reg_init(&wib_reg, page_addr ,0x10000/4);
    uint32_t val =io_reg_read(&wib_reg, page_offset/4);
    io_reg_free(&wib_reg);
	return val;
}

void wib_poke(size_t addr, uint32_t val) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;
    io_reg_t wib_reg;
	io_reg_init(&wib_reg, page_addr ,0x10000/4);
    uint32_t mask = 0xFFFFFFFF;
    io_reg_write(&wib_reg, page_offset/4, val, mask);
    io_reg_free(&wib_reg);
}

uint8_t cdpeek(uint8_t femb_idx, uint8_t chip_addr, uint8_t reg_page, uint8_t reg_addr) {
    uint8_t coldata_idx = 0;
	//init io_reg each time- see FEMB_3ASIC::FEMB_3ASIC(int _index)
	io_reg_t coldata_i2c;
	io_reg_init(&coldata_i2c,CD_I2C_ADDR[coldata_idx+femb_idx*2],2);
	
	//see FEMB_3ASIC::i2c_read
    uint32_t ctrl = ((chip_addr & 0xF) << COLD_I2C_CHIP_ADDR)
                  | ((reg_page & 0x7) << COLD_I2C_REG_PAGE)
                  | (0x1 << COLD_I2C_RW)
                  | ((reg_addr & 0xFF) << COLD_I2C_REG_ADDR);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_CTRL,ctrl);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_START,1);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_START,0);
	usleep(COLD_I2C_DELAY);
	ctrl = io_reg_read(&coldata_i2c,REG_COLD_I2C_CTRL);
	
	//delete io_reg - see FEMB_3ASIC::~FEMB_3ASIC
	io_reg_free(&coldata_i2c);

//  printf("femb:%i coldata:%i chip:0x%02X page:0x%02X reg:0x%02X -> 0x%02X\n",femb_idx,coldata_idx,chip_addr,reg_page,reg_addr,(ctrl >> COLD_I2C_DATA) & 0xFF);	
	return (ctrl >> COLD_I2C_DATA) & 0xFF;
}

void cdpoke(uint8_t femb_idx, uint8_t chip_addr, uint8_t reg_page, uint8_t reg_addr, uint8_t data) {
    uint8_t coldata_idx = 0;
	//init io_reg each time- see FEMB_3ASIC::FEMB_3ASIC(int _index)
	io_reg_t coldata_i2c;
	io_reg_init(&coldata_i2c,CD_I2C_ADDR[coldata_idx+femb_idx*2],2);
	
    uint32_t ctrl = ((chip_addr & 0xF) << COLD_I2C_CHIP_ADDR)
                  | ((reg_page & 0x7) << COLD_I2C_REG_PAGE)
                  | (0x0 << COLD_I2C_RW)
                  | ((reg_addr & 0xFF) << COLD_I2C_REG_ADDR)
                  | ((data & 0xFF) << COLD_I2C_DATA);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_CTRL,ctrl);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_START,1);
    io_reg_write(&coldata_i2c,REG_COLD_I2C_START,0);
    usleep(COLD_I2C_DELAY);	
	
	//delete io_reg - see FEMB_3ASIC::~FEMB_3ASIC
	io_reg_free(&coldata_i2c);
	
//  printf("femb:%i coldata:%i chip:0x%02X page:0x%02X reg:0x%02X <- 0x%02X\n",femb_idx,coldata_idx,chip_addr,reg_page,reg_addr,data);	
}		

void bufread(char* dest, size_t buf_num) {
	size_t daq_spy_addr;
	
	if (buf_num==0) daq_spy_addr = DAQ_SPY_0;
	else if (buf_num==1) daq_spy_addr = DAQ_SPY_1;
	else return;    
	
	//see WIB_upgrade::WIB_upgrade		
    int daq_spy_fd = open("/dev/mem",O_RDWR); // File descriptor for the daq spy mapped memory    
    void *daq_spy = mmap(NULL,DAQ_SPY_SIZE,PROT_READ,MAP_SHARED,daq_spy_fd,daq_spy_addr); // Pointer to the daq spy firmware buffers
	
	close(daq_spy_fd); //"After mmap() call has returned, fd can be closed immediately without invalidating the mapping.
	if (daq_spy == MAP_FAILED) return; //mmap failed
	
	memcpy(dest, daq_spy, DAQ_SPY_SIZE);
	
	munmap(daq_spy,DAQ_SPY_SIZE); 
}

uint8_t i2cread(uint8_t bus, uint8_t chip, uint8_t reg) {
	i2c_t i2c_bus;
	bool fail;
	if (bus == 0) fail = i2c_init(&i2c_bus, (char*)"/dev/i2c-0"); //sel
	else if (bus == 2) fail = i2c_init(&i2c_bus,(char*)"/dev/i2c-2"); //pwr
	else {
		printf("Unknown bus %d. Accepted buses are 0 (sel) and 2 (pwr).\n",bus);
		return -1;
	}
	if (fail) printf("i2c_init failed\n");	
	
	uint8_t val;	
	for(int tries=0; tries<10; tries++) {
		val = i2c_reg_read(&i2c_bus, chip, reg);
		if (val >= 0) break;
		if (tries < 9) printf("Trying again... ");
		usleep(10000); //1 ms
	}
	//printf("bus:%d addr:0x%02X reg:0x%02X -> 0x%02X\n",bus,chip,reg,val);
	i2c_free(&i2c_bus);
	//For some reason WIB::~WIB() doesn't free pwr i2c bus, I assume this is intentional
	
	return val;
	
}
void i2cwrite(uint8_t bus, uint8_t chip, uint8_t reg, uint8_t data) {
	i2c_t i2c_bus;
	
	if (bus == 0) i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	else if (bus == 2) i2c_init(&i2c_bus,(char*)"/dev/i2c-2");
	else {
		printf("Unknown bus %d. Accepted buses are 0 (sel) and 2 (pwr).\n",bus);
		return;
	}

	i2c_reg_write(&i2c_bus, chip, reg, data);
	//printf("bus:%d addr:0x%02X reg:0x%02X <- 0x%02X\n",bus,chip,reg,data);	
	
	i2c_free(&i2c_bus);
	//For some reason WIB::~WIB() doesn't free pwr i2c bus, I assume this is intentional	
	
}

void i2cselect(uint8_t device) {
    uint32_t regaddr = 0xa00c0004;
    uint32_t next = peek(regaddr);
    next = (next & 0xFFFFFFF0) | (device & 0xF);
    poke(regaddr, next);
    //next = peek(regaddr);
    //printf ("reg=%08x, val=%08x\n",regaddr , next);
}

double read_ltc2990(uint8_t slave, bool differential, uint8_t ch) {	
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);
	
	//uint8_t buf[1] = {0x7};
	//i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater
	
	enable_ltc2990(&i2c_bus, slave, differential);//enable and trigger
	double voltage = 0.00030518*read_ltc2990_value(&i2c_bus,slave,ch);
	
	i2c_free(&i2c_bus);
	return voltage;
} 

double read_ltc2991(uint8_t bus, uint8_t slave, bool differential, uint8_t ch) { //ltc2991 are on 2 different buses
	i2c_t i2c_bus;
	if (bus == 0) i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	else if (bus == 2) i2c_init(&i2c_bus,(char*)"/dev/i2c-2");
	else {
		printf("read_ltc2991 Unknown bus %d. Accepted buses are 0 (sel) and 2 (pwr).\n",bus);
		return 0;
	}		

	enable_ltc2991(&i2c_bus, slave, differential);
	double voltage = 0.00030518*read_ltc2991_value(&i2c_bus,slave,ch);
	
	i2c_free(&i2c_bus);
	return voltage;
}

double read_ad7414(uint8_t slave) {
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);

	//uint8_t buf[1] = {0x7};
	//i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater

	double temp = read_ad7414_temp(&i2c_bus, slave);
	
	i2c_free(&i2c_bus);
	return temp;
}

double read_ina226_c(uint8_t slave) {
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);

	double val= read_ina226_vshunt(&i2c_bus, slave);
    val = val*(2.5e-6)/0.005;
	i2c_free(&i2c_bus);
	return val;
}

double read_ina226_v(uint8_t slave) {
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);

	double val= read_ina226_vbus(&i2c_bus, slave);
    val=val*1.25/1000;
	
	i2c_free(&i2c_bus);
	return val;
}

double read_ltc2499(uint8_t ch) {
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);

	//uint8_t buf[1] = {0x7};
	//i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater
	start_ltc2499_temp(&i2c_bus, ch);
	usleep(175000);
	double temp = read_ltc2499_temp(&i2c_bus, ch+1);
	usleep(175000);
	
	i2c_free(&i2c_bus);
	return temp;	
}

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
	        usleep(10000);
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
// not in V3A WIB
//        case 4:
//            i2cselect(I2C_PL_FEMB_PWR3);   // SET I2C mux to 0x08 for FEMB LDO DAC access
//            chip = 0x4C;
//            reg  = (0x10 | ((femb_id & 0x0f) << 1));
//            DAC_value   = (uint32_t) ((voltage * -819.9871877) + 2705.465);
//            buffer[0]   = (uint8_t) (DAC_value >> 4) & 0xff;
//            buffer[1]   = (uint8_t) (DAC_value << 4) & 0xf0;
//            break;
//        case 5:
//            i2cselect(I2C_PL_FEMB_PWR3);   // SET I2C mux to 0x08 for FEMB LDO DAC access
//            chip = 0x4D;
//            reg  = (0x10 | ((femb_id & 0x0f) << 1));
//            DAC_value   = (uint32_t) ((voltage * -819.9871877) + 2705.465);
//            buffer[0]   = (uint8_t) (DAC_value >> 4) & 0xff;
//            buffer[1]   = (uint8_t) (DAC_value << 4) & 0xf0;
//            break;
        default:
            printf("femb_power_reg_ctrl: Unknown regulator_id\n");
			return false;
    }
	i2c_block_write(&i2c_bus,chip,reg,buffer,2);
	i2c_free(&i2c_bus);
    return true;
}

bool femb_power_config(uint8_t femb_id, double dc2dc_o1, double dc2dc_o2, double dc2dc_o3, double dc2dc_o4 ) { //, double ldo_a0, double ldo_a1) {
	bool success = true;
    success &= femb_power_reg_ctrl(femb_id, 0, dc2dc_o1); //dc2dc_O1
    success &= femb_power_reg_ctrl(femb_id, 1, dc2dc_o2); //dc2dc_O2
    success &= femb_power_reg_ctrl(femb_id, 2, dc2dc_o3); //dc2dc_O2
    success &= femb_power_reg_ctrl(femb_id, 3, dc2dc_o4); //dc2dc_O2
    //success &= femb_power_reg_ctrl(femb_id, 4, ldo_a0); //ldo_A0
    //success &= femb_power_reg_ctrl(femb_id, 5, ldo_a1); //ldo_A1
    return success;
}

bool all_femb_bias_ctrl(bool bias   ) {
    uint8_t bus = 2;
    i2cwrite(bus, 0x23, 0xC, 0);
    i2cwrite(bus, 0x23, 0xD, 0);
    i2cwrite(bus, 0x23, 0xE, 0);
    i2cwrite(bus, 0x22, 0xC, 0);
    i2cwrite(bus, 0x22, 0xD, 0);
    i2cwrite(bus, 0x22, 0xE, 0);
    if (bias) { i2cwrite(bus, 0x22, 0x5, 0x1); }
    else {i2cwrite(bus, 0x22, 0x5, 0x0);}
    return true;
}

bool femb_power_en_ctrl(int femb_id, uint8_t dc2dco1, uint8_t dc2dco2, uint8_t dc2dco3, uint8_t dc2dco4, uint8_t bias  ) {
    uint8_t bus = 2;
    uint8_t reg_val;
    reg_val = (dc2dco1&0x01) + ((dc2dco2&0x01)<<1) + ((dc2dco3&0x01)<<2) + ((dc2dco4&0x01)<<3) + ((bias&0x01)<<6);
    uint8_t i2c_addr;
    uint8_t i2c_reg;
    switch (femb_id) {
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
            return false;
    }
    i2cwrite(bus, i2c_addr, i2c_reg, reg_val);
	int rd_val;	
    rd_val = i2cread(bus, i2c_addr, i2c_reg);
    usleep(100000);
    //printf ("%x, %x\n", reg_val, rd_val);
    if (rd_val != reg_val) {return false;}
    else {return true;}
}

bool script_cmd(char* line) {
	// printf("Printing line:%s",line);
	char* token = strtok(line, " \n");
	if (token == NULL or token[0] == '#') return true;
	
    if (not strcmp(token,"delay")) {
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments
            printf("Invalid delay\n");
            return false;
        }
        size_t micros = (size_t) strtoull(token,NULL,10);
        usleep(micros);
		//printf("slept %d micros\n",micros);
        return true;
    //} else if (not strcmp(token,"run")) {
	//	token = strtok(NULL," \n");
	//	if (token == NULL) { //no more arguments
    //        printf("Invalid run\n");
    //        return false;
    //    }
    //    return script(token);
    } else if (not strcmp(token,"i2c")) {
		char* bus = strtok(NULL," \n");
		bool res;
		if (token == NULL) { //no more arguments, strcmp has undefined behavior with NULL
            printf("Invalid i2c\n");
            return false;
        }        
        i2c_t i2c_bus;
        if (not strcmp(bus,"sel")) {  // i2c sel chip addr data [...]
            i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
        } else if (not strcmp(bus,"pwr")) { // i2c pwr chip addr data [...]
            i2c_init(&i2c_bus, (char*)"/dev/i2c-2");
        } else {
            printf("Invalid i2c bus selection: %s\n", bus);
            return false;
        }
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments
            printf("Invalid i2c\n");
            return false;
        }			
        uint8_t chip = (uint8_t)strtoull(token,NULL,16);
		
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments
            printf("Invalid i2c\n");
            return false;
        }						
        uint8_t addr = (uint8_t)strtoull(token,NULL,16);
		
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments
            printf("Invalid i2c\n");
            return false;
        }						
        uint8_t data = (uint8_t)strtoull(token,NULL,16);		
		
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments = single register to write            
			res = i2c_reg_write(&i2c_bus, chip, addr, data);
			//printf("res is %d\n",res);
            return (res > -1);		
		} else {			//rest of arguments are block of data to write
			uint8_t *buf = new uint8_t[32]; //max length of data that can be written
			buf[0] = data;
			size_t i;
			for (i = 1; i < 32 and token != NULL; i++) {
				buf[i] = (uint8_t)strtoull(token,NULL,16);
				token = strtok(NULL," \n");
			} 
            res = i2c_block_write(&i2c_bus, chip, addr, buf, i); //i is now = total number of data arguments
            //printf("res is %d\n",res);
			delete [] buf;
			return (res > -1);
		}			
		
		i2c_free(&i2c_bus);
    } else if (not strcmp(token,"mem")) {
		token = strtok(NULL," \n");
		if (token == NULL) { //no more arguments
            printf("Invalid arguments to mem\n");
            return false;
        }
		uint32_t addr = strtoull(token,NULL,16);
		
		token = strtok(NULL," ");
		if (token == NULL) { //no more arguments
            printf("Invalid arguments to mem\n");
            return false;
        }
		uint32_t value = strtoull(token,NULL,16);
		
		token = strtok(NULL," \n");
		if (token == NULL) { // mem addr value
			printf("poke 0x%x 0x%x\n",addr,value);
			poke(addr, value);
			return true;
		}
		else { // mem addr value mask
			uint32_t mask = strtoull(token,NULL,16);
            uint32_t prev = peek(addr);
            poke(addr, (prev & (~mask)) | (value & mask));
            return true;			
		}
				
    } else {
        printf("Invalid script command: %s\n", token);
    }
    return false;	
}


} 

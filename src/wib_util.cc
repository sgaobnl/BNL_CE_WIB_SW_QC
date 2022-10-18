
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


//functions
uint32_t peek(size_t addr) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;

    int fd = open("/dev/mem",O_RDWR|O_SYNC);	
	
	void *ptr = mmap(NULL,sysconf(_SC_PAGESIZE),PROT_READ|PROT_WRITE,MAP_SHARED,fd,(addr & ~(sysconf(_SC_PAGESIZE)-1)));
	if (ptr == MAP_FAILED) return -1; //otherwise mmap will segfault
	
	uint32_t val = *((uint32_t*)((char*)ptr+page_offset));
    munmap(ptr,sysconf(_SC_PAGESIZE));
    close(fd);
	
//	printf("Register 0x%016X was read as 0x%08X\n",addr,val);

	return val;
}

void poke(size_t addr, uint32_t val) {
    size_t page_addr = (addr & ~(sysconf(_SC_PAGESIZE)-1));
    size_t page_offset = addr-page_addr;

    int fd = open("/dev/mem",O_RDWR);
    void *ptr = mmap(NULL,sysconf(_SC_PAGESIZE),PROT_READ|PROT_WRITE,MAP_SHARED,fd,(addr & ~(sysconf(_SC_PAGESIZE)-1)));
	close(fd);//"After mmap() call has returned, fd can be closed immediately without invalidating the mapping.
	
	if (ptr == MAP_FAILED) return;
    *((uint32_t*)((char*)ptr+page_offset)) = val;
    
    munmap(ptr,sysconf(_SC_PAGESIZE));
//	printf("Register 0x%016X was set to 0x%08X\n",addr,val);
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

int i2cread(uint8_t bus, uint8_t chip, uint8_t reg) {
	i2c_t i2c_bus;
	bool fail;
	if (bus == 0) fail = i2c_init(&i2c_bus, (char*)"/dev/i2c-0"); //sel
	else if (bus == 2) fail = i2c_init(&i2c_bus,(char*)"/dev/i2c-2"); //pwr
	else {
		printf("Unknown bus %d. Accepted buses are 0 (sel) and 2 (pwr).\n",bus);
		return -1;
	}
	if (fail) printf("i2c_init failed\n");	
	
	int val;	
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
    uint32_t next = peek(REG_FW_CTRL);
    next = (next & 0xFFFFFFF0) | (device & 0xF);
    poke(REG_FW_CTRL,next);
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

double read_ltc2990(uint8_t slave, bool differential, uint8_t ch) {	
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);
	
	uint8_t buf[1] = {0x7};
	i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater
	
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

	uint8_t buf[1] = {0x7};
	i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater

	double temp = read_ad7414_temp(&i2c_bus, slave);
	
	i2c_free(&i2c_bus);
	return temp;
}

double read_ltc2499(uint8_t ch) {
	i2c_t i2c_bus;
	i2c_init(&i2c_bus, (char*)"/dev/i2c-0");
	i2cselect(I2C_SENSOR);

	uint8_t buf[1] = {0x7};
	i2c_write(&i2c_bus,0x70,buf,1);	 // enable i2c repeater

	start_ltc2499_temp(&i2c_bus, ch);
	usleep(175000);
	double temp = read_ltc2499_temp(&i2c_bus, ch+1);
	usleep(175000);
	
	i2c_free(&i2c_bus);
	return temp;	
}

} //extern "C"

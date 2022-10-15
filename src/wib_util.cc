
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

} 

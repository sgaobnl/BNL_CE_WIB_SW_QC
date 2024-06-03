WRKDIR=$(HOME)/BNL_CE_WIB_SW_QC-DAT_QC_HERMES/decoding_cpp
SRCS=$(WRKDIR)/rawdatautils/pybindsrc/module.cpp $(WRKDIR)/rawdatautils/pybindsrc/unpack.cpp $(WRKDIR)/rawdatautils/pybindsrc/TDEUnpacker.cpp $(WRKDIR)/rawdatautils/pybindsrc/WIB2Unpacker.cpp $(WRKDIR)/rawdatautils/pybindsrc/WIBEthUnpacker.cpp $(WRKDIR)/rawdatautils/pybindsrc/WIBUnpacker.cpp
OUTPUT=$(WRKDIR)/build/_daq_rawdatautils_py.so
CFLAGS=-O3 -Wall -shared -std=c++17 -fPIC
INCLUDE=-I$(WRKDIR)/detdataformats/include -I$(WRKDIR)/daqdataformats/include -I$(WRKDIR)/fddetdataformats/include -I$(WRKDIR)/rawdatautils/include -I$(WRKDIR)/Python-3.7.6 -I$(WRKDIR)/Python-3.7.6/Include -I/usr/include/python3.7m -I/usr/lib/python3.7/site-packages/pybind11/include

all: $(OUTPUT)

$(OUTPUT): $(SRCS)
	g++ -o $@ $(CFLAGS) $(INCLUDE) $^

util: src/wib_util.cc src/io_reg.cc src/wib_util.h src/io_reg.h
	g++ -O2 -shared -fPIC src/wib_util.cc src/io_reg.cc -o build/wib_util.so
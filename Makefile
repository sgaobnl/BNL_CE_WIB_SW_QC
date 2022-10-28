util: src/wib_util.cc src/io_reg.cc src/sensors.cc src/wib_i2c.cc src/wib_util.h src/io_reg.h src/wib_i2c.h src/sensors.h 
	g++ -O2 -shared -fPIC -li2c src/wib_util.cc src/io_reg.cc src/wib_i2c.cc src/sensors.cc -o build/wib_util.so

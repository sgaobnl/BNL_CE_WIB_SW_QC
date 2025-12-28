cmake_minimum_required(VERSION 3.12)
project(fddetdataformats VERSION 1.0.0)

find_package(daq-cmake REQUIRED)

daq_setup_environment()

find_package(detdataformats REQUIRED)
find_package(Boost COMPONENTS unit_test_framework REQUIRED)

##############################################################################

daq_add_library( LINK_LIBRARIES detdataformats::detdataformats) 

##############################################################################

daq_add_python_bindings(*.cpp LINK_LIBRARIES ${PROJECT_NAME} ) 

##############################################################################

daq_add_unit_test(WIBEthFrame_test LINK_LIBRARIES fddetdataformats) 
daq_add_unit_test(WIB2Frame_test   LINK_LIBRARIES fddetdataformats)
daq_add_unit_test(WIBFrame_test    LINK_LIBRARIES fddetdataformats)
daq_add_unit_test(TDE16Frame_test  LINK_LIBRARIES fddetdataformats)
daq_add_unit_test(DAPHNEFrame_test LINK_LIBRARIES fddetdataformats)

##############################################################################

daq_install()


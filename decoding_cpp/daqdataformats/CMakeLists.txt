
cmake_minimum_required(VERSION 3.12)
project(daqdataformats VERSION 3.5.1)

find_package(daq-cmake REQUIRED)

find_package(Boost COMPONENTS unit_test_framework REQUIRED)

daq_setup_environment()


##############################################################################
# Main library

daq_add_library(LINK_LIBRARIES)

##############################################################################
daq_add_python_bindings(*.cpp LINK_LIBRARIES ${PROJECT_NAME})

##############################################################################
# Plugins

##############################################################################
# Integration tests

##############################################################################
# Unit Tests
daq_add_unit_test(ComponentRequest_test        LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(Fragment_test                LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(FragmentHeader_test          LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(SourceID_test                   LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(TimeSlice_test           LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(TimeSliceHeader_test     LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(TriggerRecord_test           LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(TriggerRecordHeader_test     LINK_LIBRARIES ${PROJECT_NAME})
daq_add_unit_test(TriggerRecordHeaderData_test LINK_LIBRARIES ${PROJECT_NAME})

##############################################################################

daq_install()

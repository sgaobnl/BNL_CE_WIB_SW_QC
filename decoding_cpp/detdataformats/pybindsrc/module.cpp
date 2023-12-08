/**
 * @file module.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "registrators.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::detdataformats::python {

PYBIND11_MODULE(_daq_detdataformats_py, m) {

    m.doc() = "c++ implementation of the dunedaq detdataformats modules"; // optional module docstring

    register_detid(m);
    register_daqheader(m);
    register_daqethheader(m);
    register_hsi(m);

}

} // namespace dunedaq::detdataformats::python

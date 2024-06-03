/**
 * @file module.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "registrators.hpp"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

namespace dunedaq::fddetdataformats::python {

PYBIND11_MODULE(_daq_fddetdataformats_py, m)
{

  m.doc() = "C++ implementation of the fddetdataformats modules";

  register_wib(m);
  register_wib2(m);
  register_wibeth(m);
  register_daphne(m);
  register_ssp(m);
  register_tde(m);
}

} // namespace dunedaq::fddetdataformats::python

/**
 * @file registrators.hpp
 *
 * Declaration of functions to register Python bindings to C++ objects
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */


#ifndef FDDETDATAFORMATS_PYBINDSRC_REGISTRATORS_HPP_
#define FDDETDATAFORMATS_PYBINDSRC_REGISTRATORS_HPP_

#include <pybind11/pybind11.h>

namespace dunedaq::fddetdataformats::python {

  void register_wib2(pybind11::module&);
  void register_wibeth(pybind11::module&);
  void register_wib(pybind11::module&);
  void register_daphne(pybind11::module&);
  void register_ssp(pybind11::module&);
  void register_tde(pybind11::module&);
}

#endif // FDDETDATAFORMATS_PYBINDSRC_REGISTRATORS_HPP_

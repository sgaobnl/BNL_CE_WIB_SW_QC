/**
 * @file file_conversion.cpp Python bindings for file conversions between formats
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "rawdatautils/WIBtoWIB2.hpp"
#include "rawdatautils/WIBtoWIBEth.hpp"
#include "rawdatautils/WIBtoTDE.hpp"


#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq {
namespace rawdatautils {

namespace fc {
namespace python {

void
register_file_conversion(py::module& m)
{
  m.def("wib_hdf5_to_wib2_binary", &wib_hdf5_to_wib2_binary);
  m.def("wib_binary_to_wib2_binary", &wib_binary_to_wib2_binary);
  m.def("wib_hdf5_to_wibeth_binary", &wib_hdf5_to_wibeth_binary);
  m.def("wib_binary_to_wibeth_binary", &wib_binary_to_wibeth_binary);
  m.def("wib_hdf5_to_tde_binary", &wib_hdf5_to_tde_binary);
  m.def("wib_binary_to_tde_binary", &wib_binary_to_tde_binary);
}

} // namespace python
} // namespace file_conversion
} // namespace rawdatautils
} // namespace dunedaq

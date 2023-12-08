/**
 * @file tde.cpp Python bindings for the TDE16Frame format
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/TDE16Frame.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::fddetdataformats::python {

void
register_tde(py::module& m)
{

  py::class_<TDE16Frame>(m, "TDE16Frame", py::buffer_protocol())
    .def(py::init())
    .def(py::init([](py::capsule capsule) {
        auto wfp = *static_cast<TDE16Frame*>(capsule.get_pointer());
        return wfp;
    } ))
    .def(py::init([](py::bytes bytes){
      py::buffer_info info(py::buffer(bytes).request());
      auto wfp = *static_cast<TDE16Frame*>(info.ptr);
      return wfp;
    }))
    .def("get_timestamp", &TDE16Frame::get_timestamp)
    .def("set_timestamp", &TDE16Frame::set_timestamp)
    .def("get_channel", &TDE16Frame::get_channel)
    .def("get_daq_header", [](TDE16Frame& self) -> detdataformats::DAQEthHeader* {return self.get_daq_header();}, py::return_value_policy::reference_internal)
    .def("get_tde_header", [](TDE16Frame& self) -> TDEHeader* {return self.get_tde_header();}, py::return_value_policy::reference_internal)
    .def_static("sizeof", [](){ return sizeof(TDE16Frame); })
    .def("get_bytes",
         [](TDE16Frame* fr) -> py::bytes {
           return py::bytes(reinterpret_cast<char*>(fr), sizeof(TDE16Frame));
        }
    )
  ;

  py::class_<TDEHeader>(m, "TDEHeader")
    .def_property_readonly("channel", [](TDEHeader& self) -> uint16_t {return self.channel;})
    .def_property_readonly("version", [](TDEHeader& self) -> uint16_t {return self.version;})
    .def_property_readonly("tde_header", [](TDEHeader& self) -> uint16_t {return self.tde_header;})
    .def_property_readonly("tde_errors", [](TDEHeader& self) -> uint16_t {return self.tde_errors;})
    .def_property_readonly("TAItime", [](TDEHeader& self) -> uint64_t {return self.TAItime;})
  ;
}

} // namespace dunedaq::fddetdataformats::python

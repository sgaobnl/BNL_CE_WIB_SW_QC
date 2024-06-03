/**
 * @file hsi.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */
#include "detdataformats/HSIFrame.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::detdataformats::python {

void
register_hsi(py::module& m)
{

  py::class_<HSIFrame> (m, "HSIFrame", py::buffer_protocol())
    .def(py::init())
    .def(py::init([](py::capsule capsule) {
        auto hsfp = *static_cast<HSIFrame*>(capsule.get_pointer());
        return hsfp;
    } ))
    .def(py::init([](py::bytes bytes){
      py::buffer_info info(py::buffer(bytes).request());
      auto wfp = *static_cast<HSIFrame*>(info.ptr);
      return wfp;
    }))
    .def("get_timestamp", &HSIFrame::get_timestamp)
    .def_property_readonly("version", [](const HSIFrame& self) -> uint64_t {return self.version;})
    .def_property_readonly("detector_id", [](const HSIFrame& self) -> uint64_t {return self.detector_id;})
    .def_property_readonly("crate", [](const HSIFrame& self) -> uint64_t {return self.crate;})
    .def_property_readonly("slot", [](const HSIFrame& self) -> uint64_t {return self.slot;})
    .def_property_readonly("link", [](const HSIFrame& self) -> uint64_t {return self.link;})
    .def_property_readonly("input_low", [](const HSIFrame& self) -> uint64_t {return self.input_low;})
    .def_property_readonly("input_high", [](const HSIFrame& self) -> uint64_t {return self.input_high;})
    .def_property_readonly("trigger", [](const HSIFrame& self) -> uint64_t {return self.trigger;})
    .def_property_readonly("sequence", [](const HSIFrame& self) -> uint64_t {return self.sequence;})
  ;
}

} // namespace dunedaq::detdataformats::python

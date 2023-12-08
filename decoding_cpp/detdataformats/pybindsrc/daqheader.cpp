/**
 * @file detid.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "detdataformats/DAQHeader.hpp"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

namespace py = pybind11;

namespace dunedaq::detdataformats::python {

void register_daqheader(py::module& m) {

  py::class_<DAQHeader>(m, "DAQHeader", py::buffer_protocol())
    .def_property("version", 
      [](DAQHeader& self) -> uint32_t { return self.version; }, 
      [](DAQHeader& self, uint32_t version) { self.version = version; } 
      )
    .def_property("det_id", 
      [](DAQHeader& self) -> uint32_t { return self.det_id; }, 
      [](DAQHeader& self, uint32_t det_id) { self.det_id = det_id; } 
      )
    .def_property("crate_id", 
      [](DAQHeader& self) -> uint32_t { return self.crate_id; }, 
      [](DAQHeader& self, uint32_t crate_id) { self.crate_id = crate_id; } 
      )
    .def_property("slot_id", 
      [](DAQHeader& self) -> uint32_t { return self.slot_id; }, 
      [](DAQHeader& self, uint32_t slot_id) { self.slot_id = slot_id; } 
      )
    .def_property("link_id", 
      [](DAQHeader& self) -> uint32_t { return self.link_id; }, 
      [](DAQHeader& self, uint32_t link_id) { self.link_id = link_id; } 
      )
    .def("get_timestamp", &DAQHeader::get_timestamp)
    ;
}

}  // namespace dunedaq::detdataformats::python

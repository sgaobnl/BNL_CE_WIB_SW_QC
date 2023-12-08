/**
 * @file detid.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "detdataformats/DAQEthHeader.hpp"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

namespace py = pybind11;

namespace dunedaq::detdataformats::python {

void register_daqethheader(py::module& m) {

  py::class_<DAQEthHeader>(m, "DAQEthHeader", py::buffer_protocol())
    .def_property("version", 
      [](DAQEthHeader& self) -> uint32_t { return self.version; }, 
      [](DAQEthHeader& self, uint32_t version) { self.version = version; } 
      )
    .def_property("det_id", 
      [](DAQEthHeader& self) -> uint32_t { return self.det_id; }, 
      [](DAQEthHeader& self, uint32_t det_id) { self.det_id = det_id; } 
      )
    .def_property("crate_id", 
      [](DAQEthHeader& self) -> uint32_t { return self.crate_id; }, 
      [](DAQEthHeader& self, uint32_t crate_id) { self.crate_id = crate_id; } 
      )
    .def_property("slot_id", 
      [](DAQEthHeader& self) -> uint32_t { return self.slot_id; }, 
      [](DAQEthHeader& self, uint32_t slot_id) { self.slot_id = slot_id; } 
      )
    .def_property("stream_id", 
      [](DAQEthHeader& self) -> uint32_t { return self.stream_id; }, 
      [](DAQEthHeader& self, uint32_t stream_id) { self.stream_id = stream_id; } 
      )
     .def_property("reserved",
      [](DAQEthHeader& self) -> uint32_t { return self.reserved; },
      [](DAQEthHeader& self, uint32_t reserved) { self.reserved = reserved; }
      )
     .def_property("seq_id",
      [](DAQEthHeader& self) -> uint32_t { return self.seq_id; },
      [](DAQEthHeader& self, uint32_t seq_id) { self.seq_id = seq_id; }
      )
     .def_property("block_length",
      [](DAQEthHeader& self) -> uint32_t { return self.block_length; },
      [](DAQEthHeader& self, uint32_t block_length) { self.block_length = block_length; }
      )
     .def_property("timestamp",
      [](DAQEthHeader& self) -> uint64_t { return self.timestamp; },
      [](DAQEthHeader& self, uint64_t timestamp) { self.timestamp = timestamp; }
      )
     .def("get_timestamp", &DAQEthHeader::get_timestamp)
    ;
}

}  // namespace dunedaq::detdataformats::python

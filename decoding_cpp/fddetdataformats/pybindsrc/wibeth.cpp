/**
 * @file wibeth.cpp Python bindings for the WIBEthFrame format
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIBEthFrame.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::fddetdataformats::python {

void
register_wibeth(py::module& m)
{


  py::class_<WIBEthFrame::WIBEthHeader>(m, "WIBEthHeader")
    .def_property("channel",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.channel;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t channel) {self.channel = channel;}
      )
    .def_property("version",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.version;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t version) {self.version = version;}
      )
    // .def_property("reserved",
      // [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.reserved;},
      // [](WIBEthFrame::WIBEthHeader& self, uint32_t reserved) {self.reserved = reserved;}
      // )
    .def_property("context",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.context;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t context) {self.version = context;}
      )
    .def_property("ready",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.ready;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t ready) {self.ready = ready;}
      )
    .def_property("calibration",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.calibration;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t calibration) {self.calibration = calibration;}
      )
    .def_property("pulser",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.pulser;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t pulser) {self.pulser = pulser;}
      )
    .def_property("femb_sync",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.femb_sync;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t femb_sync) {self.femb_sync = femb_sync;}
      )
    .def_property("wib_sync",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.wib_sync;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t wib_sync) {self.wib_sync = wib_sync;}
      )
    .def_property("lol",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.lol;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t lol) {self.lol = lol;}
      )
    .def_property("link_valid",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.link_valid;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t link_valid) {self.link_valid = link_valid;}
      )
    .def_property("crc_err",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.crc_err;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t crc_err) {self.crc_err = crc_err;}
      )
    .def_property("colddata_timestamp_1",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.colddata_timestamp_1;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t colddata_timestamp_1) {self.lol = colddata_timestamp_1;}
      )
    .def_property("colddata_timestamp_0",
      [](WIBEthFrame::WIBEthHeader& self) -> uint32_t {return self.colddata_timestamp_0;},
      [](WIBEthFrame::WIBEthHeader& self, uint32_t colddata_timestamp_0) {self.colddata_timestamp_0 = colddata_timestamp_0;}
      )
    .def_property("extra_data",
      [](WIBEthFrame::WIBEthHeader& self) -> uint64_t {return self.extra_data;},
      [](WIBEthFrame::WIBEthHeader& self, uint64_t extra_data) {self.extra_data = extra_data;}
      )
    ;

  py::class_<WIBEthFrame>(m, "WIBEthFrame", py::buffer_protocol())
    .def(py::init())
    .def(py::init([](py::capsule capsule) {
        auto wfp = *static_cast<WIBEthFrame*>(capsule.get_pointer());
        return wfp;
    } ))
    .def(py::init([](py::bytes bytes){
        py::buffer_info info(py::buffer(bytes).request());
        auto wfp = *static_cast<WIBEthFrame*>(info.ptr);
        return wfp;
    }))
    .def("get_daqheader", [](WIBEthFrame& self) -> const detdataformats::DAQEthHeader& {return self.daq_header;}, py::return_value_policy::reference_internal)
    .def("get_wibheader", [](WIBEthFrame& self) -> const WIBEthFrame::WIBEthHeader& {return self.header;}, py::return_value_policy::reference_internal)
    .def("get_adc", &WIBEthFrame::get_adc)
    .def("set_adc", &WIBEthFrame::set_adc)
    .def("get_timestamp", &WIBEthFrame::get_timestamp)
    .def("set_timestamp", &WIBEthFrame::set_timestamp)
    .def("get_channel", &WIBEthFrame::get_channel)
    .def("set_channel", &WIBEthFrame::set_channel)
    .def_static("sizeof", [](){ return sizeof(WIBEthFrame); })
    .def("get_bytes",
         [](WIBEthFrame* fr) -> py::bytes {
           return py::bytes(reinterpret_cast<char*>(fr), sizeof(WIBEthFrame));
        })
  ;
}

} // namespace dunedaq::fddetdataformats::python

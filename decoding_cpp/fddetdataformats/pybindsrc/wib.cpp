/**
 * @file wib.cpp Python bindings for the WIBFrame format
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIBFrame.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq::fddetdataformats::python {

void
register_wib(py::module& m)
{

  py::class_<WIBFrame>(m, "WIBFrame", py::buffer_protocol())
    .def(py::init())
    .def(py::init([](py::capsule capsule) {
        auto wfp = *static_cast<WIBFrame*>(capsule.get_pointer());
        return wfp;
    } ))
    .def(py::init([](py::bytes bytes){
      py::buffer_info info(py::buffer(bytes).request());
      auto wfp = *static_cast<WIBFrame*>(info.ptr);
      return wfp;
    }))
    .def("get_wib_header", static_cast<const WIBHeader* (WIBFrame::*)() const >(&WIBFrame::get_wib_header), py::return_value_policy::reference_internal)
    .def("get_coldata_header", &WIBFrame::get_coldata_header, py::return_value_policy::reference_internal)
    .def("get_block", &WIBFrame::get_block, py::return_value_policy::reference_internal)
    .def("get_channel", static_cast<uint16_t (WIBFrame::*)(const uint8_t, const uint8_t, const uint8_t) const>(&WIBFrame::get_channel))
    .def("get_channel", static_cast<uint16_t (WIBFrame::*)(const uint8_t, const uint8_t) const>(&WIBFrame::get_channel))
    .def("get_channel", static_cast<uint16_t (WIBFrame::*)(const uint8_t) const>(&WIBFrame::get_channel))
    .def("set_channel", static_cast<void (WIBFrame::*)(const uint8_t, const uint16_t)>(&WIBFrame::set_channel))
    .def("get_timestamp", &WIBFrame::get_timestamp)
    .def_static("sizeof", [](){ return sizeof(WIBFrame); })
    .def("get_bytes",
         [](WIBFrame* fr) -> py::bytes {
           return py::bytes(reinterpret_cast<char*>(fr), sizeof(WIBFrame));
        }
    )
  ;

  py::class_<WIBHeader>(m, "WIBHeader")
    .def_property_readonly("sof", [](WIBHeader& self) -> uint32_t {return self.sof;})
    .def_property_readonly("version", [](WIBHeader& self) -> uint32_t {return self.version;})
    .def_property_readonly("fiber_no", [](WIBHeader& self) -> uint32_t {return self.fiber_no;})
    .def_property_readonly("crate_no", [](WIBHeader& self) -> uint32_t {return self.crate_no;})
    .def_property_readonly("slot_no", [](WIBHeader& self) -> uint32_t {return self.slot_no;})
    .def_property_readonly("mm", [](WIBHeader& self) -> uint32_t {return self.mm;})
    .def_property_readonly("oos", [](WIBHeader& self) -> uint32_t {return self.oos;})
    .def_property_readonly("mm", [](WIBHeader& self) -> uint32_t {return self.mm;})
    .def_property_readonly("wib_errors", [](WIBHeader& self) -> uint32_t {return self.wib_errors;})
    .def("get_timestamp", &WIBHeader::get_timestamp)
    .def("get_wib_counter", &WIBHeader::get_wib_counter)
  ;
  py::class_<ColdataHeader>(m, "ColdataHeader")
    .def_property_readonly("s1_error", [](ColdataHeader& self) -> uint32_t {return self.s1_error;})
    .def_property_readonly("s2_error", [](ColdataHeader& self) -> uint32_t {return self.s2_error;})
    .def_property_readonly("coldata_convert_count", [](ColdataHeader& self) -> uint32_t {return self.coldata_convert_count;})
    .def_property_readonly("error_register", [](ColdataHeader& self) -> uint32_t {return self.error_register;})
    .def_property_readonly("hdr_1", [](ColdataHeader& self) -> uint32_t {return self.hdr_1;})
    .def_property_readonly("hdr_3", [](ColdataHeader& self) -> uint32_t {return self.hdr_3;})
    .def_property_readonly("hdr_2", [](ColdataHeader& self) -> uint32_t {return self.hdr_2;})
    .def_property_readonly("hdr_4", [](ColdataHeader& self) -> uint32_t {return self.hdr_4;})
    .def_property_readonly("hdr_5", [](ColdataHeader& self) -> uint32_t {return self.hdr_5;})
    .def_property_readonly("hdr_7", [](ColdataHeader& self) -> uint32_t {return self.hdr_7;})
    .def_property_readonly("hdr_6", [](ColdataHeader& self) -> uint32_t {return self.hdr_6;})
    .def_property_readonly("hdr_8", [](ColdataHeader& self) -> uint32_t {return self.hdr_8;})
    .def("get_checksum_a", &ColdataHeader::get_checksum_a)
    .def("get_checksum_b", &ColdataHeader::get_checksum_b)
    .def("get_hdr", &ColdataHeader::get_hdr)
  ;

  py::class_<ColdataSegment>(m, "ColdataSegment")
    .def("get_channel", &ColdataSegment::get_channel)
  ;
  py::class_<ColdataBlock>(m, "ColdataBlock")
    .def("get_channel", &ColdataBlock::get_channel)
  ;

}

} // namespace dunedaq::fddetdataformats::python

/**
 * @file ssp.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/SSPTypes.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

using namespace dunedaq::fddetdataformats::ssp;

namespace dunedaq::fddetdataformats::python {

void
register_ssp(py::module& m)
{ 
    py::enum_<Comm_t>(m, "Comm_t")
    .value("kUSB", kUSB)
    .value("kEthernet", kEthernet)
    .value("kEmulated", kEmulated)
    .export_values()
  ;

  m.attr("max_control_data") = max_control_data;
  
  py::enum_<commandConstants>(m, "commandConstants")
    .value("cmdNone", cmdNone)
    .value("cmdRead", cmdRead)
    .value("cmdReadMask", cmdReadMask)
    .value("cmdWrite", cmdWrite)
    .value("cmdWriteMask", cmdWriteMask)
    .value("cmdArrayRead", cmdArrayRead)
    .value("cmdArrayWrite", cmdArrayWrite)
    .value("cmdFifoRead", cmdFifoRead)
    .value("cmdFifoWrite", cmdFifoWrite)
    .value("numCommands", numCommands)
    .export_values() 
  ;

  py::enum_<statusConstants>(m, "statusConstants")
    .value("statusNoError", statusNoError)
    .value("statusSendError", statusSendError)
    .value("statusReceiveError", statusReceiveError)
    .value("statusTimeoutError", statusTimeoutError)
    .value("statusAddressError", statusAddressError)
    .value("statusAlignError", statusAlignError)
    .value("statusCommandError", statusCommandError)
    .value("statusSizeError", statusSizeError)
    .value("statusWriteError", statusWriteError)
    .export_values() 
  ;

  py::class_<MillisliceHeader> (m, "MillisliceHeader")
    .def_property_readonly("startTime", [](const MillisliceHeader& self) -> unsigned long {return self.startTime;})
    .def_property_readonly("endTime",  [](const MillisliceHeader& self) -> unsigned long {return self.endTime;})
    .def_property_readonly("triggerTime",  [](const MillisliceHeader& self) -> unsigned long {return self.triggerTime;})
    .def_property_readonly("length", [](const MillisliceHeader& self) -> unsigned int {return self.length;})
    .def_property_readonly("nTriggers", [](const MillisliceHeader& self) -> unsigned int {return self.nTriggers;})
    .def_property_readonly("triggerType", [](const MillisliceHeader& self) -> unsigned int {return self.triggerType;})
    .def_property_readonly_static("sizeInUInts", [](const MillisliceHeader& self) -> size_t {return self.sizeInUInts;})
  ;

  py::class_<EventHeader> (m, "EventHeader", pybind11::buffer_protocol())
    .def(py::init([](py::capsule capsule) {
        auto evp = *static_cast<EventHeader*>(capsule.get_pointer());
        return evp;
    } ))
    .def_property_readonly("header", [](const EventHeader& self) -> unsigned int {return self.header;})
    .def_property_readonly("length", [](const EventHeader& self) -> unsigned short {return self.length;})
    .def_property_readonly("group1", [](const EventHeader& self) -> unsigned short {return self.group1;})
    .def_property_readonly("triggerID", [](const EventHeader& self) -> unsigned short {return self.triggerID;})
    .def_property_readonly("group2", [](const EventHeader& self) -> unsigned short {return self.group2;})
    .def_property_readonly("timestamp",
      [](const EventHeader& self) -> pybind11::array {
            auto dtype = py::dtype(py::format_descriptor<unsigned short>::format());
            auto base = py::array(dtype, {4}, {sizeof(unsigned short)});
            return pybind11::array(dtype, {4}, {sizeof(unsigned short)}, self.timestamp, base);
      },
      py::return_value_policy::reference_internal)
    .def_property_readonly("peakSumLow", [](const EventHeader& self) -> unsigned short {return self.peakSumLow;})
    .def_property_readonly("group3", [](const EventHeader & self) -> unsigned short {return self.group3;})
    .def_property_readonly("preriseLow", [](const EventHeader& self) -> unsigned short {return self.preriseLow;})
    .def_property_readonly("group4", [](const EventHeader& self) -> unsigned short {return self.group4;})
    .def_property_readonly("intSumHigh", [](const EventHeader& self) -> unsigned short {return self.intSumHigh;})
    .def_property_readonly("baseline", [](const EventHeader& self) -> unsigned short {return self.baseline;})
    .def_property_readonly("cfdPoint",
      [](const EventHeader& self) -> pybind11::array {
            auto dtype = py::dtype(py::format_descriptor<unsigned short>::format());
            auto base = py::array(dtype, {4}, {sizeof(unsigned short)});
            return pybind11::array(dtype, {4}, {sizeof(unsigned short)}, self.cfdPoint, base);
      },
      py::return_value_policy::reference_internal)
    .def_property_readonly("intTimestamp",
      [](const EventHeader& self) -> pybind11::array {
            auto dtype = py::dtype(py::format_descriptor<unsigned short>::format());
            auto base = py::array(dtype, {4}, {sizeof(unsigned short)});
            return pybind11::array(dtype, {4}, {sizeof(unsigned short)}, self.intTimestamp, base);
      },
      py::return_value_policy::reference_internal)
    .def_static("sizeof", [](){ return sizeof(EventHeader); })
  ;
  
  py::class_<CtrlHeader> (m, "CtrlHeader", pybind11::buffer_protocol())
    .def_property_readonly("length", [](const CtrlHeader& self) -> unsigned int {return self.length;})
    .def_property_readonly("address", [](const CtrlHeader& self) -> unsigned int {return self.address;})
    .def_property_readonly("command", [](const CtrlHeader& self) -> unsigned int {return self.command;})
    .def_property_readonly("size", [](const CtrlHeader& self) -> unsigned int {return self.size;})
    .def_property_readonly("status", [](const CtrlHeader& self) -> unsigned int {return self.status;})
  ;

  py::class_<CtrlPacket> (m, "CtrlPacket")
    .def_property_readonly("header", [](const CtrlPacket& self) -> const CtrlHeader& {return self.header;})
    .def_property_readonly("data",
      [](const CtrlPacket& self) -> pybind11::array {
        auto dtype = py::dtype(py::format_descriptor<unsigned int>::format());
        auto base = py::array(dtype, {max_control_data}, {sizeof(unsigned int)});
        return pybind11::array(dtype, {max_control_data}, {sizeof(unsigned int)}, self.data, base);
      },
      py::return_value_policy::reference_internal)
  ;
}
} // namespace dunedaq::fddetdataformats::python

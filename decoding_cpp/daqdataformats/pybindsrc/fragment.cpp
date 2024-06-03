/**
 * @file fragment.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/Fragment.hpp"
#include "daqdataformats/FragmentHeader.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq {
namespace daqdataformats {
namespace python {

void
register_fragment(py::module& m)
{

  py::class_<Fragment> py_fragment(m, "Fragment", py::buffer_protocol());

  py_fragment.def("get_header", &Fragment::get_header, py::return_value_policy::reference_internal)
    .def("get_storage_location", &Fragment::get_storage_location, py::return_value_policy::reference_internal)
    .def("get_trigger_number", &Fragment::get_trigger_number)
    .def("get_run_number", &Fragment::get_run_number)
    .def("get_trigger_timestamp", &Fragment::get_trigger_timestamp)
    .def("get_window_begin", &Fragment::get_window_begin)
    .def("get_window_end", &Fragment::get_window_end)
    .def("get_element_id", &Fragment::get_element_id)
    .def("get_detector_id", &Fragment::get_detector_id)
    .def("get_error_bits", &Fragment::get_error_bits)
    .def("get_error_bit", &Fragment::get_error_bit)
    .def("get_fragment_type_code", &Fragment::get_fragment_type_code)
    .def("get_fragment_type", &Fragment::get_fragment_type)
    .def("get_sequence_number", &Fragment::get_sequence_number)
    .def("get_size", &Fragment::get_size)
    .def("get_data_size", &Fragment::get_data_size)
    .def("get_data", &Fragment::get_data, py::return_value_policy::reference_internal)
    .def(
      "get_data",
      [](Fragment& self, size_t offset) { return static_cast<void*>(static_cast<char*>(self.get_data()) + offset); },
      py::return_value_policy::reference_internal  
    )
    .def("get_data_bytes", [](Fragment* fr) -> py::bytes {
           return py::bytes(reinterpret_cast<char*>(fr->get_data()), fr->get_data_size());
        },
        py::return_value_policy::reference_internal
    );

  py::enum_<Fragment::BufferAdoptionMode>(py_fragment, "BufferAdoptionMode")
    .value("kReadOnlyMode", Fragment::BufferAdoptionMode::kReadOnlyMode)
    .value("kTakeOverBuffer", Fragment::BufferAdoptionMode::kTakeOverBuffer)
    .value("kCopyFromBuffer", Fragment::BufferAdoptionMode::kCopyFromBuffer)
    .export_values();

  py::class_<FragmentHeader>(m, "FragmentHeader")
    .def_property_readonly(
      "fragment_header_marker",
      [](const FragmentHeader& self) -> uint32_t { return self.fragment_header_marker; }) // NOLINT(build/unsigned)
    .def_property_readonly(
      "version", [](const FragmentHeader& self) -> uint32_t { return self.version; }) // NOLINT(build/unsigned)
    .def_property_readonly("size", [](const FragmentHeader& self) -> fragment_size_t { return self.size; })
    .def_property_readonly("trigger_number",
                           [](const FragmentHeader& self) -> trigger_number_t { return self.trigger_number; })
    .def_property_readonly("trigger_timestamp",
                           [](const FragmentHeader& self) -> timestamp_t { return self.trigger_timestamp; })
    .def_property_readonly("window_begin", [](const FragmentHeader& self) -> timestamp_t { return self.window_begin; })
    .def_property_readonly("window_end", [](const FragmentHeader& self) -> timestamp_t { return self.window_end; })
    .def_property_readonly("run_number", [](const FragmentHeader& self) -> run_number_t { return self.run_number; })
    .def_property_readonly(
      "error_bits", [](const FragmentHeader& self) -> uint32_t { return self.error_bits; }) // NOLINT(build/unsigned)
    .def_property_readonly("fragment_type",
                           [](const FragmentHeader& self) -> fragment_type_t { return self.fragment_type; })
    .def_property_readonly("sequence_number",
                           [](const FragmentHeader& self) -> sequence_number_t { return self.sequence_number; })
    .def_property_readonly("detector_id", [](const FragmentHeader& self) -> uint16_t { return self.detector_id; })
    .def_property_readonly("element_id", [](const FragmentHeader& self) -> SourceID { return self.element_id; })
    .def_static("sizeof", []() { return sizeof(FragmentHeader); });

  py::enum_<FragmentErrorBits>(m, "FragmentErrorBits")
    .value("kDataNotFound", FragmentErrorBits::kDataNotFound)
    .value("kIncomplete", FragmentErrorBits::kIncomplete)
    .value("kInvalidWindow", FragmentErrorBits::kInvalidWindow)
    // TODO, Alessandro Thea <thea@github.com> Oct-31-2021:  Add unassigned
    .export_values();

  py::enum_<FragmentType>(m, "FragmentType")
    .value("kUnknown", FragmentType::kUnknown)
    .value("kProtoWIB", FragmentType::kProtoWIB)
    .value("kWIB", FragmentType::kWIB)
    .value("kDAPHNE", FragmentType::kDAPHNE)
    .value("kTDE_AMC", FragmentType::kTDE_AMC)
    .value("kFW_TriggerPrimitive", FragmentType::kFW_TriggerPrimitive)
    .value("kTriggerPrimitive", FragmentType::kTriggerPrimitive)
    .value("kTriggerActivity", FragmentType::kTriggerActivity)
    .value("kTriggerCandidate", FragmentType::kTriggerCandidate)
    .value("kHardwareSignal", FragmentType::kHardwareSignal)
    .value("kPACMAN", FragmentType::kPACMAN)
    .value("kWIBEth", FragmentType::kWIBEth)
    .export_values();
}

} // namespace python
} // namespace daqdataformats
} // namespace dunedaq

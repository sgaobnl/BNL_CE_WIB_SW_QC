/**
 * @file timeslice.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/TimeSlice.hpp"
#include "daqdataformats/TimeSliceHeader.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>
#include <vector>

namespace py = pybind11;

namespace dunedaq {
namespace daqdataformats {
namespace python {

void
register_timeslice(py::module& m)
{
  py::class_<TimeSliceHeader>(m, "TimeSliceHeader")
    .def_property_readonly_static("s_timeslice_header_marker",
                                  [](const TimeSliceHeader& self) -> uint32_t { // NOLINT(build/unsigned)
                                    return self.s_timeslice_header_marker;
                                  })
    .def_property_readonly_static("s_timeslice_header_version",
                                  [](const TimeSliceHeader& self) -> uint32_t { // NOLINT(build/unsigned)
                                    return self.s_timeslice_header_version;
                                  })
    .def_property_readonly("timeslice_header_marker",
                           [](const TimeSliceHeader& self) -> uint32_t { // NOLINT(build/unsigned)
                             return self.timeslice_header_marker;
                           })
    .def_property_readonly(
      "version", [](const TimeSliceHeader& self) -> uint32_t { return self.version; }) // NOLINT(build/unsigned)
    .def_property_readonly("timeslice_number",
                           [](const TimeSliceHeader& self) -> timeslice_number_t { return self.timeslice_number; })

    .def_property_readonly("run_number", [](const TimeSliceHeader& self) -> run_number_t { return self.run_number; });

  py::class_<TimeSlice> py_timeslice(m, "TimeSlice", pybind11::buffer_protocol());
  py_timeslice.def(py::init<TimeSliceHeader const&>())
    .def(py::init<timeslice_number_t, run_number_t>())
    .def(
      "get_header", [](TimeSlice& self) { return self.get_header(); }, py::return_value_policy::reference_internal)
    //    .def("set_header", &TimeSlice::set_header)
    .def(
      "get_fragments_ref",
      [](TimeSlice& self) {
        auto fragments = py::list();
        for (auto& fragment : self.get_fragments_ref()) {
          auto py_fragment = py::cast(*fragment, py::return_value_policy::reference);
          fragments.append(py_fragment);
        }
        return fragments;
      },
      py::return_value_policy::reference_internal);
} // NOLINT

} // namespace python
} // namespace daqdataformats
} // namespace dunedaq
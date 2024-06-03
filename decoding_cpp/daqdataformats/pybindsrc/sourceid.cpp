/**
 * @file sourceid.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/SourceID.hpp"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

namespace py = pybind11;

namespace dunedaq::daqdataformats::python {

void
register_sourceid(py::module& m)
{

  py::class_<SourceID> py_sourceid(m, "SourceID");
  py_sourceid.def(py::init()).def(py::init<const SourceID::Subsystem&, const SourceID::ID_t&>());
  py_sourceid.def(py::self < py::self).def("__repr__", [](const SourceID& gid) {
    std::ostringstream oss;
    oss << "<daqdataformats::SourceID " << gid << ">";
    return oss.str();
  });

  py::enum_<SourceID::Subsystem>(py_sourceid, "Subsystem")
    .value("kUnknown", SourceID::Subsystem::kUnknown)
    .value("kDetectorReadout", SourceID::Subsystem::kDetectorReadout)
    .value("kHwSignalsInterface", SourceID::Subsystem::kHwSignalsInterface)
    .value("kTrigger", SourceID::Subsystem::kTrigger)
    .value("kTRBuilder", SourceID::Subsystem::kTRBuilder)
    .export_values();

  py_sourceid.def_readwrite("version", &SourceID::version)
    .def_readwrite("subsystem", &SourceID::subsystem)
    .def_readwrite("id", &SourceID::id);

  py_sourceid.def("subsystem_to_string", &SourceID::subsystem_to_string)
    .def("string_to_subsystem", &SourceID::string_to_subsystem)
      .def("to_string", &SourceID::to_string);
}

} // namespace dunedaq::daqdataformats::python

/**
 * @file detid.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "detdataformats/DetID.hpp"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

namespace py = pybind11;

namespace dunedaq::detdataformats::python {

void register_detid(py::module& m) {
  py::class_<DetID> py_detid(m, "DetID");
  py_detid.def(py::init())
      .def(py::init<const DetID::Subdetector&>())
      .def("__repr__", [](const DetID& gid) {
        std::ostringstream oss;
        oss << "<detdataformats::DetID " << gid.to_string() << ">";
        return oss.str();
      })
      .def("to_string", &DetID::to_string)
      .def("is_in_valid_state", &DetID::is_in_valid_state)
      .def("subdetector_to_string", &DetID::subdetector_to_string)
      .def("string_to_subdetector", &DetID::string_to_subdetector);

  py::enum_<DetID::Subdetector>(py_detid, "Subdetector")
      .value("kUnknown", DetID::Subdetector::kUnknown)
      .value("kDAQ", DetID::Subdetector::kDAQ)
      .value("kHD_PDS", DetID::Subdetector::kHD_PDS)
      .value("kHD_TPC", DetID::Subdetector::kHD_TPC)
      .value("kHD_CRT", DetID::Subdetector::kHD_CRT)
      .value("kVD_CathodePDS", DetID::Subdetector::kVD_CathodePDS)
      .value("kVD_MembranePDS", DetID::Subdetector::kVD_MembranePDS)
      .value("kVD_BottomTPC", DetID::Subdetector::kVD_BottomTPC)
      .value("kVD_TopTPC", DetID::Subdetector::kVD_TopTPC)
      .value("kNDLAr_TPC", DetID::Subdetector::kNDLAr_TPC)
      .value("kNDLAr_PDS", DetID::Subdetector::kNDLAr_PDS)
      .value("kND_GAr", DetID::Subdetector::kND_GAr)
      .export_values();

  py_detid.def_readwrite("version", &DetID::version)
      .def_readwrite("subdetector", &DetID::subdetector);
}

}  // namespace dunedaq::detdataformats::python


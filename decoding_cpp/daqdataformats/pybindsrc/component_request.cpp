/**
 * @file omponent_request.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/ComponentRequest.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq {
namespace daqdataformats {
namespace python {

void
register_component_request(py::module& m)
{

  py::class_<ComponentRequest>(m, "ComponentRequest")
    .def(py::init())
    .def(py::init<SourceID const&, timestamp_t const&, timestamp_t const&>())
    .def_readonly_static("s_component_request_version", &ComponentRequest::s_component_request_version)
    .def_readonly("unused", &ComponentRequest::unused)
    .def_readonly("version", &ComponentRequest::version)
    .def_readonly("window_begin", &ComponentRequest::window_begin)
    .def_readonly("window_end", &ComponentRequest::window_end);
}

} // namespace python
} // namespace daqdataformats
} // namespace dunedaq
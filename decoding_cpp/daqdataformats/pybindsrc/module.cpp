/**
 * @file module.cpp
 *
 * This is part of the DUNE DAQ Software Suite, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace dunedaq {
namespace daqdataformats {
namespace python {

extern void
register_sourceid(py::module&);
extern void
register_fragment(py::module&);
extern void
register_component_request(py::module&);
extern void
register_trigger_record(py::module&);
extern void
register_timeslice(py::module&);

PYBIND11_MODULE(_daq_daqdataformats_py, m)
{

  m.doc() = "c++ implementation of the dunedaq daqdataformats modules"; // optional module docstring

  register_sourceid(m);
  register_fragment(m);
  register_component_request(m);
  register_trigger_record(m);
  register_timeslice(m);
}

} // namespace python
} // namespace daqdataformats
} // namespace dunedaq

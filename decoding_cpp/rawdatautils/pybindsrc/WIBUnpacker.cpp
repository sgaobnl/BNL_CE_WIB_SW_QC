/**
 * @file WIBUnpacker.cc Fast C++ -> numpy WIB format decoder
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIBFrame.hpp"
#include "daqdataformats/Fragment.hpp"

#include <cstdint>
#include <pybind11/numpy.h>

namespace py = pybind11;
namespace dunedaq::rawdatautils::wib {

/**
 * @brief Unpacks data containing WIBFrames into a numpy array with the ADC
 * values and dimension (number of WIBFrames, 256)
 * Warning: It doesn't check that nframes is a sensible value (can read out of bounds)
 */
py::array_t<uint16_t> np_array_adc_data(void* data, int nframes){
  py::array_t<uint16_t> ret(256 * nframes);
  auto ptr = static_cast<uint16_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; ++i) {
    auto fr = reinterpret_cast<fddetdataformats::WIBFrame*>(static_cast<char*>(data) + i * sizeof(fddetdataformats::WIBFrame));
    for (size_t j=0; j<256; ++j)
      ptr[256 * i + j] = fr->get_channel(j);
  }
  ret.resize({nframes, 256});

  return ret;
}

/**
 * @brief Unpacks data containing WIBFrames into a numpy array with the
 * timestamps with dimension (number of WIBFrames)
 * Warning: It doesn't check that nframes is a sensible value (can read out of bounds)
 */
py::array_t<uint64_t> np_array_timestamp_data(void* data, int nframes){
  py::array_t<uint64_t> ret(nframes);
  auto ptr = static_cast<uint64_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; ++i) {
    auto fr = reinterpret_cast<fddetdataformats::WIBFrame*>(static_cast<char*>(data) + i * sizeof(fddetdataformats::WIBFrame));
    ptr[i] = fr->get_timestamp();
  }

  return ret;
}

/**
 * @brief Unpacks a Fragment containing WIBFrames into a numpy array with the
 * ADC values and dimension (number of WIBFrames in the Fragment, 256)
 */
py::array_t<uint16_t> np_array_adc(daqdataformats::Fragment& frag){
  return np_array_adc_data(frag.get_data(), (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::WIBFrame));
}

/**
 * @brief Unpacks the timestamps in a Fragment containing WIBFrames into a numpy
 * array with dimension (number of WIBFrames in the Fragment)
 */
py::array_t<uint64_t> np_array_timestamp(daqdataformats::Fragment& frag){
  return np_array_timestamp_data(frag.get_data(), (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::WIBFrame));
}


} // namespace dunedaq::rawdatautils::wib // NOLINT

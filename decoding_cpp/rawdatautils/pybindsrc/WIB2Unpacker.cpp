/**
 * @file WIB2Unpacker.cc Fast C++ -> numpy WIB2 format unpacker
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIB2Frame.hpp"
#include "daqdataformats/Fragment.hpp"

#include <cstdint>
#include <pybind11/numpy.h>

namespace py = pybind11;
namespace dunedaq::rawdatautils::wib2 {

/**
 * @brief Gets number of WIB2Frames in a fragment
 */
uint32_t get_n_frames(daqdataformats::Fragment const& frag){
  return (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::WIB2Frame);
}

/**
 * @brief Unpacks data containing WIB2Frames into a numpy array with the ADC
 * values and dimension (number of WIB2Frames, 256)
 * Warning: It doesn't check that nframes is a sensible value (can read out of bounds)
 */
py::array_t<uint16_t> np_array_adc_data(void* data, int nframes){
  py::array_t<uint16_t> ret(256 * nframes);
  auto ptr = static_cast<uint16_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; ++i) {
    auto fr = reinterpret_cast<fddetdataformats::WIB2Frame*>(static_cast<char*>(data) + i * sizeof(fddetdataformats::WIB2Frame));
    for (size_t j=0; j<256; ++j)
      ptr[256 * i + j] = fr->get_adc(j);
  }
  ret.resize({nframes, 256});

  return ret;
}

/**
 * @brief Unpacks data containing WIB2Frames into a numpy array with the
 * timestamps with dimension (number of WIB2Frames)
 * Warning: It doesn't check that nframes is a sensible value (can read out of bounds)
 */
py::array_t<uint64_t> np_array_timestamp_data(void* data, int nframes){
  py::array_t<uint64_t> ret(nframes);
  auto ptr = static_cast<uint64_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; ++i) {
    auto fr = reinterpret_cast<fddetdataformats::WIB2Frame*>(static_cast<char*>(data) + i * sizeof(fddetdataformats::WIB2Frame));
    ptr[i] = fr->get_timestamp();
  }

  return ret;
}

/**
 * @brief Unpacks a Fragment containing WIB2Frames into a numpy array with the
 * ADC values and dimension (number of WIB2Frames in the Fragment, 256)
 */
py::array_t<uint16_t> np_array_adc(daqdataformats::Fragment const& frag){
  return np_array_adc_data(frag.get_data(), get_n_frames(frag));
}

/**
 * @brief Unpacks the timestamps in a Fragment containing WIBFrames into a numpy
 * array with dimension (number of WIB2Frames in the Fragment)
 */
py::array_t<uint64_t> np_array_timestamp(daqdataformats::Fragment const& frag){
  return np_array_timestamp_data(frag.get_data(), get_n_frames(frag));
}


} // namespace dunedaq::rawdatautils::wib2 // NOLINT

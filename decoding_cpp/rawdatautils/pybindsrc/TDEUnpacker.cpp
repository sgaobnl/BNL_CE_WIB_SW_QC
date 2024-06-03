/**
 * @file WIBEthUnpacker.cc Fast C++ -> numpy WIBEth format unpacker
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/TDE16Frame.hpp"
#include "daqdataformats/Fragment.hpp"

#include <cstdint>
#include <pybind11/numpy.h>

namespace py = pybind11;
namespace dunedaq::rawdatautils::tde {

/**
 * @brief Gets number of TDE16Frames in a fragment
 */
uint32_t get_n_frames(daqdataformats::Fragment const& frag){
  return (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::TDE16Frame);
}

/**
 * @brief Unpacks data containing TDE16Frames into a numpy array with the
 * timestamps/channel with dimension (number of TDE16Frames)
 * Warning: It doesn't check that nframes is a sensible value (can read out of bounds)
 */
py::array_t<uint64_t> np_array_timestamp_data(daqdataformats::Fragment const& frag){
  size_t nframes = (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::TDE16Frame);
  py::array_t<uint64_t> ret(nframes);
  auto ptr = static_cast<uint64_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; i++) {
    auto fr = reinterpret_cast<fddetdataformats::TDE16Frame*>(static_cast<char*>(frag.get_data()) + i * sizeof(fddetdataformats::TDE16Frame));
    ptr[i] = fr->get_timestamp();
  }

  return ret;
}

py::array_t<uint64_t> np_array_channel_data(daqdataformats::Fragment const& frag){
  size_t nframes = (frag.get_size() - sizeof(daqdataformats::FragmentHeader)) / sizeof(fddetdataformats::TDE16Frame);
  py::array_t<uint64_t> ret(nframes);
  auto ptr = static_cast<uint64_t*>(ret.request().ptr);
  for (size_t i=0; i<(size_t)nframes; i++) {
    auto fr = reinterpret_cast<fddetdataformats::TDE16Frame*>(static_cast<char*>(frag.get_data()) + i * sizeof(fddetdataformats::TDE16Frame));
    ptr[i] = fr->get_channel();
  }

  return ret;
}

} // namespace dunedaq::rawdatautils::tde // NOLINT

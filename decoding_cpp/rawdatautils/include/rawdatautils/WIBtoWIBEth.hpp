/**
 * @file WIBtoWIBEth.hpp Implementation of functions to convert files from the old WIB format to WIBEth
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef RAWDATAUTILS_INCLUDE_WIBTOWIBETH_HPP_
#define RAWDATAUTILS_INCLUDE_WIBTOWIBETH_HPP_

#include <cstdint>
#include <iostream>
#include <fstream>
#include <filesystem>
#include "fddetdataformats/WIBFrame.hpp"
#include "fddetdataformats/WIBEthFrame.hpp"

namespace dunedaq {
namespace rawdatautils {

fddetdataformats::WIBEthFrame
wibtowibeth(fddetdataformats::WIBFrame* fr, uint64_t timestamp=0, int starting_channel=0) {
  fddetdataformats::WIBEthFrame res;
  for (int j = 0; j < 64; ++j) {
    for (int i = 0; i < 64; ++i) {
      res.set_adc(i, j, (fr + j)->get_channel(starting_channel + i));
    }
  }
  auto header = fr->get_wib_header();
  //res.daq_header.version = header->version; //Warning, in WIBFrames version has 5 bits and here it has 4
  //res.daq_header.crate_id = header->crate_no; //CHANGED ALL THESE CAUSE I GOT RID OF EM
  //res.daq_header.slot_id = header->slot_no;
  //res.daq_header.stream_id = header->fiber_no;
  res.set_channel(starting_channel);
  res.set_timestamp(timestamp);
  res.header.extra_data = 0xdeadbeef0badface;
  return res;
}

void
wib_binary_to_wibeth_binary(std::string& filename, std::string& output) {
  std::ifstream file(filename.c_str(), std::ios::binary);
  std::cout << "Transforming " << filename << " to " << output << '\n';
  auto size = std::filesystem::file_size(filename);
  std::vector<char> v(size);
  file.read(v.data(), size);
  file.close();
  std::cout << "Number of frames found: "<< size / sizeof(fddetdataformats::WIBFrame) << '\n';

  std::ofstream out(output.c_str(), std::ios::binary);
  std::vector<int> starting_channel {0, 64, 128, 192};
  for (auto& sc : starting_channel) {
    auto ptr = reinterpret_cast<fddetdataformats::WIBFrame*>(v.data());
    uint64_t timestamp = ptr->get_timestamp();
    int num_frames = size / sizeof(fddetdataformats::WIBFrame);
    while(num_frames >= 64){
      auto wibethfr = wibtowibeth(ptr, timestamp, sc);
      timestamp += 32 * 64;
      ptr += 64;
      num_frames -= 64;
      out.write(reinterpret_cast<char*>(&wibethfr), sizeof(wibethfr));
    }
    out.close();
  }

}

void
wib_hdf5_to_wibeth_binary(std::string& /*filename*/, std::string& /*output*/) {
}


} // namespace dunedaq::rawdatautils
}

#endif // RAWDATAUTILS_INCLUDE_WIBTOWIBETH_HPP_

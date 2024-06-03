/**
 * @file WIBtoTDE16.hpp Implementation of functions to convert files from the old WIB format to TDE16
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef RAWDATAUTILS_INCLUDE_WIBTOTDE16_HPP_
#define RAWDATAUTILS_INCLUDE_WIBTOTDE16_HPP_

#include <cstdint>
#include <iostream>
#include <fstream>
#include <filesystem>
#include "detdataformats/DetID.hpp"
#include "fddetdataformats/WIBFrame.hpp"
#include "fddetdataformats/TDE16Frame.hpp"

namespace dunedaq {
namespace rawdatautils {

fddetdataformats::TDE16Frame
wibtotde(fddetdataformats::WIBFrame* fr, uint64_t timestamp, uint16_t ch) {
  fddetdataformats::TDE16Frame res;
  // leave ADCs empty for now
  for (auto i=0; i < dunedaq::fddetdataformats::tot_adc16_samples; i++) {
	res.set_adc_sample(ch,i);
  }

  auto header = fr->get_wib_header();
  //res.get_daq_header()->version = header->version;
  //res.get_daq_header()->det_id = 11;
  //res.get_daq_header()->crate_id = header->crate_no;
  //res.get_daq_header()->slot_id = header->slot_no;
  //res.get_daq_header()->stream_id = header->fiber_no;
  res.set_channel(ch);
  res.set_timestamp(timestamp);
  std::cout << " Generated frame with TS " << res.get_timestamp() << " for channel " << res.get_channel() << std::endl;
  return res;
}

void
wib_binary_to_tde_binary(std::string& filename, std::string& output) {
  //FIXME: this is temporary.... we take 1 WIB frame and invent TDE frames from it... ADC values not set
  std::ifstream file(filename.c_str(), std::ios::binary);
  std::ofstream out(output.c_str(), std::ios::binary);
  std::cout << "Transforming " << filename << " to " << output << '\n';
  auto size = std::filesystem::file_size(filename);
  std::vector<char> v(size);
  file.read(v.data(), size);
  file.close();
  int num_frames = size / sizeof(fddetdataformats::WIBFrame);
  if (num_frames > 10 ) num_frames = 10;
  std::cout << "Number of frames found: "<< num_frames << '\n';
  auto ptr = reinterpret_cast<fddetdataformats::WIBFrame*>(v.data());
  uint64_t timestamp = ptr->get_timestamp();
  while(num_frames--){
    for (uint16_t i = 0; i < dunedaq::fddetdataformats::n_channels_per_amc; i++) {	  
       auto tdefr = wibtotde(ptr, timestamp, i);
       out.write(reinterpret_cast<char*>(&tdefr), sizeof(tdefr));
    }
    timestamp += (dunedaq::fddetdataformats::tot_adc16_samples * dunedaq::fddetdataformats::ticks_between_adc_samples);
    ptr++;
  }
  out.close();
}

void
wib_hdf5_to_tde_binary(std::string& /*filename*/, std::string& /*output*/) {
}


} // namespace dunedaq::rawdatautils
}

#endif // RAWDATAUTILS_INCLUDE_WIBTOTDE16_HPP_

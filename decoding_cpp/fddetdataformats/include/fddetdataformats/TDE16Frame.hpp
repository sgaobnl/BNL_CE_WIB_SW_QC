/**
 * @file TDE16Frame.hpp TDE 16 bit fields and accessors
 *
 * This is part of the DUNE DAQ, copyright 2022.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */
#ifndef FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_TDE16FRAME_HPP_
#define FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_TDE16FRAME_HPP_

#include <bitset>
#include <iostream>
#include <vector>
#include <stdexcept> 

#include <ostream>
#include <string>
#include <fstream>
#include <iterator>

#include "detdataformats/DAQEthHeader.hpp"

namespace dunedaq::fddetdataformats {

static constexpr int ticks_between_adc_samples = 32;
static constexpr int tot_adc16_samples = 4474;
static constexpr int n_channels_per_amc = 64;
//static constexpr int payload16 = 8972;

struct TDEHeader
{
  uint64_t channel : 8, version : 4, tde_header : 10, tde_errors : 16, reserved : 26;
  uint64_t TAItime : 64;
};

struct Sample 
{
  uint16_t sample : 12, reserved : 4;
};

struct ADC16Data
{
  Sample samples_info[tot_adc16_samples];

  uint16_t get_adc_sample(int i) const
  {
    if (i < 0 || i >= tot_adc16_samples) { throw std::out_of_range("ADC sample index out of range"); }
    
    return (uint16_t)samples_info[i].sample;
  }
};

class TDE16Frame
{
public:
  const detdataformats::DAQEthHeader* get_daq_header() const { return &m_daq_header; }
  detdataformats::DAQEthHeader* get_daq_header() { return &m_daq_header; }
  const TDEHeader* get_tde_header() const { return &m_tde16_header; }
  TDEHeader* get_tde_header() { return &m_tde16_header; }

  // TDEHeader mutators
  uint64_t get_timestamp() const { return m_daq_header.get_timestamp(); } 
  void set_timestamp(const uint64_t new_timestamp) { m_daq_header.timestamp = new_timestamp; } 
  uint16_t get_channel() const { return m_tde16_header.channel; } 
  void set_channel(const uint16_t new_channel) { m_tde16_header.channel=new_channel; } 
  uint16_t get_tde_errors() { return m_tde16_header.tde_errors; } 
  void set_tde_errors(const uint16_t new_tde_errors) { m_tde16_header.tde_errors = new_tde_errors; } 
  uint64_t get_TAItime() { return m_tde16_header.TAItime; } 
  void set_TAItime(const uint64_t new_TAItime) { m_tde16_header.TAItime = new_TAItime; } 

  // ADC16Data mutators
  void set_adc_sample(const uint16_t new_adc_val, int sample_no) { m_adc16_data.samples_info[sample_no].sample = new_adc_val; } 
  uint16_t get_adc_sample(int sample_no) const { return m_adc16_data.get_adc_sample(sample_no); } 

  friend std::ostream& operator<<(std::ostream& o, TDE16Frame const& tde16_frame);

private:
  detdataformats::DAQEthHeader m_daq_header;
  TDEHeader m_tde16_header;
  ADC16Data m_adc16_data;
};

inline std::ostream&
operator<<(std::ostream& o, TDEHeader const& tde_header)
{
    return o << std::hex << "channel: " << tde_header.channel << "version: " << tde_header.version 
	    << "TAItime: " << tde_header.TAItime
	    << " tde_header: " <<  tde_header.tde_header<< " tde_errors: " << tde_header.tde_errors << std::dec << '\n';
}

inline std::ostream&
operator<<(std::ostream& o, Sample const& sampleinfo)
{
  return o << "sample: " << unsigned(sampleinfo.sample) << " reserved: " << unsigned(sampleinfo.reserved) << '\n';
}

inline std::ostream&
operator<<(std::ostream& o, TDE16Frame const& tde16frame)
{
  o << "Printing frame:" << '\n';
  o << tde16frame.m_daq_header << '\n';
  o << tde16frame.m_tde16_header << '\n';
  return o;
}

} // namespace dunedaq::fddetdataformats

#endif // FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_TDE16FRAME_HPP_

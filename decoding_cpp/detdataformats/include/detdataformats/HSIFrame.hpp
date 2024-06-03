/**
 * @file HSIFrame.hpp
 *
 *  Contains declaration of HSIFrame.
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DETDATAFORMATS_INCLUDE_HSIFRAME_HPP_
#define DETDATAFORMATS_INCLUDE_HSIFRAME_HPP_

#include <cstdint>  // For uint32_t etc

namespace dunedaq::detdataformats {

class HSIFrame
{
public:
  // The definition of the format is in terms of 32-bit words
  typedef uint32_t word_t; // NOLINT
  
  word_t version : 6, detector_id : 6, crate : 10, slot : 4, link : 6;
  word_t timestamp_low : 32;
  word_t timestamp_high : 32;
  word_t input_low : 32;
  word_t input_high : 32;
  word_t trigger : 32;
  word_t sequence : 32;

  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    return (uint64_t)timestamp_low | ((uint64_t)timestamp_high << 32); // NOLINT(build/unsigned)
  }

  void set_timestamp(uint64_t ts) // NOLINT(build/unsigned)
  {
    timestamp_low = ts;
    timestamp_high = ts >> 32;
  }
};

} // namespace dunedaq::detdataformats

#endif // DETDATAFORMATS_INCLUDE_HSIFRAME_HPP_

// Local Variables:
// c-basic-offset: 2
// End:

/**
 * @file DAQEthHeader.hpp Common header structure that is used by 
 * every FrontEnd electronics board sending data over ethernet.
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQETHHEADER_HPP_
#define DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQETHHEADER_HPP_

#include <cstdint>
#include <ostream>

namespace dunedaq::detdataformats {

/**
 * @brief DAQEthHeader is a versioned and unified structure for every FE electronics.
 */
struct DAQEthHeader 
{
  using word_t = uint64_t; // NOLINT(build/unsigned)

  //BELOW COMMENTED OUT TO MAKE FRAME 899 INSTEAD OF 900 WORDS
  //word_t version : 6, det_id : 6, crate_id : 10, slot_id : 4, stream_id : 8, reserved : 6, seq_id : 12, block_length : 12;
  word_t timestamp : 64;

  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    return uint64_t(timestamp); // NOLINT(build/unsigned)
  } 
};

inline std::ostream&
operator<<(std::ostream& o, DAQEthHeader const& h)
{
  return o << "Version: N/A DetID: N/A CrateID: N/A"
           << " SlotID: N/A StreamID: N/A"
           << " SequenceID: N/A Block length: N/A"
	   << " Timestamp: " << h.get_timestamp() << '\n';
}

} // namespace dunedaq::detdataformats

#endif // DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQETHHEADER_HPP_

/**
 * @file DAQHeader.hpp Common header structure that is used by 
 * every FrontEnd electronics board.
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQHEADER_HPP_
#define DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQHEADER_HPP_

#include <cstdint>
#include <ostream>

namespace dunedaq::detdataformats {

/**
 * @brief DAQHeader is a versioned and unified structure for every FE electronics.
 */
struct DAQHeader 
{
  using word_t = uint32_t; // NOLINT(build/unsigned)

  word_t version : 6, det_id : 6, crate_id : 10, slot_id : 4, link_id : 6;
  word_t timestamp_1 : 32;
  word_t timestamp_2 : 32;

  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    return uint64_t(timestamp_1) | (uint64_t(timestamp_2) << 32); // NOLINT(build/unsigned)
  } 
};

inline std::ostream&
operator<<(std::ostream& o, DAQHeader const& h)
{
  return o << "Version:" << unsigned(h.version) << " DetID:" << unsigned(h.det_id) << " CrateID:" << unsigned(h.crate_id)
           << " SlotID:" << unsigned(h.slot_id) << " LinkID:" << unsigned(h.link_id)
           << " Timestamp: " << h.get_timestamp() << '\n';
}

} // namespace dunedaq::detdataformats

#endif // DETDATAFORMATS_INCLUDE_DETDATAFORMATS_DAQHEADER_HPP_

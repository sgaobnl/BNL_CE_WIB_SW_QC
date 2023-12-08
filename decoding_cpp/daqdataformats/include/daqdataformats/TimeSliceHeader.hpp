/**
 * @file TimeSliceHeaderData.hpp  TimeSliceHeaderData struct definition
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICEHEADER_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICEHEADER_HPP_

#include "daqdataformats/ComponentRequest.hpp"
#include "daqdataformats/SourceID.hpp"
#include "daqdataformats/Types.hpp"

#include <cstddef>
#include <limits>
#include <ostream>
#include <string>
#include <vector>

namespace dunedaq::daqdataformats {

/**
 * @brief Additional data fields associated with a TimeSliceHeader
 */
struct TimeSliceHeader
{
  /**
   * @brief Marker bytes to identify a TimeSliceHeader entry in a raw data stream
   */
  static constexpr uint32_t s_timeslice_header_marker = 0x55556666; // NOLINT(build/unsigned)

  /**
   * @brief The current version of the TimeSliceHeader
   */
  static constexpr uint32_t s_timeslice_header_version = 2; // NOLINT(build/unsigned)

  /**
   * @brief Marker bytes used to identify a TimeSliceHeader struct in a raw data stream
   */
  uint32_t timeslice_header_marker = s_timeslice_header_marker; // NOLINT(build/unsigned)

  /**
   * @brief Version of the TimeSliceHeader structure
   */
  uint32_t version = s_timeslice_header_version; // NOLINT(build/unsigned)

  /**
   * @brief Slice number of this TimeSlice within the stream
   */
  timeslice_number_t timeslice_number{ TypeDefaults::s_invalid_timeslice_number };

  /**
   * @brief Run Number for the TimeSlice
   */
  run_number_t run_number{ TypeDefaults::s_invalid_run_number };

  /**
   * @brief Padding to ensure 64-bit alignment
   */
  uint32_t unused{ 0xFFFFFFFF }; // NOLINT(build/unsigned)

  SourceID element_id;
};
static_assert(sizeof(TimeSliceHeader) == 32, "TimeSliceHeader struct size different than expected!");
static_assert(offsetof(TimeSliceHeader, timeslice_header_marker) == 0,
              "TimeSliceHeader timeslice_header_marker field not at expected offset!");
static_assert(offsetof(TimeSliceHeader, version) == 4, "TimeSliceHeader version field not at expected offset!");
static_assert(offsetof(TimeSliceHeader, timeslice_number) == 8,
              "TimeSliceHeader timeslice_number field not at expected offset!");
static_assert(offsetof(TimeSliceHeader, run_number) == 16, "TimeSliceHeader run_number field not at expected offset!");
static_assert(offsetof(TimeSliceHeader, unused) == 20, "TimeSliceHeader unused field not at expected offset!");
static_assert(offsetof(TimeSliceHeader, element_id) == 24, "TimeSliceHeader source_id field not at expected offset!");

/**
 * @brief Stream a TimeSliceHeader instance in human-readable form
 * @param o Stream to write to
 * @param hdr TimeSliceHeader to write
 * @return Stream instance for continued streaming
 */
inline std::ostream&
operator<<(std::ostream& o, TimeSliceHeader const& hdr)
{
  return o << "check_word: " << std::hex << hdr.timeslice_header_marker << std::dec << ", "
           << "version: " << hdr.version << ", "

           << "timeslice_number: " << hdr.timeslice_number << ", "
           << "run_number: " << hdr.run_number << ", "
           << "element_id: { " << hdr.element_id << " }";
}

/**
 * @brief Read a TimeSliceHeader instance from a string stream
 * @param is Stream to read from
 * @param hdr TimeSliceHeader toread
 * @return Stream instance for continued streaming
 */
inline std::istream&
operator>>(std::istream& o, TimeSliceHeader& hdr)
{
  std::string tmp;
  return o >> tmp >> std::hex >> hdr.timeslice_header_marker >> std::dec >> tmp >> tmp >> hdr.version >> tmp >> tmp >>
         hdr.timeslice_number >> tmp >> tmp >> hdr.run_number >> tmp >> tmp >> tmp >> hdr.element_id;
}

} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICEHEADER_HPP_

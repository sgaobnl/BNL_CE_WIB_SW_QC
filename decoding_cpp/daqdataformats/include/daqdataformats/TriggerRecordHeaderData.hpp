/**
 * @file TriggerRecordHeaderData.hpp  TriggerRecordHeaderData struct definition
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADERDATA_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADERDATA_HPP_

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
 * @brief Additional data fields associated with a TriggerRecordHeader
 */
struct TriggerRecordHeaderData
{
  /**
   * @brief Magic bytes to identify a TriggerRecordHeader entry in a raw data stream
   */
  static constexpr uint32_t s_trigger_record_header_magic = 0x33334444; // NOLINT(build/unsigned)

  /**
   * @brief The current version of the TriggerRecordHeader
   */
  static constexpr uint32_t s_trigger_record_header_version = 3; // NOLINT(build/unsigned)

  /**
   * @brief An invalid number of components
   */
  static constexpr uint64_t s_invalid_number_components = // NOLINT(build/unsigned)
    std::numeric_limits<uint64_t>::max();                 // NOLINT(build/unsigned)

  /**
   * @brief By default, all error bits are unset
   */
  static constexpr uint32_t s_default_error_bits = 0; // NOLINT(build/unsigned)

  /**
   * @brief Magic bytes used to identify a TriggerRecordHeaderData struct in a raw data stream
   */
  uint32_t trigger_record_header_marker = s_trigger_record_header_magic; // NOLINT(build/unsigned)

  /**
   * @brief Version of the TriggerRecordHeaderData structure
   */
  uint32_t version = s_trigger_record_header_version; // NOLINT(build/unsigned)

  /**
   * @brief Trigger Number
   */
  trigger_number_t trigger_number{ TypeDefaults::s_invalid_trigger_number };

  /**
   * @brief Timestamp of the TriggerDecision
   */
  timestamp_t trigger_timestamp{ TypeDefaults::s_invalid_timestamp };

  /**
   * @brief Number of ComponentRequest objects stored in the TriggerRecordHeader
   */
  uint64_t num_requested_components{ s_invalid_number_components }; // NOLINT(build/unsigned)

  /**
   * @brief Run Number for the TriggerRecord
   */
  run_number_t run_number{ TypeDefaults::s_invalid_run_number };

  /**
   * @brief Error bits for the TriggerRecord
   */
  uint32_t error_bits{ s_default_error_bits }; // NOLINT(build/unsigned)

  /**
   * @brief Type of the TriggerDecision
   */
  trigger_type_t trigger_type{ TypeDefaults::s_invalid_trigger_type };

  /**
   * @brief Sequence number of this TriggerRecord within the trigger response
   */
  sequence_number_t sequence_number{ TypeDefaults::s_invalid_sequence_number };
  /**
   * @brief Maximum sequence number of TriggerRecords corresponding to this trigger
   */
  sequence_number_t max_sequence_number{ TypeDefaults::s_invalid_sequence_number };

  /**
   * @brief Padding to ensure 64-bit alignment
   */
  uint16_t unused{ 0xFFFF }; // NOLINT(build/unsigned)

  SourceID element_id;
};

  static_assert(TriggerRecordHeaderData::s_trigger_record_header_version == 3, "This is intentionally designed to tell the developer to update the static_assert checks (including this one) when the version is bumped");

static_assert(sizeof(TriggerRecordHeaderData) == 56, "TriggerRecordHeaderData struct size different than expected!");
static_assert(offsetof(TriggerRecordHeaderData, trigger_record_header_marker) == 0,
              "TriggerRecordHeaderData trigger_record_header_marker field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, version) == 4,
              "TriggerRecordHeaderData version field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, trigger_number) == 8,
              "TriggerRecordHeaderData trigger_number field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, trigger_timestamp) == 16,
              "TriggerRecordHeaderData trigger_timestamp field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, num_requested_components) == 24,
              "TriggerRecordHeaderData num_requested_components field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, run_number) == 32,
              "TriggerRecordHeaderData run_number field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, error_bits) == 36,
              "TriggerRecordHeaderData error_bits field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, trigger_type) == 40,
              "TriggerRecordHeaderData trigger_type field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, sequence_number) == 42,
              "TriggerRecordHeaderData sequence_number field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, max_sequence_number) == 44,
              "TriggerRecordHeaderData max_sequence_number field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, unused) == 46,
              "TriggerRecordHeaderData unused field not at expected offset!");
static_assert(offsetof(TriggerRecordHeaderData, element_id) == 48,
              "TriggerRecordHeaderData source_id field not at expected offset!");

/**
 * @brief This enumeration should list all defined error bits, as well as a short documentation of their meaning
 */
enum class TriggerRecordErrorBits : size_t
{
  kIncomplete = 0,    ///< Indicates a trigger record with incomplete fragments
  kMismatch = 1,      ///< We have as many fragments as requested but they do not match the requested components
  kUnassigned2 = 2,   ///< Error bit 2 is not assigned
  kUnassigned3 = 3,   ///< Error bit 3 is not assigned
  kUnassigned4 = 4,   ///< Error bit 4 is not assigned
  kUnassigned5 = 5,   ///< Error bit 5 is not assigned
  kUnassigned6 = 6,   ///< Error bit 6 is not assigned
  kUnassigned7 = 7,   ///< Error bit 7 is not assigned
  kUnassigned8 = 8,   ///< Error bit 8 is not assigned
  kUnassigned9 = 9,   ///< Error bit 9 is not assigned
  kUnassigned10 = 10, ///< Error bit 10 is not assigned
  kUnassigned11 = 11, ///< Error bit 11 is not assigned
  kUnassigned12 = 12, ///< Error bit 12 is not assigned
  kUnassigned13 = 13, ///< Error bit 13 is not assigned
  kUnassigned14 = 14, ///< Error bit 14 is not assigned
  kUnassigned15 = 15, ///< Error bit 15 is not assigned
  kUnassigned16 = 16, ///< Error bit 16 is not assigned
  kUnassigned17 = 17, ///< Error bit 17 is not assigned
  kUnassigned18 = 18, ///< Error bit 18 is not assigned
  kUnassigned19 = 19, ///< Error bit 19 is not assigned
  kUnassigned20 = 20, ///< Error bit 20 is not assigned
  kUnassigned21 = 21, ///< Error bit 21 is not assigned
  kUnassigned22 = 22, ///< Error bit 22 is not assigned
  kUnassigned23 = 23, ///< Error bit 23 is not assigned
  kUnassigned24 = 24, ///< Error bit 24 is not assigned
  kUnassigned25 = 25, ///< Error bit 25 is not assigned
  kUnassigned26 = 26, ///< Error bit 26 is not assigned
  kUnassigned27 = 27, ///< Error bit 27 is not assigned
  kUnassigned28 = 28, ///< Error bit 28 is not assigned
  kUnassigned29 = 29, ///< Error bit 29 is not assigned
  kUnassigned30 = 30, ///< Error bit 30 is not assigned
  kUnassigned31 = 31, ///< Error bit 31 is not assigned
  kInvalid = 32       ///< Error bit 32 and higher are not valid (error_bits is only 32 bits)
};

/**
 * @brief Stream a TriggerRecordHeaderData instance in human-readable form
 * @param o Stream to write to
 * @param hdr TriggerRecordHeaderData to write
 * @return Stream instance for continued streaming
 */
inline std::ostream&
operator<<(std::ostream& o, TriggerRecordHeaderData const& hdr)
{
  return o << "check_word: " << std::hex << hdr.trigger_record_header_marker << std::dec << ", "
           << "version: " << hdr.version << ", "

           << "trigger_number: " << hdr.trigger_number << ", "
           << "run_number: " << hdr.run_number << ", "
           << "trigger_timestamp: " << hdr.trigger_timestamp << ", "
           << "trigger_type: " << hdr.trigger_type << ", "

           << "error_bits: " << hdr.error_bits << ", "

           << "num_requested_components: " << hdr.num_requested_components << ", "
           << "sequence_number: " << hdr.sequence_number << ", "
           << "max_sequence_number: " << hdr.max_sequence_number << ", "
           << "element_id: { " << hdr.element_id << " }";
}

/**
 * @brief Read a TriggerRecordHeaderData instance from a string stream
 * @param is Stream to read from
 * @param hdr TriggerRecordHeaderData toread
 * @return Stream instance for continued streaming
 */
inline std::istream&
operator>>(std::istream& o, TriggerRecordHeaderData& hdr)
{
  std::string tmp;
  return o >> tmp >> std::hex >> hdr.trigger_record_header_marker >> std::dec >> tmp >> tmp >> hdr.version >> tmp >>
         tmp >> hdr.trigger_number >> tmp >> tmp >> hdr.run_number >> tmp >> tmp >> hdr.trigger_timestamp >> tmp >>
         tmp >> hdr.trigger_type >> tmp >> tmp >> hdr.error_bits >> tmp >> tmp >> hdr.num_requested_components >> tmp >>
         tmp >> hdr.sequence_number >> tmp >> tmp >> hdr.max_sequence_number >> tmp >> tmp >> tmp >> hdr.element_id;
}

} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADERDATA_HPP_

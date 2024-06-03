/**
 * @file Types.hpp  Types used in Data Structures
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TYPES_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TYPES_HPP_

#include <cstdint>
#include <limits>

namespace dunedaq::daqdataformats {

/**
 * @brief Type used to represent run number
 */
using run_number_t = uint32_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent trigger number
 */
using trigger_number_t = uint64_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent Fragment type ID
 */
using fragment_type_t = uint32_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent Fragment size
 */
using fragment_size_t = uint64_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent DUNE timing system timestamps
 */
using timestamp_t = uint64_t;     // NOLINT(build/unsigned)
using timestamp_diff_t = int64_t; ///< Used to represent differences between timestamps
/**
 * @brief Type used to represent Trigger Decision trigger types
 */
using trigger_type_t = uint16_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent sequence within a trigger record
 */
using sequence_number_t = uint16_t; // NOLINT(build/unsigned)
/**
 * @brief Type used to represent timeslice number
 */
using timeslice_number_t = uint64_t; // NOLINT(build/unsigned)

/**
 * @brief Default values for daqdataformats types
 */
class TypeDefaults
{
public:
  static constexpr run_number_t s_invalid_run_number =
    std::numeric_limits<run_number_t>::max(); ///< An invalid run number
  static constexpr trigger_number_t s_invalid_trigger_number =
    std::numeric_limits<trigger_number_t>::max(); ///< An invalid trigger number
  static constexpr fragment_type_t s_invalid_fragment_type =
    std::numeric_limits<fragment_type_t>::max(); ///< An invalid fragment type
  static constexpr fragment_size_t s_invalid_fragment_size =
    0; ///< Invalid size for a Fragment (as FragmentHeader is counted as well)
  static constexpr timestamp_t s_invalid_timestamp = std::numeric_limits<timestamp_t>::max(); ///< An invalid timestamp
  static constexpr timestamp_diff_t s_invalid_timestamp_diff =
    std::numeric_limits<timestamp_diff_t>::max(); ///< An invalid timestamp difference

  static constexpr trigger_type_t s_invalid_trigger_type =
    std::numeric_limits<trigger_type_t>::max(); ///< An invalid trigger type
  static constexpr sequence_number_t s_invalid_sequence_number =
    std::numeric_limits<sequence_number_t>::max(); // An invalid sequence number
  static constexpr timeslice_number_t s_invalid_timeslice_number =
    std::numeric_limits<timeslice_number_t>::max(); ///< An invalid timeslice number
};

} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TYPES_HPP_

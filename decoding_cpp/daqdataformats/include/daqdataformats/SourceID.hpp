/**
 * @file SourceID.hpp Identification for the origin of a dunedaq::daqdataformats::Fragment instance in the DAQ
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_SOURCEID_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_SOURCEID_HPP_

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <istream>
#include <limits>
#include <ostream>
#include <sstream>
#include <string>
#include <tuple>

namespace dunedaq::daqdataformats {

/**
 * @brief SourceID is a generalized representation of the source of a
 * piece of data in the DAQ. That source could be a physical location
 * in the detector, a running process in the DAQ
 * (e.g. a dataflow app, the source of a data request), etc.
 */
struct SourceID
{

  using Version_t = uint16_t;   // NOLINT(build/unsigned)
  using Subsystem_t = uint16_t; // NOLINT(build/unsigned)
  using ID_t = uint32_t;        // NOLINT(build/unsigned)

  /**
   * @brief The Subsystem enum describes the kind of source we're dealing with
   */

  enum class Subsystem : Subsystem_t
  {
    kUnknown = 0,
    kDetectorReadout = 1,
    kHwSignalsInterface = 2,
    kTrigger = 3,
    kTRBuilder = 4
  };

  /**
   * @brief The version of this SourceID struct.
   */
  static constexpr Version_t s_source_id_version =
    2; // Taking SourceID as the direct successor of GeoID which had version 1

  /**
   * @brief A value for the id meant to convey that it doesn't identify a data source and shouldn't be worked with
   */
  static constexpr ID_t s_invalid_id = std::numeric_limits<ID_t>::max();

  /**
   * @brief Version number of the SourceID
   */
  Version_t version{ s_source_id_version };
  /**
   * @brief The general subsystem of the source of the data
   */
  Subsystem subsystem{ Subsystem::kUnknown };

  /**
   * @brief Unique identifier of the source of the data
   */
  ID_t id{ s_invalid_id };

  SourceID() = default;

  SourceID(const Subsystem& subsystem_arg, const ID_t& id_arg)
    : subsystem(subsystem_arg)
    , id(id_arg)
  {}

  std::string to_string() const
  {
    std::ostringstream ostr;
    ostr << subsystem_to_string(subsystem) << "_0x" << std::hex << std::setfill('0') << std::setw(2 * sizeof(id)) << id;
    return ostr.str();
  }

  bool is_in_valid_state() const noexcept { return subsystem != Subsystem::kUnknown && id != s_invalid_id; }

  /**
   * @brief Comparison operators to allow SourceID to be used in std::map
   */
  inline bool operator<(const SourceID& other) const noexcept;
  inline bool operator!=(const SourceID& other) const noexcept;
  inline bool operator==(const SourceID& other) const noexcept;

  inline static std::string subsystem_to_string(const Subsystem& type);
  inline static Subsystem string_to_subsystem(const std::string& typestring);
};

} // namespace dunedaq::daqdataformats

#include "detail/SourceID.hxx"

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_SOURCEID_HPP_

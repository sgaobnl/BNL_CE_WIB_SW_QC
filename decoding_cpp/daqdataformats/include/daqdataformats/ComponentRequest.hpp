/**
 * @file ComponentRequest.hpp Represents the requested timestamp range for a single component
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_COMPONENTREQUEST_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_COMPONENTREQUEST_HPP_

#include "daqdataformats/SourceID.hpp"
#include "daqdataformats/Types.hpp"

#include <cstddef>
#include <iostream>
#include <ostream>
#include <string>

namespace dunedaq::daqdataformats {

/**
 * @brief A request sent to a Component, including the SourceID of the component and the window offset and width
 */
struct ComponentRequest
{
  /**
   * @brief The current version of the ComponentRequest
   */
  static constexpr uint32_t s_component_request_version = 2; // NOLINT(build/unsigned)

  /**
   * @brief The version number of this ComponentRequest
   */
  uint32_t version{ s_component_request_version }; // NOLINT(build/unsigned)
  uint32_t unused{ 0xFFFFFFFF };                   ///< Padding to ensure 64b alignment // NOLINT(build/unsigned)

  SourceID component; ///< The Requested Component

  /**
   * @brief Start of the data collection window
   */
  timestamp_t window_begin{ TypeDefaults::s_invalid_timestamp };

  /**
   * @brief End of the data collection window
   */
  timestamp_t window_end{ TypeDefaults::s_invalid_timestamp };

  ComponentRequest() = default;
  inline ComponentRequest(SourceID const& comp, timestamp_t const& wbegin, timestamp_t const& wend);
};

  static_assert(ComponentRequest::s_component_request_version == 2, "This is intentionally designed to tell the developer to update the static_assert checks (including this one) when the version is bumped");

static_assert(sizeof(ComponentRequest) == 32, "ComponentRequest struct size different than expected!");
static_assert(offsetof(ComponentRequest, version) == 0, "ComponentRequest version field not at expected offset");
static_assert(offsetof(ComponentRequest, unused) == 4, "ComponentRequest unused field not at expected offset");
static_assert(offsetof(ComponentRequest, component) == 8, "ComponentRequest component field not at expected offset");
static_assert(offsetof(ComponentRequest, window_begin) == 16,
              "ComponentRequest window_begin field not at expected offset");
static_assert(offsetof(ComponentRequest, window_end) == 24, "ComponentRequest window_end field not at expected offset");

/**
 * @brief Write out a ComponentRequest in human-readable form
 * @param o Output stream
 * @param cr ComponentRequest to write
 * @return Stream instance for continued streaming
 */
inline std::ostream&
operator<<(std::ostream& o, ComponentRequest const& cr)
{
  return o << cr.component << ", begin: " << cr.window_begin << ", end: " << cr.window_end;
}

/**
 * @brief Read a ComponentRequest from a string stream
 * @param is Input stream
 * @param cr ComponentRequest to read
 * @return Stream instance for continued streaming
 */
inline std::istream&
operator>>(std::istream& is, ComponentRequest& cr)
{
  std::string tmp;
  return is >> cr.component >> tmp >> tmp >> cr.window_begin >> tmp >> tmp >> cr.window_end;
}

ComponentRequest::ComponentRequest(SourceID const& comp, timestamp_t const& wbegin, timestamp_t const& wend)
  : version(s_component_request_version)
  , component(comp)
  , window_begin(wbegin)
  , window_end(wend)
{}
} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_COMPONENTREQUEST_HPP_

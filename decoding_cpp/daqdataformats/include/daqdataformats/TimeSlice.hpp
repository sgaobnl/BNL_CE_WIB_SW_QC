/**
 * @file TimeSlice.hpp  TimeSlice class definition
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICE_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICE_HPP_

#include "daqdataformats/Fragment.hpp"
#include "daqdataformats/TimeSliceHeader.hpp"
#include "daqdataformats/Types.hpp"

#include <memory>
#include <utility>
#include <vector>

namespace dunedaq::daqdataformats {

/**
 * @brief C++ Representation of a DUNE TimeSlice, consisting of a TimeSliceHeader object and a vector of
 * pointers to Fragment objects
 */
class TimeSlice
{
public:
  /**
   * @brief Construct a TimeSlice, filling in header fields
   */
  inline explicit TimeSlice(timeslice_number_t timeslice_number, run_number_t run_number);

  /**
   * @brief Construct a TimeSlice using the given TimeSliceHeader
   * @param header TimeSliceHeader to *copy* into the TimeSlice
   */
  inline explicit TimeSlice(TimeSliceHeader const& header);

  virtual ~TimeSlice() = default; ///< TimeSlice default destructor

  TimeSlice(TimeSlice const&) = delete;            ///< TimeSlices are not copy-constructible
  TimeSlice(TimeSlice&&) = default;                ///< Default TimeSlice move constructor
  TimeSlice& operator=(TimeSlice const&) = delete; ///< TimeSlices are not copy-assignable
  TimeSlice& operator=(TimeSlice&&) = default;     ///< Default TimeSlice move assignment operator

  /**
   * @brief Get a copy of the TimeSliceHeader struct
   * @return A copy of the TimeSliceHeader struct
   */
  TimeSliceHeader get_header() const { return m_header; }
  /**
   * @brief Set the TimeSliceHeader to the given TimeSliceHeader object
   * @param header new TimeSliceHeader to use
   */
  void set_header(TimeSliceHeader header) { m_header = header; }

  /**
   * @brief Get a handle to the Fragments
   * @return A reference to the Fragments vector
   */
  const std::vector<std::unique_ptr<Fragment>>& get_fragments_ref() const { return m_fragments; }

  /**
   * @brief Set the Fragments vector to the given vector of Fragments
   * @param fragments Fragments vector to use
   */
  void set_fragments(std::vector<std::unique_ptr<Fragment>>&& fragments) { m_fragments = std::move(fragments); }

  /**
   * @brief Add a Fragment pointer to the Fragments vector
   * @param fragment Fragment to add
   */
  void add_fragment(std::unique_ptr<Fragment>&& fragment) { m_fragments.emplace_back(std::move(fragment)); }

  /**
   * @brief Set the SourceID for this TimeSlice
   * @param source_id SourceID value to set
   */
  void set_element_id(SourceID source_id) { m_header.element_id = source_id; }

  /**
   * @brief Get size of trigger record from underlying TriggerRecordHeader and Fragments
   */
  size_t get_total_size_bytes() const
  {
    size_t total_size = sizeof(get_header());

    for (auto const& frag_ptr : m_fragments)
      total_size += frag_ptr->get_size();

    return total_size;
  }

private:
  TimeSliceHeader m_header;                           ///< TimeSliceHeader object
  std::vector<std::unique_ptr<Fragment>> m_fragments; ///< Vector of unique_ptrs to Fragment objects
};

//-------

TimeSlice::TimeSlice(timeslice_number_t timeslice_number, run_number_t run_number)
  : m_header()
  , m_fragments()
{
  m_header.timeslice_number = timeslice_number;
  m_header.run_number = run_number;
}

TimeSlice::TimeSlice(TimeSliceHeader const& header)
  : m_header(header)
  , m_fragments()
{}

} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TIMESLICE_HPP_

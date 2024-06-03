/**
 * @file Fragment.hpp Data Fragment Interface
 *
 * This class respresents the data response of one element to a Dataflow DataRequest message.
 * This version is not serializable, and classes wanting to stream it/write it to disk must
 * also fetch the data associated with the Fragment.
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_FRAGMENT_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_FRAGMENT_HPP_

#include "daqdataformats/FragmentHeader.hpp"
#include "daqdataformats/SourceID.hpp"
#include "daqdataformats/Types.hpp"

#include <bitset>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <new>
#include <numeric>
#include <stdexcept>
#include <utility>
#include <vector>

namespace dunedaq {

namespace daqdataformats {

/**
 * @brief C++ Representation of a DUNE Fragment, wrapping the flat byte array that is the Fragment's "actual" form
 */
class Fragment
{
public:
  /**
   * @brief Describes how the "existing Fragment buffer" Constructor should treat the given buffer
   */
  enum class BufferAdoptionMode
  {
    kReadOnlyMode,   ///< Just use the buffer in non-owning mode
    kTakeOverBuffer, ///< Take over control of the buffer
    kCopyFromBuffer  ///< Copy the contents of the buffer into a new Fragment array
  };

  /**
   * @brief Fragment constructor using a vector of buffer pointers
   * @param pieces Vector of pairs of pointer/size pairs used to initialize Fragment payload
   */
  inline explicit Fragment(const std::vector<std::pair<void*, size_t>>& pieces);
  /**
   * @brief Fragment constructor using a buffer and size
   * @param buffer Pointer to Fragment payload
   * @param size Size of payload
   */
  inline Fragment(void* buffer, size_t size);
  /**
   * @brief Framgnet constructor using existing Fragment array
   * @param existing_fragment_buffer Pointer to existing Fragment array
   * @param adoption_mode How the constructor should treat the existing_fragment_buffer
   */
  inline explicit Fragment(void* existing_fragment_buffer, BufferAdoptionMode adoption_mode);

  Fragment(Fragment const&) = delete;            ///< Fragment copy constructor is deleted
  Fragment& operator=(Fragment const&) = delete; ///< Fragment copy assignment operator is deleted
  Fragment(Fragment&& other)
  {
    m_alloc = other.m_alloc;
    other.m_alloc = false;
    m_data_arr = other.m_data_arr;
  }
  Fragment& operator=(Fragment&& other)
  {
    m_alloc = other.m_alloc;
    other.m_alloc = false;
    m_data_arr = other.m_data_arr;
    return *this;
  }

  /**
   * @brief Fragment destructor
   */
  inline ~Fragment();
  /**
   * @brief Get a copy of the FragmentHeader struct
   * @return A copy of the FragmentHeader struct stored in this Fragment
   */
  FragmentHeader get_header() const { return *header_(); }
  /**
   * @brief Copy fields from the provided header in this Fragment's header
   * @param header Header to copy into the Fragment data array
   *
   * The size FragmentHeader field is *not* copied from the given FragmentHeader
   */
  inline void set_header_fields(const FragmentHeader& header);

  /**
   * @brief Get a pointer to the Fragment's data array to read its contents directly
   * @return Pointer to the Fragment's data array
   */
  const void* get_storage_location() const { return m_data_arr; }

  // Header setters and getters
  /**
   * @brief Get the trigger_number field from the header
   * @return The trigger_number header field
   */
  trigger_number_t get_trigger_number() const { return header_()->trigger_number; }
  /**
   * @brief Set the trigger_number for the Fragment
   * @param trigger_number Value of trigger_number to set
   */
  void set_trigger_number(trigger_number_t trigger_number) { header_()->trigger_number = trigger_number; }
  /**
   * @brief Get the run_number field from the header
   * @return The run_number header field
   */
  run_number_t get_run_number() const { return header_()->run_number; }
  /**
   * @brief Set the run_number for the Fragment
   * @param run_number Value of run_number to set
   */
  void set_run_number(run_number_t run_number) { header_()->run_number = run_number; }

  /**
   * @brief Get the trigger_timestamp field from the header
   * @return The trigger_timestamp header field
   */
  timestamp_t get_trigger_timestamp() const { return header_()->trigger_timestamp; }
  /**
   * @brief Set the trigger_timestamp for the Fragment
   * @param trigger_timestamp Value of trigger_timestamp to set
   */
  void set_trigger_timestamp(timestamp_t trigger_timestamp) { header_()->trigger_timestamp = trigger_timestamp; }
  /**
   * @brief Get the window_begin field from the header
   * @return The window_begin header field
   */
  timestamp_t get_window_begin() const { return header_()->window_begin; }
  /**
   * @brief Set the window_begin for the Fragment
   * @param window_begin Value of the window_begin to set
   */
  void set_window_begin(timestamp_t window_begin) { header_()->window_begin = window_begin; }
  /**
   * @brief Get the window_end field from the header
   * @return The window_end header field
   */
  timestamp_t get_window_end() const { return header_()->window_end; }
  /**
   * @brief Set the window_end for the Fragment
   * @param window_end Value of the window_end to set
   */
  void set_window_end(timestamp_t window_end) { header_()->window_end = window_end; }

  /**
   * @brief Get the SourceID for the Fragment
   * @return The element_id header field
   */
  SourceID get_element_id() const { return header_()->element_id; }

  /**
   * @brief Set the SourceID for the Fragment
   * @param element_id SourceID to use as element_id
   */
  void set_element_id(SourceID element_id) { header_()->element_id = element_id; }

  /**
   * @brief Get the DetID for the Fragment
   * @return The detector_id header field
   */

  uint16_t get_detector_id() const noexcept { return header_()->detector_id; }

  /**
   * @brief Set the DetID for the Fragment
   * @param detector_id DetID to use as the detector_id 
   */

  void set_detector_id(const uint16_t& detector_id) noexcept { header_()->detector_id = detector_id; }


  /**
   * @brief Get the error_bits header field
   * @return Bitset generated from header's error_bits field
   */
  std::bitset<32> get_error_bits() const { return header_()->error_bits; }
  /**
   * @brief Overwrite the error_bits header field
   * @param error_bits Bitset of error bits to set
   */
  void set_error_bits(std::bitset<32> error_bits) { header_()->error_bits = error_bits.to_ulong(); }
  /**
   * @brief Get the value of a designated error bit
   * @param bit Bit to query
   * @return Value of bit (true/false)
   */
  bool get_error_bit(FragmentErrorBits bit) const { return get_error_bits()[static_cast<size_t>(bit)]; }

  /**
   * @brief Set the designated error bit
   * @param bit Bit to set
   * @param value Value (true/false) for the error bit
   */
  inline void set_error_bit(FragmentErrorBits bit, bool value);

  /**
   * @brief Get the fragment_type_t value stored in the header
   * @return Current value of the fragment_type header field
   */
  fragment_type_t get_fragment_type_code() const { return header_()->fragment_type; }
  /**
   * @brief Get the fragment_type header field
   * @return Current value of the fragment_type header field
   */
  FragmentType get_fragment_type() const { return static_cast<FragmentType>(get_fragment_type_code()); }
  /**
   * @brief Set the fragment_type header field
   * @param fragment_type Value to set
   */
  void set_type(FragmentType fragment_type) { header_()->fragment_type = static_cast<fragment_type_t>(fragment_type); }

  /**
   * @brief Get the sequence_number field from the header
   * @return The sequence_number header field
   */
  sequence_number_t get_sequence_number() const { return header_()->sequence_number; }
  /**
   * @brief Set the sequence_number for the Fragment
   * @param sequence_number Value of sequence_number to set
   */
  void set_sequence_number(sequence_number_t number) { header_()->sequence_number = number; }

  /**
   * @brief Get the total size of the Fragment
   * @return The size of the Fragment, including header and all payload pieces
   */
  fragment_size_t get_size() const { return header_()->size; }

  /**
   * @brief Get the size of the Fragment data
   * @return The size of the Fragment data, payload only
   */
  fragment_size_t get_data_size() const { return header_()->size-sizeof(FragmentHeader); }

  /**
   * @brief Get a pointer to the data payload in the Fragmnet
   * @return Pointer to the data payload in the Fragment
   */
  void* get_data() const
  {
    // Increment header pointer by one to skip header
    return static_cast<void*>(header_() + 1); // NOLINT
  }

private:
  /**
   * @brief Get the FragmentHeader from the m_data_arr array
   * @return Pointer to the FragmentHeader
   */
  FragmentHeader* header_() const { return static_cast<FragmentHeader*>(m_data_arr); }
  void* m_data_arr{ nullptr }; ///< Flat memory containing a FragmentHeader and the data payload
  bool m_alloc{ false };       ///< Whether the Fragment owns the memory pointed by m_data_arr
};

// ------

Fragment::Fragment(const std::vector<std::pair<void*, size_t>>& pieces)
{
  size_t size = sizeof(FragmentHeader) +
                std::accumulate(pieces.begin(), pieces.end(), 0ULL, [](auto& a, auto& b) { return a + b.second; });

  if (size < sizeof(FragmentHeader)) {
    throw std::length_error("The Fragment size is smaller than the Fragment header size.");
  }

  m_data_arr = malloc(size); // NOLINT(build/unsigned)
  if (m_data_arr == nullptr) {
    throw std::bad_alloc();
  }
  m_alloc = true;

  FragmentHeader header;
  header.size = size;
  memcpy(m_data_arr, &header, sizeof(header));

  size_t offset = sizeof(FragmentHeader);
  for (auto& piece : pieces) {
    if (piece.first == nullptr) {
      throw std::invalid_argument("The Fragment buffer point to NULL.");
    }
    memcpy(static_cast<uint8_t*>(m_data_arr) + offset, piece.first, piece.second); // NOLINT(build/unsigned)
    offset += piece.second;
  }
}

Fragment::Fragment(void* buffer, size_t size)
  : Fragment({ std::make_pair(buffer, size) })
{}

Fragment::Fragment(void* existing_fragment_buffer, BufferAdoptionMode adoption_mode)
{
  if (adoption_mode == BufferAdoptionMode::kReadOnlyMode) {
    m_data_arr = existing_fragment_buffer;
  } else if (adoption_mode == BufferAdoptionMode::kTakeOverBuffer) {
    m_data_arr = existing_fragment_buffer;
    m_alloc = true;
  } else if (adoption_mode == BufferAdoptionMode::kCopyFromBuffer) {
    auto header = reinterpret_cast<FragmentHeader*>(existing_fragment_buffer); // NOLINT
    m_data_arr = malloc(header->size);
    if (m_data_arr == nullptr) {
      throw std::bad_alloc();
    }
    m_alloc = true;
    memcpy(m_data_arr, existing_fragment_buffer, header->size);
  }
}

Fragment::~Fragment()
{
  if (m_alloc)
    free(m_data_arr);
}

void
Fragment::set_header_fields(const FragmentHeader& header)
{
  header_()->trigger_number = header.trigger_number;
  header_()->trigger_timestamp = header.trigger_timestamp;
  header_()->window_begin = header.window_begin;
  header_()->window_end = header.window_end;
  header_()->run_number = header.run_number;
  header_()->element_id = header.element_id;
  header_()->detector_id = header.detector_id;
  header_()->error_bits = header.error_bits;
  header_()->fragment_type = header.fragment_type;
  header_()->sequence_number = header.sequence_number;
}

void
Fragment::set_error_bit(FragmentErrorBits bit, bool value)

{
  auto bits = get_error_bits();
  bits[static_cast<size_t>(bit)] = value;
  set_error_bits(bits);
}

} // namespace daqdataformats
} // namespace dunedaq

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_FRAGMENT_HPP_

/**
 * @file TriggerRecordHeader.hpp  TriggerRecordHeader struct definition
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADER_HPP_
#define DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADER_HPP_

#include "daqdataformats/ComponentRequest.hpp"
#include "daqdataformats/SourceID.hpp"
#include "daqdataformats/TriggerRecordHeaderData.hpp"
#include "daqdataformats/Types.hpp"

#include <bitset>
#include <cstddef>
#include <cstring>
#include <new>
#include <ostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace dunedaq::daqdataformats {

/**
 * @brief C++ representation of a TriggerRecordHeader, which wraps a flat array that is the TriggerRecordHeader's
 * "actual" form
 */
class TriggerRecordHeader
{
public:
  /**
   * @brief Construct a TriggerRecordHeader using a vector of ComponentRequest objects
   * @param components Vector of ComponentRequests to copy into TriggerRecordHeader
   */
  inline explicit TriggerRecordHeader(const std::vector<ComponentRequest>& components);

  /**
   * @brief Construct a TriggerRecordHeader using an existing TriggerRecordHeader data array
   * @param existing_trigger_record_header_buffer Pointer to existing TriggerRecordHeader array
   * @param copy_from_buffer Whether to create a copy of the exiting buffer (true) or use that memory without taking
   * ownership (false)
   */
  inline explicit TriggerRecordHeader(void* existing_trigger_record_header_buffer, bool copy_from_buffer = false);

  /**
   * @brief TriggerRecordHeader Copy Constructor
   * @param other TriggerRecordHeader to copy
   */
  inline TriggerRecordHeader(TriggerRecordHeader const& other);
  /**
   * @brief TriggerRecordHeader copy assignment operator
   * @param other TriggerRecordHeader to copy
   * @return Reference to TriggerRecordHeader copy
   */
  inline TriggerRecordHeader& operator=(TriggerRecordHeader const& other);

  TriggerRecordHeader(TriggerRecordHeader&& other)
  {
    m_alloc = other.m_alloc;
    other.m_alloc = false;
    m_data_arr = other.m_data_arr;
  }
  TriggerRecordHeader& operator=(TriggerRecordHeader&& other)
  {
    m_alloc = other.m_alloc;
    other.m_alloc = false;
    m_data_arr = other.m_data_arr;
    return *this;
  }

  /**
   * @brief TriggerRecordHeader destructor
   */
  ~TriggerRecordHeader()
  {
    if (m_alloc)
      free(m_data_arr);
  }

  /**
   * @brief Get a copy of the TriggerRecordHeaderData struct
   * @return A copy of the TriggerRecordHeaderData struct stored in this TriggerRecordHeader
   */
  TriggerRecordHeaderData get_header() const { return *header_(); }

  /**
   * @brief Get the trigger number for this TriggerRecordHeader
   * @return The trigger_number TriggerRecordHeaderData field
   */
  trigger_number_t get_trigger_number() const { return header_()->trigger_number; }
  /**
   * @brief Set the trigger number for this TriggerRecordHeader
   * @param trigger_number Trigger nunmber to set
   */
  void set_trigger_number(trigger_number_t trigger_number) { header_()->trigger_number = trigger_number; }
  /**
   * @brief Get the trigger_timestamp stored in this TriggerRecordHeader
   * @return The trigger_timestamp TriggerRecordHeaderData field
   */
  timestamp_t get_trigger_timestamp() const { return header_()->trigger_timestamp; }
  /**
   * @brief Set the trigger timestamp for this TriggerRecordHeader
   * @param trigger_timestamp Trigger timestamp to set
   */
  void set_trigger_timestamp(timestamp_t trigger_timestamp) { header_()->trigger_timestamp = trigger_timestamp; }

  /**
   * @brief Get the number of ComponentRequest objects stored in this TriggerRecordHeader
   * @return The num_requested_components TriggerRecordHeaderData field
   */
  uint64_t get_num_requested_components() const // NOLINT(build/unsigned)
  {
    return header_()->num_requested_components;
  }

  /**
   * @brief Get the run_number stored in this TriggerRecordHeader
   * @return The run_number TriggerRecordHeaderData field
   */
  run_number_t get_run_number() const { return header_()->run_number; }
  /**
   * @brief Set the run number for this TriggerRecordHeader
   * @param run_number Run number to set
   */
  void set_run_number(run_number_t run_number) { header_()->run_number = run_number; }

  /**
   * @brief Get the error_bits header field as a bitset
   * @return bitset containing error_bits header field
   */
  std::bitset<32> get_error_bits() const { return header_()->error_bits; }
  /**
   * @brief Overwrite error bits using the given bitset
   * @param bits Bitset of error bits to set
   */
  void set_error_bits(std::bitset<32> bits) { header_()->error_bits = bits.to_ulong(); }
  /**
   * @brief Get the value of the given error bit
   * @param bit Bit to get
   * @return Value of bit (true/false)
   */
  bool get_error_bit(TriggerRecordErrorBits bit) const { return get_error_bits()[static_cast<size_t>(bit)]; }
  /**
   * @brief Set the given error bit to the given value
   * @param bit Bit to set
   * @param value Value to set (true/false)
   */
  void set_error_bit(TriggerRecordErrorBits bit, bool value)
  {
    auto bits = get_error_bits();
    bits[static_cast<size_t>(bit)] = value;
    set_error_bits(bits);
  }

  /**
   * @brief Get the trigger_type field from the data struct
   * @return The trigger_type field from the TriggerRecordHeaderData struct
   */
  trigger_type_t get_trigger_type() const { return header_()->trigger_type; }
  /**
   * @brief Set the trigger_type header field to the given value
   * @param trigger_type Value of trigger_type to set
   */
  void set_trigger_type(trigger_type_t trigger_type) { header_()->trigger_type = trigger_type; }

  /**
   * @brief Get the sequence number for this TriggerRecordHeader
   * @return The sequence_number TriggerRecordHeaderData field
   */
  trigger_number_t get_sequence_number() const { return header_()->sequence_number; }
  /**
   * @brief Set the sequence number for this TriggerRecordHeader
   * @param sequence_number Sequence number to set
   */
  void set_sequence_number(sequence_number_t number) { header_()->sequence_number = number; }

  /**
   * @brief Get the maximum sequence number for this TriggerRecordHeader
   * @return The max_sequence_number TriggerRecordHeaderData field
   */
  trigger_number_t get_max_sequence_number() const { return header_()->max_sequence_number; }
  /**
   * @brief Set the maxiumum sequence number for this TriggerRecordHeader
   * @param max_sequence_number Maximum sequence number to set
   */
  void set_max_sequence_number(sequence_number_t number) { header_()->max_sequence_number = number; }

  /**
   * @brief Get the SourceID for this TriggerRecordHeader
   * @return The element_id TriggerRecordHeaderData field
   */
  SourceID get_element_id() const { return header_()->element_id; }
  /**
   * @brief Set the SourceID for this TriggerRecordHeader
   * @param source_id SourceID value to set
   */
  void set_element_id(SourceID source_id) { header_()->element_id = source_id; }

  /**
   * @brief Get the total size of the TriggerRecordHeader
   * @return The size of the TriggerRecordHeader, including header and all component requests
   */
  size_t get_total_size_bytes() const
  {
    return header_()->num_requested_components * sizeof(ComponentRequest) + sizeof(TriggerRecordHeaderData);
  }
  /**
   * @brief Get the location of the flat data array for output
   * @return Pointer to the TriggerRecordHeader data array
   */

  const void* get_storage_location() const { return m_data_arr; }

  /**
   * @brief Access ComponentRequest and copy result
   * @param idx Index to access
   * @return Copy of ComponentRequest at index
   * @throws std::range_error exception if idx is outside of allowable range
   */
  inline ComponentRequest at(size_t idx) const;

  /**
   * @brief Operator[] to access ComponentRequests by index
   * @param idx Index to access
   * @return ComponentRequest reference
   * @throws std::range_error exception if idx is outside of allowable range
   */
  inline ComponentRequest& operator[](size_t idx);

private:
  /**
   * @brief Get the TriggerRecordHeaderData from the m_data_arr array
   * @return Pointer to the TriggerRecordHeaderData
   */
  TriggerRecordHeaderData* header_() const { return static_cast<TriggerRecordHeaderData*>(m_data_arr); }

  void* m_data_arr{
    nullptr
  };                     ///< Flat memory containing a TriggerRecordHeaderData header and an array of ComponentRequests
  bool m_alloc{ false }; ///< Whether the TriggerRecordHeader owns the memory pointed by m_data_arr
};

//------

TriggerRecordHeader::TriggerRecordHeader(const std::vector<ComponentRequest>& components)
{
  size_t size = sizeof(TriggerRecordHeaderData) + components.size() * sizeof(ComponentRequest);

  m_data_arr = malloc(size); // NOLINT(build/unsigned)
  if (m_data_arr == nullptr) {
    throw std::bad_alloc();
  }
  m_alloc = true;

  TriggerRecordHeaderData header;
  header.num_requested_components = components.size();
  std::memcpy(m_data_arr, &header, sizeof(header));

  size_t offset = sizeof(header);
  for (auto const& component : components) {
    std::memcpy(static_cast<uint8_t*>(m_data_arr) + offset, &component, sizeof(component)); // NOLINT
    offset += sizeof(component);
  }
}

TriggerRecordHeader::TriggerRecordHeader(void* existing_trigger_record_header_buffer, bool copy_from_buffer)
{
  if (!copy_from_buffer) {
    m_data_arr = existing_trigger_record_header_buffer;
  } else {
    auto header = reinterpret_cast<TriggerRecordHeaderData*>(existing_trigger_record_header_buffer); // NOLINT
    size_t size = header->num_requested_components * sizeof(ComponentRequest) + sizeof(TriggerRecordHeaderData);

    m_data_arr = malloc(size);
    if (m_data_arr == nullptr) {
      throw std::bad_alloc();
    }
    m_alloc = true;
    std::memcpy(m_data_arr, existing_trigger_record_header_buffer, size);
  }
}

TriggerRecordHeader::TriggerRecordHeader(TriggerRecordHeader const& other)
  : TriggerRecordHeader(other.m_data_arr, true)
{}

TriggerRecordHeader&
TriggerRecordHeader::operator=(TriggerRecordHeader const& other)
{
  if (&other == this)
    return *this;

  if (m_alloc) {
    free(m_data_arr);
  }
  m_data_arr = malloc(other.get_total_size_bytes());
  if (m_data_arr == nullptr) {
    throw std::bad_alloc();
  }
  m_alloc = true;
  std::memcpy(m_data_arr, other.m_data_arr, other.get_total_size_bytes());
  return *this;
}

ComponentRequest
TriggerRecordHeader::at(size_t idx) const
{
  if (idx >= header_()->num_requested_components) {
    throw std::range_error("Supplied ComponentRequest index is larger than the maximum index.");
  }
  // Increment header pointer by one to skip header
  return *(reinterpret_cast<ComponentRequest*>(header_() + 1) + idx); // NOLINT
}

ComponentRequest&
TriggerRecordHeader::operator[](size_t idx)
{
  if (idx >= header_()->num_requested_components) {
    throw std::range_error("Supplied ComponentRequest index is larger than the maximum index.");
  }
  // Increment header pointer by one to skip header
  return *(reinterpret_cast<ComponentRequest*>(header_() + 1) + idx); // NOLINT
}

} // namespace dunedaq::daqdataformats

#endif // DAQDATAFORMATS_INCLUDE_DAQDATAFORMATS_TRIGGERRECORDHEADER_HPP_

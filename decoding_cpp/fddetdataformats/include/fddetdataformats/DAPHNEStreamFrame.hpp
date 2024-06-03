/**
 * @file DAPHNEStreamFrame.hpp
 *
 *  Contains declaration of DAPHNEStreamFrame, a class for accessing 
 *  raw DAPHNE streaming version frames, as produced by the DAPHNE boards
 *
 *  The canonical definition of the PDS DAPHNE format is given in EDMS document 2088726:
 *  https://edms.cern.ch/document/2088726/3
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_DAPHNESTREAMFRAME_HPP_
#define FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_DAPHNESTREAMFRAME_HPP_

#include "detdataformats/DAQHeader.hpp" // For unified DAQ header

#include <algorithm> // For std::min
#include <cassert>   // For assert()
#include <cstdio>
#include <cstdlib>
#include <stdexcept> // For std::out_of_range
#include <cstdint>  // For uint32_t etc

namespace dunedaq::fddetdataformats {

class DAPHNEStreamFrame
{
public:
  // ===============================================================
  // Preliminaries
  // ===============================================================

  // The definition of the format is in terms of 32-bit words
  typedef uint32_t word_t; // NOLINT

  static constexpr int s_bits_per_adc = 14;
  static constexpr int s_bits_per_word = 8 * sizeof(word_t);
  static constexpr int s_channels_per_frame = 4;
  static constexpr int s_adcs_per_channel = 64;
  static constexpr int s_daphnes_per_frame = 1;
  static constexpr int s_num_adc_words = s_channels_per_frame * s_adcs_per_channel * s_bits_per_adc / s_bits_per_word;

  struct Header
  {
    word_t channel_0 : 6, channel_1 : 6, channel_2 : 6, channel_3 : 6, tbd_0 : 8;
    word_t tbd_1 : 32;
  };

  struct Trailer
  {
    word_t tbd : 32;
  };

  // ===============================================================
  // Data members
  // ===============================================================
  detdataformats::DAQHeader daq_header;
  Header header;
  word_t adc_words[s_num_adc_words]; // NOLINT
  Trailer trailer; 

  // ===============================================================
  // Accessors
  // ===============================================================

  uint64_t get_timestamp() const 
  {
    return daq_header.get_timestamp();
  }

  /** @brief Set the 64-bit timestamp of the frame
  */
  void set_timestamp(const uint64_t new_timestamp) // NOLINT(build/unsigned)
  {
    daq_header.timestamp_1 = new_timestamp;
    daq_header.timestamp_2 = new_timestamp >> 32;
  }


  /**
   * @brief Get the @p i ADC value of @p chn in the frame
   */
  uint16_t get_adc(uint i, uint chn) const // NOLINT
  {

    if (i >= s_adcs_per_channel)
      throw std::out_of_range("ADC index out of range");

    if (chn >= s_channels_per_frame)
      throw std::out_of_range("ADC index out of range");

    // find absolute index in frame
    uint j = i*s_channels_per_frame+chn;
    // The index of the first (and sometimes only) word containing the required ADC value
    uint word_index = s_bits_per_adc * j / s_bits_per_word;
    assert(word_index < s_num_adc_words);
    // Where in the word the lowest bit of our ADC value is located
    int first_bit_position = (s_bits_per_adc * j) % s_bits_per_word;
    // How many bits of our desired ADC are located in the `word_index`th word
    int bits_from_first_word = std::min(s_bits_per_adc, s_bits_per_word - first_bit_position);
    uint16_t adc = adc_words[word_index] >> first_bit_position; // NOLINT(build/unsigned)

    if (bits_from_first_word < s_bits_per_adc) {
      assert(word_index + 1 < s_num_adc_words);
      adc |= adc_words[word_index + 1] << bits_from_first_word;
    }
    // Mask out all but the lowest 14 bits;
    return adc & 0x3FFFu;
  }

  /**
   * @brief Set the @p i ADC value of @p chn in the frame to @p val
   */
  void set_adc(uint i, uint chn, uint16_t val) // NOLINT
  {

    if (i >= s_adcs_per_channel)
      throw std::out_of_range("ADC index out of range");

    if (chn >= s_channels_per_frame)
      throw std::out_of_range("ADC index out of range");

    if (val >= (1 << s_bits_per_adc))
      throw std::out_of_range("ADC value out of range");


    // find absolute index in frame
    uint j = i*s_channels_per_frame+chn;
    // The index of the first (and sometimes only) word containing the required ADC value
    int word_index = s_bits_per_adc * j / s_bits_per_word;
    assert(word_index < s_num_adc_words);
    // Where in the word the lowest bit of our ADC value is located
    int first_bit_position = (s_bits_per_adc * j) % s_bits_per_word;
    // How many bits of our desired ADC are located in the `word_index`th word
    int bits_in_first_word = std::min(s_bits_per_adc, s_bits_per_word - first_bit_position);
    uint32_t mask = (1 << (first_bit_position)) - 1;
    adc_words[word_index] = ((val << first_bit_position) & ~mask) | (adc_words[word_index] & mask);
    // If we didn't put the full 14 bits in this word, we need to put the rest in the next word
    if (bits_in_first_word < s_bits_per_adc) {
      assert(word_index + 1 < s_num_adc_words);
      mask = (1 << (s_bits_per_adc - bits_in_first_word)) - 1;
      adc_words[word_index + 1] = ((val >> bits_in_first_word) & mask) | (adc_words[word_index + 1] & ~mask);
    }

  }
};

} // namespace dunedaq::fddetdataformats

#endif // FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_DAPHNESTREAMFRAME_HPP_

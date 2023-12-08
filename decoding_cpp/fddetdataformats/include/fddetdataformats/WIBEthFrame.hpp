/**
 * @file WIBEthFrame.hpp
 *
 * Contains declaration of WIBEthFrame, a class for accessing raw WIB v2 frames, as used in ProtoDUNE-SP-II
 * 
 * The canonical definition of the WIB format is given in EDMS document 2088713: *  https://edms.cern.ch/document/2088713/XXX
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#ifndef FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBETHFRAME_HPP_
#define FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBETHFRAME_HPP_

#include "detdataformats/DAQEthHeader.hpp"

#include <algorithm> // For std::min
#include <cassert>   // For assert()
#include <cstdint>   // For uint32_t etc
#include <cstdio>
#include <cstdlib>
#include <stdexcept> // For std::out_of_range

namespace dunedaq::fddetdataformats {

/**
 *  @brief Class for accessing raw WIB eth frames, as used in ProtoDUNE-II
 *
 *  The canonical definition of the WIB format is given in EDMS document 2088713:
 *  https://edms.cern.ch/document/2088713/XXX
 */
class WIBEthFrame
{
public:
  // ===============================================================
  // Preliminaries
  // ===============================================================

  // The definition of the format is in terms of 64-bit words
  typedef uint64_t word_t; // NOLINT

  static constexpr int s_bits_per_adc = 14;
  static constexpr int s_bits_per_word = 8 * sizeof(word_t);
  static constexpr int s_time_samples_per_frame = 64;
  static constexpr int s_channels_per_half_femb = 64;
  static constexpr int s_half_fembs_per_frame = 1;
  static constexpr int s_num_channels = s_channels_per_half_femb * s_half_fembs_per_frame;
  static constexpr int s_num_adc_words_per_ts = s_num_channels * s_bits_per_adc / s_bits_per_word;
  static constexpr int s_num_adc_words = s_time_samples_per_frame * s_num_channels * s_bits_per_adc / s_bits_per_word;
  

  struct WIBEthHeader
  {	  
    word_t colddata_timestamp_0 : 15;
    word_t pad_0: 1;
    word_t colddata_timestamp_1 : 15;
    word_t pad_1: 1;
    word_t cd: 1;
    word_t crc_err : 2;
    word_t link_valid : 2;
    word_t lol : 1;
    word_t wib_sync : 1;
    word_t femb_sync : 2;
    word_t pulser : 1;
    word_t calibration : 1;
    word_t ready : 1;
    word_t context : 8;
    word_t version : 4;
    word_t channel : 8;
    word_t extra_data; 
  };

  // ===============================================================
  // Data members
  // ===============================================================
  detdataformats::DAQEthHeader daq_header;
  WIBEthHeader header;
  // word_t adc_words[s_num_adc_words_per_ts][s_time_samples_per_frame]; // NOLINT
  word_t adc_words[s_time_samples_per_frame][s_num_adc_words_per_ts]; // NOLINT

  // ===============================================================
  // Accessors
  // ===============================================================

  /**
   * @brief Get the ith ADC value in the frame
   *
   * The ADC words are 14 bits long;
   * wrod_t stored packed in the data structure. 
   * The order is: 64 channels repeated for 64 time samples
   *
   */
  uint16_t get_adc(int i, int sample=0) const // NOLINT(build/unsigned)
  {
    if (i < 0 || i >= s_num_channels)
      throw std::out_of_range("ADC index out of range");

    // The index of the first (and sometimes only) word containing the required ADC value
    int word_index = s_bits_per_adc * i / s_bits_per_word;
    assert(word_index < s_num_adc_words_per_ts);
    // Where in the word the lowest bit of our ADC value is located
    int first_bit_position = (s_bits_per_adc * i) % s_bits_per_word;
    // How many bits of our desired ADC are located in the `word_index`th word
    int bits_from_first_word = std::min(s_bits_per_adc, s_bits_per_word - first_bit_position);
    // uint16_t adc = adc_words[word_index][sample] >> first_bit_position; // NOLINT(build/unsigned)
    uint16_t adc = adc_words[sample][word_index] >> first_bit_position; // NOLINT(build/unsigned)
    // If we didn't get the full 14 bits from this word, we need the rest from the next word
    if (bits_from_first_word < s_bits_per_adc) {
      assert(word_index + 1 < s_num_adc_words_per_ts);
      // adc |= adc_words[word_index + 1][sample] << bits_from_first_word;
      adc |= adc_words[sample][word_index + 1] << bits_from_first_word;
    }
    // Mask out all but the lowest 14 bits;
    return adc & 0x3FFFu;
  }

  /**
   * @brief Set the ith ADC value in the frame to @p val
   */
  void set_adc(int i, int sample, uint16_t val) // NOLINT(build/unsigned)
  {
    if (i < 0 || i >= s_num_channels)
      throw std::out_of_range("ADC index out of range");
    if (val >= (1 << s_bits_per_adc))
      throw std::out_of_range("ADC value out of range");

    // The index of the first (and sometimes only) word containing the required ADC value
    int word_index = s_bits_per_adc * i / s_bits_per_word;
    assert(word_index < s_num_adc_words);
    // Where in the word the lowest bit of our ADC value is located
    int first_bit_position = (s_bits_per_adc * i) % s_bits_per_word;
    // How many bits of our desired ADC are located in the `word_index`th word
    int bits_in_first_word = std::min(s_bits_per_adc, s_bits_per_word - first_bit_position);
    uint64_t mask = (static_cast<uint64_t>(1) << first_bit_position) - 1;
    adc_words[sample][word_index] = ((static_cast<uint64_t>(val) << first_bit_position) & ~mask) | (adc_words[sample][word_index] & mask);
    // If we didn't put the full 14 bits in this word, we need to put the rest in the next word
    if (bits_in_first_word < s_bits_per_adc) {
      assert(word_index + 1 < s_num_adc_words);
      mask = (1 << (s_bits_per_adc - bits_in_first_word)) - 1;
      adc_words[sample][word_index + 1] = ((val >> bits_in_first_word) & mask) | (adc_words[sample][word_index + 1] & ~mask);
    }
  }

  /** @brief Get the starting 64-bit timestamp of the frame
   */
  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    return daq_header.get_timestamp() ; // NOLINT(build/unsigned)
  }

  /** @brief Set the starting 64-bit timestamp of the frame
   */
  void set_timestamp(const uint64_t new_timestamp) // NOLINT(build/unsigned)
  {
    daq_header.timestamp = new_timestamp;
  }

  /** @brief Get the channel identifier of the frame
   */
  uint8_t get_channel() const // NOLINT(build/unsigned)
  {
    return header.channel ; // NOLINT(build/unsigned)
  }

  /** @brief Set the channel identifier of the frame
   */
  void set_channel(const uint8_t new_channel) // NOLINT(build/unsigned)
  {
    header.channel = new_channel;
  }
  
  /** @brief Get the starting 15-bit COLDATA 0 or 1 timestamp of the frame
   * (returned as 16-bit)
   */
  uint16_t get_cd_timestamp(uint8_t cd) const // NOLINT(build/unsigned)
  {
    if (cd == 0) return uint16_t(header.colddata_timestamp_0) ; // NOLINT(build/unsigned)
	else return uint16_t(header.colddata_timestamp_1);
  }  
   
};

} // namespace dunedaq::fddetdataformats

#endif // FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBETHFRAME_HPP_

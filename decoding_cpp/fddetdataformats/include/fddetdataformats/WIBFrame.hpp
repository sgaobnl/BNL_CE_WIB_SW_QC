/**
 * @file WIBFrame.hpp WIB1 bit fields and accessors
 * Originally FelixFrame.hpp from protodune.
 * Original authors M. Vermeulen, R.Sipos 2018
 * Modified by P. Rodrigues on June 2020
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */
#ifndef FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBFRAME_HPP_
#define FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBFRAME_HPP_

#include <bitset>
#include <iostream>
#include <vector>
#include <stdexcept>

namespace dunedaq::fddetdataformats {

using word_t = uint32_t; // NOLINT(build/unsigned)
using adc_t = uint16_t;  // NOLINT(build/unsigned)

/**
 * @brief WIB header struct
 */
struct WIBHeader
{
  word_t sof : 8, version : 5, fiber_no : 3, crate_no : 5, slot_no : 3, reserved_1 : 8;
  word_t mm : 1, oos : 1, reserved_2 : 14, wib_errors : 16;
  word_t timestamp_1;
  word_t timestamp_2 : 16, wib_counter_1 : 15, z : 1;

  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    uint64_t timestamp = timestamp_1 | (static_cast<uint64_t>(timestamp_2) << 32); // NOLINT(build/unsigned)
    if (!z) {
      timestamp |= static_cast<uint64_t>(wib_counter_1) << 48; // NOLINT(build/unsigned)
    }
    return timestamp;
  }
  uint16_t get_wib_counter() const { return z ? wib_counter_1 : 0; } // NOLINT(build/unsigned)

  void set_timestamp(const uint64_t new_timestamp) // NOLINT(build/unsigned)
  {
    timestamp_1 = new_timestamp;
    timestamp_2 = new_timestamp >> 32;
    if (!z) {
      wib_counter_1 = new_timestamp >> 48;
    }
  }
  void set_wib_counter(const uint16_t new_wib_counter) // NOLINT(build/unsigned)
  {
    if (z) {
      wib_counter_1 = new_wib_counter;
    }
  }

  // Print functions for debugging.
  std::ostream& print_hex(std::ostream& o) const
  {
    return o << std::hex << "SOF:" << sof << " version:" << version << " fiber:" << fiber_no << " slot:" << slot_no
             << " crate:" << crate_no << " mm:" << mm << " oos:" << oos << " wib_errors:" << wib_errors
             << " timestamp: " << get_timestamp() << std::dec << '\n';
  }

  std::ostream& print_bits(std::ostream& o) const
  {
    return o << "SOF:" << std::bitset<8>(sof) << " version:" << std::bitset<5>(version)
             << " fiber:" << std::bitset<3>(fiber_no) << " slot:" << std::bitset<5>(slot_no)
             << " crate:" << std::bitset<3>(crate_no) << " mm:" << bool(mm) << " oos:" << bool(oos)
             << " wib_errors:" << std::bitset<16>(wib_errors) << " timestamp: " << get_timestamp() << '\n'
             << " Z: " << z << '\n';
  }
};

inline std::ostream&
operator<<(std::ostream& o, WIBHeader const& h)
{
  return o << "SOF:" << unsigned(h.sof) << " version:" << unsigned(h.version) << " fiber:" << unsigned(h.fiber_no)
           << " slot:" << unsigned(h.slot_no) << " crate:" << unsigned(h.crate_no) << " mm:" << unsigned(h.mm)
           << " oos:" << unsigned(h.oos) << " wib_errors:" << unsigned(h.wib_errors)
           << " timestamp: " << h.get_timestamp() << '\n';
}

/**
 * @brief COLDATA header struct
 */
struct ColdataHeader
{
  word_t s1_error : 4, s2_error : 4, reserved_1 : 8, checksum_a_1 : 8, checksum_b_1 : 8;
  word_t checksum_a_2 : 8, checksum_b_2 : 8, coldata_convert_count : 16;
  word_t error_register : 16, reserved_2 : 16;
  word_t hdr_1 : 4, hdr_3 : 4, hdr_2 : 4, hdr_4 : 4, hdr_5 : 4, hdr_7 : 4, hdr_6 : 4, hdr_8 : 4;

  uint16_t get_checksum_a() const // NOLINT(build/unsigned)
  {
    return static_cast<uint16_t>(checksum_a_1) | (checksum_a_2 << 8); // NOLINT(build/unsigned)
  }
  uint16_t get_checksum_b() const // NOLINT(build/unsigned)
  {
    return static_cast<uint16_t>(checksum_b_1) | (checksum_b_2 << 8); // NOLINT(build/unsigned)
  }
  uint8_t get_hdr(const uint8_t i) const // NOLINT(build/unsigned)
  {
    switch (i) {
      case 1:
        return hdr_1;
      case 2:
        return hdr_2;
      case 3:
        return hdr_3;
      case 4:
        return hdr_4;
      case 5:
        return hdr_5;
      case 6:
        return hdr_6;
      case 7:
        return hdr_7;
      case 8:
        return hdr_8;
    }
    return 0;
  }

  void set_checksum_a(const uint16_t new_checksum_a) // NOLINT(build/unsigned)
  {
    checksum_a_1 = new_checksum_a;
    checksum_a_2 = new_checksum_a >> 8;
  }
  void set_checksum_b(const uint16_t new_checksum_b) // NOLINT(build/unsigned)
  {
    checksum_b_1 = new_checksum_b;
    checksum_b_2 = new_checksum_b >> 8;
  }
  void set_hdr(const uint8_t i, const uint8_t new_hdr) // NOLINT(build/unsigned)
  {
    switch (i) {
      case 1:
        hdr_1 = new_hdr;
        break;
      case 2:
        hdr_2 = new_hdr;
        break;
      case 3:
        hdr_3 = new_hdr;
        break;
      case 4:
        hdr_4 = new_hdr;
        break;
      case 5:
        hdr_5 = new_hdr;
        break;
      case 6:
        hdr_6 = new_hdr;
        break;
      case 7:
        hdr_7 = new_hdr;
        break;
      case 8:
        hdr_8 = new_hdr;
        break;
    }
  }

  // Print functions for debugging.
  std::ostream& print_hex(std::ostream& o) const
  {
    o << std::hex << "s1_error:" << s1_error << " s2_error:" << s2_error << " checksum_a1:" << checksum_a_1
      << " checksum_b1:" << checksum_b_1 << " checksum_a2:" << checksum_a_2 << " checksum_b1:" << checksum_b_2
      << " coldata_convert_count:" << coldata_convert_count << " error_register:" << error_register
      << " hdr_1:" << hdr_1 << " hdr_2:" << hdr_2 << " hdr_3:" << hdr_3 << " hdr_4:" << hdr_4 << " hdr_5:" << hdr_5
      << " hdr_6:" << hdr_6 << " hdr_7:" << hdr_7 << " hdr_8:" << hdr_8;
    return o << '\n';
  }
  std::ostream& print_bits(std::ostream& o) const
  {
    o << "s1_error:" << std::bitset<4>(s1_error) << " s2_error:" << std::bitset<4>(s2_error)
      << " checksum_a1:" << std::bitset<8>(checksum_a_1) << " checksum_b1:" << std::bitset<8>(checksum_b_1)
      << " checksum_a2:" << std::bitset<8>(checksum_a_2) << " checksum_b2:" << std::bitset<8>(checksum_b_2)
      << " coldata_convert_count:" << std::bitset<16>(coldata_convert_count)
      << " error_register:" << std::bitset<16>(error_register) << " hdr_1:" << std::bitset<8>(hdr_1)
      << " hdr_2:" << std::bitset<8>(hdr_2) << " hdr_3:" << std::bitset<8>(hdr_3) << " hdr_4:" << std::bitset<8>(hdr_4)
      << " hdr_5:" << std::bitset<8>(hdr_5) << " hdr_6:" << std::bitset<8>(hdr_6) << " hdr_7:" << std::bitset<8>(hdr_7)
      << " hdr_8:" << std::bitset<8>(hdr_8);
    return o << '\n';
  }
};

inline std::ostream&
operator<<(std::ostream& o, ColdataHeader const& hdr)
{
  o << "s1_error:" << unsigned(hdr.s1_error) << " s2_error:" << unsigned(hdr.s2_error)
    << " checksum_a1:" << unsigned(hdr.checksum_a_1) << " checksum_b1:" << unsigned(hdr.checksum_b_1)
    << " checksum_a2:" << unsigned(hdr.checksum_a_2) << " checksum_b1:" << unsigned(hdr.checksum_b_2)
    << " coldata_convert_count:" << unsigned(hdr.coldata_convert_count)
    << " error_register:" << unsigned(hdr.error_register) << " hdr_1:" << unsigned(hdr.hdr_1)
    << " hdr_2:" << unsigned(hdr.hdr_2) << " hdr_3:" << unsigned(hdr.hdr_3) << " hdr_4:" << unsigned(hdr.hdr_4)
    << " hdr_5:" << unsigned(hdr.hdr_5) << " hdr_6:" << unsigned(hdr.hdr_6) << " hdr_7:" << unsigned(hdr.hdr_7)
    << " hdr_8:" << unsigned(hdr.hdr_8);
  return o << '\n';
}

/**
 * @brief COLDATA segment struct
 */
struct ColdataSegment
{
  static constexpr int s_num_ch_per_seg = 8;

  // This struct contains three words of ADC values that form the main repeating
  // pattern in the COLDATA block.
  word_t adc0ch0_1 : 8, adc1ch0_1 : 8, adc0ch0_2 : 4, adc0ch1_1 : 4, adc1ch0_2 : 4, adc1ch1_1 : 4;
  word_t adc0ch1_2 : 8, adc1ch1_2 : 8, adc0ch2_1 : 8, adc1ch2_1 : 8;
  word_t adc0ch2_2 : 4, adc0ch3_1 : 4, adc1ch2_2 : 4, adc1ch3_1 : 4, adc0ch3_2 : 8, adc1ch3_2 : 8;

  uint16_t get_channel(const uint8_t adc, const uint8_t ch) const // NOLINT(build/unsigned)
  {
    if (adc % 2 == 0) {
      switch (ch % 4) {
        case 0:
          return adc0ch0_1 | adc0ch0_2 << 8;
        case 1:
          return adc0ch1_1 | adc0ch1_2 << 4;
        case 2:
          return adc0ch2_1 | adc0ch2_2 << 8;
        case 3:
          return adc0ch3_1 | adc0ch3_2 << 4;
      }
    } else if (adc % 2 == 1) {
      switch (ch % 4) {
        case 0:
          return adc1ch0_1 | adc1ch0_2 << 8;
        case 1:
          return adc1ch1_1 | adc1ch1_2 << 4;
        case 2:
          return adc1ch2_1 | adc1ch2_2 << 8;
        case 3:
          return adc1ch3_1 | adc1ch3_2 << 4;
      }
    }
    throw std::range_error("Supplied WIB channel index is out of the allowed range.");
    return 0;
  }

  void set_channel(const uint8_t adc, const uint8_t ch, const uint16_t new_val) // NOLINT(build/unsigned)
  {
    if (adc % 2 == 0) {
      switch (ch % 4) {
        case 0:
          adc0ch0_1 = new_val;
          adc0ch0_2 = new_val >> 8;
          break;
        case 1:
          adc0ch1_1 = new_val;
          adc0ch1_2 = new_val >> 4;
          break;
        case 2:
          adc0ch2_1 = new_val;
          adc0ch2_2 = new_val >> 8;
          break;
        case 3:
          adc0ch3_1 = new_val;
          adc0ch3_2 = new_val >> 4;
          break;
      }
    } else if (adc % 2 == 1) {
      switch (ch % 4) {
        case 0:
          adc1ch0_1 = new_val;
          adc1ch0_2 = new_val >> 8;
          break;
        case 1:
          adc1ch1_1 = new_val;
          adc1ch1_2 = new_val >> 4;
          break;
        case 2:
          adc1ch2_1 = new_val;
          adc1ch2_2 = new_val >> 8;
          break;
        case 3:
          adc1ch3_1 = new_val;
          adc1ch3_2 = new_val >> 4;
          break;
      }
    }
  }
};

/**
 * @brief COLDATA block struct
 */
struct ColdataBlock
{
  static constexpr int s_num_seg_per_block = 8;
  static constexpr int s_num_ch_per_adc = 8;
  static constexpr int s_num_adc_per_block = ColdataSegment::s_num_ch_per_seg * s_num_seg_per_block / s_num_ch_per_adc;
  static constexpr int s_num_ch_per_block = s_num_seg_per_block * ColdataSegment::s_num_ch_per_seg;

  ColdataHeader head;
  ColdataSegment segments[s_num_seg_per_block]; // NOLINT

  uint16_t get_channel(const uint8_t adc, const uint8_t ch) const // NOLINT(build/unsigned)
  {
    // Each segment houses one half (four channels) of two subsequent ADCs.
    return segments[get_segment_index_(adc, ch)].get_channel(adc, ch);
  }

  void set_channel(const uint8_t adc, const uint8_t ch, const uint16_t new_val) // NOLINT(build/unsigned)
  {
    segments[get_segment_index_(adc, ch)].set_channel(adc, ch, new_val);
  }

private:
  int get_segment_index_(const int adc, const int ch) const
  {
    auto segment_id = (adc / 2) * 2 + ch / 4;

    if (segment_id < 0 || segment_id > s_num_seg_per_block - 1) {
        throw std::out_of_range("ADC index out of range");      
    }
    return segment_id;
  }
};

inline std::ostream&
operator<<(std::ostream& o, const ColdataBlock& block)
{
  o << block.head;

  // Note that this is an ADC-centric view, whereas ColdataBlock uses a channel-centric view
  o << "\t\t0\t1\t2\t3\t4\t5\t6\t7\n";
  for (int adc = 0; adc < 8; adc++) {
    o << "Stream " << adc << ":\t";
    for (int ch = 0; ch < 8; ch++) {
      o << std::hex << block.get_channel(adc, ch) << '\t';
    }
    o << std::dec << '\n';
  }
  return o;
}

/**
 * @brief FELIX frame
 */
class WIBFrame
{
public:
  static constexpr int s_num_block_per_frame = 4;
  static constexpr int s_num_ch_per_frame = s_num_block_per_frame * ColdataBlock::s_num_ch_per_block;

  static constexpr int s_num_frame_hdr_words = sizeof(WIBHeader) / sizeof(word_t);
  static constexpr int s_num_COLDATA_hdr_words = sizeof(ColdataHeader) / sizeof(word_t);
  static constexpr int s_num_COLDATA_words = sizeof(ColdataBlock) / sizeof(word_t);
  static constexpr int s_num_frame_words = s_num_block_per_frame * s_num_COLDATA_words + s_num_frame_hdr_words;
  static constexpr int s_num_frame_bytes = s_num_frame_words * sizeof(word_t);

  const WIBHeader* get_wib_header() const { return &m_head; }
  WIBHeader* get_wib_header() { return &m_head; }

  const ColdataHeader* get_coldata_header(const unsigned block_index) const
  {
    throw_if_invalid_block_index_(block_index);
    return &m_blocks[block_index].head;
  }
  const ColdataBlock& get_block(const uint8_t b) const // NOLINT(build/unsigned)
  {
    throw_if_invalid_block_index_(b);
    return m_blocks[b];
  }

  // WIBHeader mutators
  void set_wib_errors(const uint16_t new_wib_errors) { m_head.wib_errors = new_wib_errors; } // NOLINT(build/unsigned)
  void set_timestamp(const uint64_t new_timestamp) { m_head.set_timestamp(new_timestamp); }  // NOLINT(build/unsigned)

  uint64_t get_timestamp() const { return m_head.get_timestamp(); } // NOLINT(build/unsigned)

  // ColdataBlock channel accessors
  uint16_t get_channel(const uint8_t block_num, const uint8_t adc, const uint8_t ch) const // NOLINT(build/unsigned)
  {
    throw_if_invalid_block_index_(block_num);
    return m_blocks[block_num].get_channel(adc, ch);
  }
  uint16_t get_channel(const uint8_t block_num, const uint8_t ch) const // NOLINT(build/unsigned)
  {
    throw_if_invalid_block_index_(block_num);
    return get_channel(block_num, ch / ColdataBlock::s_num_adc_per_block, ch % ColdataBlock::s_num_adc_per_block);
  }
  uint16_t get_channel(const uint8_t ch) const // NOLINT(build/unsigned)
  {
    return get_channel(ch / ColdataBlock::s_num_ch_per_block, ch % ColdataBlock::s_num_ch_per_block);
  }

  // ColdataBlock channel mutators
  void set_channel(const uint8_t block_num, // NOLINT(build/unsigned)
                   const uint8_t adc,       // NOLINT(build/unsigned)
                   const uint8_t ch,        // NOLINT(build/unsigned)
                   const uint16_t new_val)  // NOLINT(build/unsigned)
  {
    throw_if_invalid_block_index_(block_num);
    m_blocks[block_num].set_channel(adc, ch, new_val);
  }
  void set_channel(const uint8_t block_num, const uint8_t ch, const uint16_t new_val) // NOLINT(build/unsigned)
  {
    throw_if_invalid_block_index_(block_num);
    set_channel(block_num, ch / ColdataBlock::s_num_adc_per_block, ch % ColdataBlock::s_num_adc_per_block, new_val);
  }
  void set_channel(const uint8_t ch, const uint16_t new_val) // NOLINT(build/unsigned)
  {
    set_channel(ch / ColdataBlock::s_num_ch_per_block, ch % ColdataBlock::s_num_ch_per_block, new_val);
  }

  friend std::ostream& operator<<(std::ostream& o, WIBFrame const& frame);

private:
  void throw_if_invalid_block_index_(const int block_num) const
  {
    if (block_num < 0 || block_num > s_num_block_per_frame - 1) {
       throw std::out_of_range("FEMB index out of range");
    }
  }

  WIBHeader m_head;
  ColdataBlock m_blocks[s_num_block_per_frame]; // NOLINT
};

inline std::ostream&
operator<<(std::ostream& o, WIBFrame const& frame)
{
  o << "Printing frame:" << '\n';
  o << frame.m_head << '\n';
  for (auto b : frame.m_blocks) {
    o << b;
  }
  return o;
}

} // namespace dunedaq::fddetdataformats 

#endif // FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_WIBFRAME_HPP_

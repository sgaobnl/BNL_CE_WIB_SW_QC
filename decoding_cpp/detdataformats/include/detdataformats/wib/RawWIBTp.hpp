/**
 * @file RawWIBTp.hpp Raw Trigger Primitive bit fields and accessors
 *
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */
#ifndef DETDATAFORMATS_INCLUDE_DETDATAFORMATS_WIB_RAWWIBTP_HPP_
#define DETDATAFORMATS_INCLUDE_DETDATAFORMATS_WIB_RAWWIBTP_HPP_

#include <bitset>
#include <iostream>
#include <vector>

namespace dunedaq {
namespace detdataformats {
namespace wib {

using tp_word_t = uint32_t; // NOLINT(build/unsigned)

//===================
// TP header struct
//===================
struct TpHeader
{
  TpHeader()
  {
    m_nhits = 1;
  }

  tp_word_t m_flags : 13, m_slot_no : 3, m_wire_no : 8, m_fiber_no : 3, m_crate_no : 5;
  tp_word_t m_timestamp_1;
  tp_word_t m_timestamp_2;
  tp_word_t m_accumulator : 16, m_median : 16;
  tp_word_t m_padding_1 : 16, m_nhits : 16;
  tp_word_t m_padding_3 : 16, m_padding_2 : 16; 

  uint64_t get_timestamp() const // NOLINT(build/unsigned)
  {
    uint64_t timestamp = (m_timestamp_1 & 0xFFFF0000) >> 16;
    timestamp += static_cast<int64_t>(m_timestamp_1 & 0xFFFF) << 16;
    timestamp += static_cast<int64_t>(m_timestamp_2 & 0xFFFF0000) << 16;
    timestamp += static_cast<int64_t>(m_timestamp_2 & 0xFFFF) << 48;
    return timestamp;
  }

  void set_timestamp(const uint64_t new_timestamp) // NOLINT(build/unsigned)
  {
    m_timestamp_1  = (new_timestamp & 0xFFFF) << 16;
    m_timestamp_1 += (new_timestamp & 0xFFFF0000) >> 16;
    m_timestamp_2  = (new_timestamp & 0xFFFF00000000) >> 16;
    m_timestamp_2 += (new_timestamp >> 48) & 0xFFFF;
  }

  int get_nhits()
  {
    return static_cast<int>(m_nhits);
  }
  void set_nhits(int nhits) 
  {
    m_nhits = nhits;
  }
 
  uint16_t get_padding_3() // NOLINT(build/unsigned)
  {
    return m_padding_3;
  } 
 
  // Print functions for debugging.
  std::ostream& print(std::ostream& o) const
  {
    o << "Printing raw WIB TP header:\n";
    o << "flags:" << unsigned(m_flags) << " slot:" << unsigned(m_slot_no) << " wire:" << unsigned(m_wire_no)
      << " fiber:" << unsigned(m_fiber_no) << " crate:" << unsigned(m_crate_no) << " timestamp:" << get_timestamp();
    o << "\nPrinting raw WIB TP pedinfo:\n";
    o << "median:" << unsigned(m_median) << " accumulator:" << unsigned(m_accumulator)
      << " nhits:" << unsigned(m_nhits) << " padding_1:" << unsigned(m_padding_1)
      << " padding_2:" << unsigned(m_padding_2) << " padding_3:" << unsigned(m_padding_3);
 
    return o << '\n';
  }

  std::ostream& print_hex(std::ostream& o) const
  {
    o << "Printing raw WIB TP header:\n";
    o << std::hex << "flags:" << m_flags << " slot:" << m_slot_no << " wire:" << m_wire_no << " fiber:" << m_fiber_no
      << " crate:" << m_crate_no << " timestamp:" << get_timestamp();
    o << "\nPrinting raw WIB TP pedinfo:\n";
    o << std::hex << "median:" << m_median << " accumulator:" << m_accumulator << " nhits:" << m_nhits
      << " padding_1:" << m_padding_1 << " padding_2:" << m_padding_2 << " padding_3:" << m_padding_3;
    return o << std::dec << '\n';
  }

  std::ostream& print_bits(std::ostream& o) const
  {
    o << "Printing raw WIB TP header:\n";
    o << "flags:" << std::bitset<13>(m_flags) << " slot:" << std::bitset<3>(m_slot_no)
      << " wire:" << std::bitset<8>(m_wire_no) << " fiber:" << std::bitset<3>(m_fiber_no)
      << " crate:" << std::bitset<5>(m_crate_no) << " timestamp:" << get_timestamp();
    o << "\nPrinting raw WIB TP pedinfo:\n";
    o << "median:" << std::bitset<16>(m_accumulator) << " accumulator:" << std::bitset<16>(m_median)
      << " nhits:" << std::bitset<16>(m_nhits) << " padding_1:" << std::bitset<16>(m_padding_1)
      << " padding_2:" << std::bitset<16>(m_padding_2) << " padding_3:" << std::bitset<16>(m_padding_3);
    return o << '\n';
  }
};

inline std::ostream&
operator<<(std::ostream& o, TpHeader const& h)
{
  o << "Printing raw WIB TP header:\n";
  o << "flags:" << unsigned(h.m_flags) << " slot:" << unsigned(h.m_slot_no) << " wire:" << unsigned(h.m_wire_no)
    << " fiber:" << unsigned(h.m_fiber_no) << " crate:" << unsigned(h.m_crate_no) << " timestamp:" << h.get_timestamp();
  o << "\nPrinting raw WIB TP pedinfo:\n";
  o << "median:" << unsigned(h.m_median) << " accumulator:" << unsigned(h.m_accumulator)
    << " nhits:" << unsigned(h.m_nhits) << " padding_1:" << unsigned(h.m_padding_1)
    << " padding_2:" << unsigned(h.m_padding_2) << " padding_3:" << unsigned(h.m_padding_3);
  return o << '\n';
}

//========================
// TP data struct
//========================
struct TpData
{
  // This struct contains three words of TP values that form the main repeating
  // pattern in the TP block.
  tp_word_t m_end_time : 16, m_start_time : 16;
  tp_word_t m_peak_time : 16, m_peak_adc : 16;
  tp_word_t m_hit_continue : 1, m_tp_flags : 15, m_sum_adc : 16;

  std::ostream& print(std::ostream& o) const
  {
    o << "Printing raw WIB TP:\n";
    o << "start_time:" << unsigned(m_start_time) << " end_time:" << unsigned(m_end_time)
      << " peak_adc:" << unsigned(m_peak_adc) << " peak_time:" << unsigned(m_peak_time)
      << " sum_adc:" << unsigned(m_sum_adc) << " flags:" << unsigned(m_tp_flags)
      << " hit_continue:" << unsigned(m_hit_continue);
    return o << '\n';
  }

  std::ostream& print_hex(std::ostream& o) const
  {
    o << "Printing raw WIB TP:\n";
    o << std::hex << "start_time:" << m_start_time << " end_time:" << m_end_time << " peak_adc:" << m_peak_adc
      << " peak_time:" << m_peak_time << " sum_adc:" << m_sum_adc << " flags:" << m_tp_flags
      << " hit_continue:" << m_hit_continue;
    return o << std::dec << '\n';
  }

  std::ostream& print_bits(std::ostream& o) const
  {
    o << "Printing raw WIB TP:\n";
    o << "start_time:" << std::bitset<16>(m_start_time) << " end_time:" << std::bitset<16>(m_end_time)
      << " peak_adc:" << std::bitset<16>(m_peak_adc) << " peak_time:" << std::bitset<16>(m_peak_time)
      << " sum_adc:" << std::bitset<16>(m_sum_adc) << " flags:" << std::bitset<15>(m_tp_flags)
      << " hit_continue:" << std::bitset<1>(m_hit_continue);
    return o << '\n';
  }
};

inline std::ostream&
operator<<(std::ostream& o, TpData const& tp)
{
  o << "Printing raw WIB TP:\n";
  o << "start_time:" << unsigned(tp.m_start_time) << " end_time:" << unsigned(tp.m_end_time)
    << " peak_adc:" << unsigned(tp.m_peak_adc) << " peak_time:" << unsigned(tp.m_peak_time)
    << " sum_adc:" << unsigned(tp.m_sum_adc) << " flags:" << unsigned(tp.m_tp_flags)
    << " hit_continue:" << unsigned(tp.m_hit_continue);
  return o << '\n';
}


//========================
// RawWIBTp data struct
//========================
struct RawWIBTp
{
  RawWIBTp()
  {
    m_nhits = 1;
  }

  // mutators
  void set_nhits(int nhits) { 
    m_nhits = nhits;
    m_head.set_nhits(nhits);
  }

  // accessors
  const TpHeader* get_tp_header() const { return &m_head; }
  TpHeader* get_tp_header() { return &m_head; }

  size_t get_header_size()
  {
    return sizeof(TpHeader);
  }
  size_t get_frame_size()
  {
    return sizeof(TpHeader) + get_nhits() * sizeof(TpData);
  }

  uint64_t get_timestamp() const 
  {
    return m_head.get_timestamp();
  }
  uint64_t get_timestamp() 
  {
    return m_head.get_timestamp();
  }
  void set_timestamp(const uint64_t ts) 
  {
    m_head.set_timestamp(ts);
  }
 
  int get_nhits()
  {
    return m_head.get_nhits();
  }
  uint16_t get_padding_3()
  {
    return m_head.get_padding_3(); 
  }

private:
  int m_nhits;

public:
  TpHeader m_head;
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
  TpData m_blocks[];
#pragma GCC diagnostic pop
};

inline std::ostream&
operator<<(std::ostream& o, RawWIBTp const& rwtp)
{
  o << "Printing raw WIB TP frame:" << '\n';
  o << rwtp.m_head << '\n';
  return o;
}

} // namespace wib
} // namespace detdataformats
} // namespace dunedaq

#endif // DETDATAFORMATS_INCLUDE_DETDATAFORMATS_WIB_RAWWIBTP_HPP_

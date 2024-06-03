
/**
 * @file WIBFrame_test.cxx WIBFrame class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIBFrame.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE WIBFrame_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::fddetdataformats;

BOOST_AUTO_TEST_SUITE(WIBFrame_test)

BOOST_AUTO_TEST_CASE(WIBHeader_TimestampMethods)
{
  WIBHeader header;
  header.z = 0;
  header.wib_counter_1 = 0x7FFF;
  header.timestamp_1 = 0x11111111;
  header.timestamp_2 = 0x2222;

  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x7FFF222211111111);
  BOOST_REQUIRE_EQUAL(header.get_wib_counter(), 0);

  header.set_wib_counter(0x3333);
  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x7FFF222211111111);
  BOOST_REQUIRE_EQUAL(header.get_wib_counter(), 0);

  header.set_timestamp(0xF333444455555555); // Try to toggle z bit
  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x7333444455555555);
  BOOST_REQUIRE_EQUAL(header.wib_counter_1, 0x7333);
  BOOST_REQUIRE_EQUAL(header.timestamp_1, 0x55555555);
  BOOST_REQUIRE_EQUAL(header.timestamp_2, 0x4444);
  BOOST_REQUIRE_EQUAL(header.z, 0);

  header.z = 1;
  header.wib_counter_1 = 0x7FFF;
  header.timestamp_1 = 0x11111111;
  header.timestamp_2 = 0x2222;

  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x222211111111);
  BOOST_REQUIRE_EQUAL(header.get_wib_counter(), 0x7FFF);

  header.set_wib_counter(0x7333); // Try to toggle z bit
  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x222211111111);
  BOOST_REQUIRE_EQUAL(header.get_wib_counter(), 0x7333);
  BOOST_REQUIRE_EQUAL(header.z, 1);

  header.set_timestamp(0xFFFF444455555555); // Try to change wib_counter_1
  BOOST_REQUIRE_EQUAL(header.get_timestamp(), 0x444455555555);
  BOOST_REQUIRE_EQUAL(header.wib_counter_1, 0x7333);
  BOOST_REQUIRE_EQUAL(header.timestamp_1, 0x55555555);
  BOOST_REQUIRE_EQUAL(header.timestamp_2, 0x4444);
}
BOOST_AUTO_TEST_CASE(WIBHeader_StreamMethods)
{
  WIBHeader header {};

  std::ostringstream ostr;
  header.print_hex(ostr);
  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Print hex: " << output);
  BOOST_REQUIRE(!output.empty());

  ostr.str("");
  ostr.clear();

  header.print_bits(ostr);
  output = ostr.str();
  BOOST_TEST_MESSAGE("Print bits: " << output);
  BOOST_REQUIRE(!output.empty());

  ostr.str("");
  ostr.clear();

  ostr << header;
  output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);
  BOOST_REQUIRE(!output.empty());
}

BOOST_AUTO_TEST_CASE(ColdataHeader_ChecksumMethods)
{
  ColdataHeader header;
  header.checksum_a_1 = 0x11;
  header.checksum_a_2 = 0x22;
  header.checksum_b_1 = 0x33;
  header.checksum_b_2 = 0x44;

  BOOST_REQUIRE_EQUAL(header.get_checksum_a(), 0x2211);
  BOOST_REQUIRE_EQUAL(header.get_checksum_b(), 0x4433);

  header.set_checksum_a(0x5566);
  header.set_checksum_b(0x7788);
  BOOST_REQUIRE_EQUAL(header.get_checksum_a(), 0x5566);
  BOOST_REQUIRE_EQUAL(header.get_checksum_b(), 0x7788);
  BOOST_REQUIRE_EQUAL(header.checksum_a_1, 0x66);
  BOOST_REQUIRE_EQUAL(header.checksum_a_2, 0x55);
  BOOST_REQUIRE_EQUAL(header.checksum_b_1, 0x88);
  BOOST_REQUIRE_EQUAL(header.checksum_b_2, 0x77);
}
BOOST_AUTO_TEST_CASE(ColdataHeader_HdrMethods)
{
  ColdataHeader header;
  header.hdr_1 = 0x1;
  header.hdr_2 = 0x2;
  header.hdr_3 = 0x3;
  header.hdr_4 = 0x4;
  header.hdr_5 = 0x5;
  header.hdr_6 = 0x6;
  header.hdr_7 = 0x7;
  header.hdr_8 = 0x8;

  BOOST_REQUIRE_EQUAL(header.get_hdr(1), 0x1);
  BOOST_REQUIRE_EQUAL(header.get_hdr(2), 0x2);
  BOOST_REQUIRE_EQUAL(header.get_hdr(3), 0x3);
  BOOST_REQUIRE_EQUAL(header.get_hdr(4), 0x4);
  BOOST_REQUIRE_EQUAL(header.get_hdr(5), 0x5);
  BOOST_REQUIRE_EQUAL(header.get_hdr(6), 0x6);
  BOOST_REQUIRE_EQUAL(header.get_hdr(7), 0x7);
  BOOST_REQUIRE_EQUAL(header.get_hdr(8), 0x8);
  BOOST_REQUIRE_EQUAL(header.get_hdr(9), 0x0);
  BOOST_REQUIRE_EQUAL(header.get_hdr(0), 0x0);

  header.set_hdr(1, 0x9);
  BOOST_REQUIRE_EQUAL(header.hdr_1, 0x9);
  BOOST_REQUIRE_EQUAL(header.get_hdr(1), 0x9);
  header.set_hdr(2, 0xA);
  BOOST_REQUIRE_EQUAL(header.hdr_2, 0xA);
  BOOST_REQUIRE_EQUAL(header.get_hdr(2), 0xA);
  header.set_hdr(3, 0xB);
  BOOST_REQUIRE_EQUAL(header.hdr_3, 0xB);
  BOOST_REQUIRE_EQUAL(header.get_hdr(3), 0xB);

  header.set_hdr(4, 0xFF);
  BOOST_REQUIRE_EQUAL(header.hdr_4, 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(4), 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(3), 0xB);
  BOOST_REQUIRE_EQUAL(header.get_hdr(5), 0x5);

  header.set_hdr(5, 0xC);
  BOOST_REQUIRE_EQUAL(header.hdr_5, 0xC);
  BOOST_REQUIRE_EQUAL(header.get_hdr(5), 0xC);
  header.set_hdr(6, 0xD);
  BOOST_REQUIRE_EQUAL(header.hdr_6, 0xD);
  BOOST_REQUIRE_EQUAL(header.get_hdr(6), 0xD);
  header.set_hdr(7, 0xE);
  BOOST_REQUIRE_EQUAL(header.hdr_7, 0xE);
  BOOST_REQUIRE_EQUAL(header.get_hdr(7), 0xE);
  header.set_hdr(8, 0xF);
  BOOST_REQUIRE_EQUAL(header.hdr_8, 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(8), 0xF);

  header.set_hdr(0, 0xB);
  BOOST_REQUIRE_EQUAL(header.get_hdr(1), 0x9);
  BOOST_REQUIRE_EQUAL(header.get_hdr(2), 0xA);
  BOOST_REQUIRE_EQUAL(header.get_hdr(3), 0xB);
  BOOST_REQUIRE_EQUAL(header.get_hdr(4), 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(5), 0xC);
  BOOST_REQUIRE_EQUAL(header.get_hdr(6), 0xD);
  BOOST_REQUIRE_EQUAL(header.get_hdr(7), 0xE);
  BOOST_REQUIRE_EQUAL(header.get_hdr(8), 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(9), 0x0);
  BOOST_REQUIRE_EQUAL(header.get_hdr(0), 0x0);

  header.set_hdr(9, 0xC);
  BOOST_REQUIRE_EQUAL(header.get_hdr(1), 0x9);
  BOOST_REQUIRE_EQUAL(header.get_hdr(2), 0xA);
  BOOST_REQUIRE_EQUAL(header.get_hdr(3), 0xB);
  BOOST_REQUIRE_EQUAL(header.get_hdr(4), 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(5), 0xC);
  BOOST_REQUIRE_EQUAL(header.get_hdr(6), 0xD);
  BOOST_REQUIRE_EQUAL(header.get_hdr(7), 0xE);
  BOOST_REQUIRE_EQUAL(header.get_hdr(8), 0xF);
  BOOST_REQUIRE_EQUAL(header.get_hdr(9), 0x0);
  BOOST_REQUIRE_EQUAL(header.get_hdr(0), 0x0);
}
BOOST_AUTO_TEST_CASE(ColdataHeader_StreamMethods)
{
  ColdataHeader header {};

  std::ostringstream ostr;
  header.print_hex(ostr);
  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Print hex: " << output);
  BOOST_REQUIRE(!output.empty());

  ostr.str("");
  ostr.clear();

  header.print_bits(ostr);
  output = ostr.str();
  BOOST_TEST_MESSAGE("Print bits: " << output);
  BOOST_REQUIRE(!output.empty());

  ostr.str("");
  ostr.clear();

  ostr << header;
  output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);
  BOOST_REQUIRE(!output.empty());
}

BOOST_AUTO_TEST_CASE(ColdataSegment_ChannelMethods)
{
  ColdataSegment segment {};
  segment.adc0ch0_1 = 0x11;
  segment.adc1ch0_1 = 0x22;
  segment.adc0ch0_2 = 0x3;
  segment.adc0ch1_1 = 0x4;
  segment.adc1ch0_2 = 0x5;
  segment.adc1ch1_1 = 0x6;
  segment.adc0ch1_2 = 0x77;
  segment.adc1ch1_2 = 0x88;
  segment.adc0ch2_1 = 0x99;
  segment.adc1ch2_1 = 0xAA;
  segment.adc0ch2_2 = 0xB;
  segment.adc0ch3_1 = 0xC;
  segment.adc1ch2_2 = 0xD;
  segment.adc1ch3_1 = 0xE;
  segment.adc0ch3_2 = 0xFF;
  segment.adc1ch3_2 = 0x10;

  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 0), 0x311);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 1), 0x774);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 2), 0xB99);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 3), 0xFFC);

  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 0), 0x522);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 1), 0x886);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 2), 0xDAA);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 3), 0x10E);

  BOOST_REQUIRE_EQUAL(segment.get_channel(2, 0), 0x311);
  BOOST_REQUIRE_EQUAL(segment.get_channel(2, 1), 0x774);
  BOOST_REQUIRE_EQUAL(segment.get_channel(2, 2), 0xB99);
  BOOST_REQUIRE_EQUAL(segment.get_channel(2, 3), 0xFFC);

  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 4), 0x311);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 5), 0x774);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 6), 0xB99);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 7), 0xFFC);

  segment.set_channel(0, 0, 0x1133);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 0), 0x133);
  BOOST_REQUIRE_EQUAL(segment.adc0ch0_1, 0x33);
  BOOST_REQUIRE_EQUAL(segment.adc0ch0_2, 0x1);
  segment.set_channel(0, 1, 0x447);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 1), 0x447);
  BOOST_REQUIRE_EQUAL(segment.adc0ch1_1, 0x7);
  BOOST_REQUIRE_EQUAL(segment.adc0ch1_2, 0x44);
  segment.set_channel(0, 2, 0x9BB);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 2), 0x9BB);
  BOOST_REQUIRE_EQUAL(segment.adc0ch2_1, 0xBB);
  BOOST_REQUIRE_EQUAL(segment.adc0ch2_2, 0x9);
  segment.set_channel(0, 3, 0xCCF);
  BOOST_REQUIRE_EQUAL(segment.get_channel(0, 3), 0xCCF);
  BOOST_REQUIRE_EQUAL(segment.adc0ch3_1, 0xF);
  BOOST_REQUIRE_EQUAL(segment.adc0ch3_2, 0xCC);

  segment.set_channel(1, 0, 0x255);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 0), 0x255);
  BOOST_REQUIRE_EQUAL(segment.adc1ch0_1, 0x55);
  BOOST_REQUIRE_EQUAL(segment.adc1ch0_2, 0x2);
  segment.set_channel(1, 1, 0x668);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 1), 0x668);
  BOOST_REQUIRE_EQUAL(segment.adc1ch1_1, 0x8);
  BOOST_REQUIRE_EQUAL(segment.adc1ch1_2, 0x66);
  segment.set_channel(1, 2, 0xADD);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 2), 0xADD);
  BOOST_REQUIRE_EQUAL(segment.adc1ch2_1, 0xDD);
  BOOST_REQUIRE_EQUAL(segment.adc1ch2_2, 0xA);
  segment.set_channel(1, 3, 0xEE1);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 3), 0xEE1);
  BOOST_REQUIRE_EQUAL(segment.adc1ch3_1, 0x1);
  BOOST_REQUIRE_EQUAL(segment.adc1ch3_2, 0xEE);

  segment.set_channel(3, 5, 0x6688);
  BOOST_REQUIRE_EQUAL(segment.get_channel(1, 1), 0x688);
  BOOST_REQUIRE_EQUAL(segment.adc1ch1_1, 0x8);
  BOOST_REQUIRE_EQUAL(segment.adc1ch1_2, 0x68);
}

BOOST_AUTO_TEST_CASE(ColdataBlock_ChannelMethods)
{
  ColdataBlock block;
  ColdataSegment segment;
  segment.adc0ch0_1 = 0x11;
  segment.adc1ch0_1 = 0x22;
  segment.adc0ch0_2 = 0x3;
  segment.adc0ch1_1 = 0x4;
  segment.adc1ch0_2 = 0x5;
  segment.adc1ch1_1 = 0x6;
  segment.adc0ch1_2 = 0x77;
  segment.adc1ch1_2 = 0x88;
  segment.adc0ch2_1 = 0x99;
  segment.adc1ch2_1 = 0xAA;
  segment.adc0ch2_2 = 0xB;
  segment.adc0ch3_1 = 0xC;
  segment.adc1ch2_2 = 0xD;
  segment.adc1ch3_1 = 0xE;
  segment.adc0ch3_2 = 0xFF;
  segment.adc1ch3_2 = 0x10;

  ColdataSegment rev_seg;
  rev_seg.adc0ch0_1 = 0xAA;
  rev_seg.adc1ch0_1 = 0x99;
  rev_seg.adc0ch0_2 = 0xD;
  rev_seg.adc1ch2_1 = 0x11;
  rev_seg.adc1ch2_2 = 0x3;
  rev_seg.adc1ch3_1 = 0x4;
  rev_seg.adc1ch3_2 = 0x77;
  rev_seg.adc1ch0_2 = 0xB;
  rev_seg.adc1ch1_1 = 0xC;
  rev_seg.adc1ch1_2 = 0xFF;
  rev_seg.adc0ch2_1 = 0x22;
  rev_seg.adc0ch2_2 = 0x5;
  rev_seg.adc0ch3_1 = 0x6;
  rev_seg.adc0ch3_2 = 0x88;
  rev_seg.adc0ch1_1 = 0xE;
  rev_seg.adc0ch1_2 = 0x10;

  block.segments[0] = segment;
  block.segments[1] = rev_seg;

  BOOST_REQUIRE_EQUAL(block.get_channel(0, 0), segment.get_channel(0, 0));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 1), segment.get_channel(0, 1));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 2), segment.get_channel(0, 2));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 3), segment.get_channel(0, 3));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 4), rev_seg.get_channel(0, 0));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 5), rev_seg.get_channel(0, 1));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 6), rev_seg.get_channel(0, 2));
  BOOST_REQUIRE_EQUAL(block.get_channel(0, 7), rev_seg.get_channel(0, 3));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 0), segment.get_channel(1, 0));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 1), segment.get_channel(1, 1));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 2), segment.get_channel(1, 2));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 3), segment.get_channel(1, 3));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 4), rev_seg.get_channel(1, 0));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 5), rev_seg.get_channel(1, 1));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 6), rev_seg.get_channel(1, 2));
  BOOST_REQUIRE_EQUAL(block.get_channel(1, 7), rev_seg.get_channel(1, 3));

  block.set_channel(0, 0, 0xFFFF);
  BOOST_REQUIRE_EQUAL(block.segments[0].adc0ch0_1, 0xFF);
  BOOST_REQUIRE_EQUAL(block.segments[0].adc0ch0_2, 0xF);
  BOOST_REQUIRE_EQUAL(block.segments[0].adc1ch0_1, 0x22);
  BOOST_REQUIRE_EQUAL(block.segments[0].adc0ch1_1, 0x4);

  uint8_t invalid_adc = ColdataBlock::s_num_adc_per_block; // NOLINT(build/unsigned)
  BOOST_REQUIRE_EXCEPTION(block.get_channel(invalid_adc, 0),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });
  BOOST_REQUIRE_EXCEPTION(block.set_channel(invalid_adc, 0, 0x123),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });
}
BOOST_AUTO_TEST_CASE(ColdataBlock_StreamOperator)
{
  ColdataBlock block {};

  std::ostringstream ostr;
  ostr << block;
  auto output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);
  BOOST_REQUIRE(!output.empty());
}

BOOST_AUTO_TEST_CASE(WIBFrame_StructMethods)
{
  WIBFrame frame {};

  BOOST_REQUIRE(frame.get_wib_header() != nullptr);
  BOOST_REQUIRE(frame.get_coldata_header(0) != nullptr);
  BOOST_REQUIRE_EXCEPTION(frame.get_coldata_header(WIBFrame::s_num_block_per_frame),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });

  BOOST_REQUIRE_NO_THROW(frame.get_block(0));
  ;
}
BOOST_AUTO_TEST_CASE(WIBFrame_HeaderMutators)
{

  {
    WIBFrame frame;
    frame.set_wib_errors(0xFC5F);
    BOOST_REQUIRE_EQUAL(frame.get_wib_header()->wib_errors, 0xFC5F);
  }

  {
    WIBFrame frame;
    frame.get_wib_header()->z = 1;
    frame.set_timestamp(0x7333444455555555);
    BOOST_REQUIRE_EQUAL(frame.get_wib_header()->get_timestamp(), 0x444455555555);
  }

  {
    WIBFrame frame;
    frame.get_wib_header()->z = 0;
    frame.set_timestamp(0xF333444455555555);
    BOOST_REQUIRE_EQUAL(frame.get_wib_header()->get_timestamp(), 0x7333444455555555);
  }
}
BOOST_AUTO_TEST_CASE(WIBFrame_BlockChannelMethods)
{
  WIBFrame frame;
  frame.set_channel(0, 0x111);
  frame.set_channel(1, 0x222);
  frame.set_channel(64, 0x333);
  frame.set_channel(65, 0x444);
  frame.set_channel(2, 0, 0x555);
  frame.set_channel(2, 63, 0x666);
  frame.set_channel(3, 0, 0, 0x777);
  frame.set_channel(3, 1, 3, 0x888);

  BOOST_REQUIRE_EXCEPTION(frame.set_channel(WIBFrame::s_num_block_per_frame, 0, 0x123),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });
  BOOST_REQUIRE_EXCEPTION(frame.set_channel(WIBFrame::s_num_block_per_frame, 0, 0, 0x123),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });

  BOOST_REQUIRE_EQUAL(frame.get_channel(0), 0x111);
  BOOST_REQUIRE_EQUAL(frame.get_channel(1, 0), 0x333);
  BOOST_REQUIRE_EQUAL(frame.get_channel(3, 0, 0), 0x777);
  BOOST_REQUIRE_EXCEPTION(frame.get_channel(WIBFrame::s_num_block_per_frame, 0),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });
  BOOST_REQUIRE_EXCEPTION(frame.get_channel(WIBFrame::s_num_block_per_frame, 0, 0),
                          std::out_of_range,
                          [&](std::out_of_range) { return true; });

  auto block_0 = frame.get_block(0);
  BOOST_REQUIRE_EQUAL(block_0.get_channel(0, 0), 0x111);
  BOOST_REQUIRE_EQUAL(block_0.get_channel(0, 1), 0x222);

  auto block_1 = frame.get_block(1);
  BOOST_REQUIRE_EQUAL(block_1.get_channel(0, 0), 0x333);
  BOOST_REQUIRE_EQUAL(block_1.get_channel(0, 1), 0x444);

  auto block_2 = frame.get_block(2);
  BOOST_REQUIRE_EQUAL(block_2.get_channel(0, 0), 0x555);
  BOOST_REQUIRE_EQUAL(block_2.get_channel(7, 7), 0x666);

  auto block_3 = frame.get_block(3);
  BOOST_REQUIRE_EQUAL(block_3.get_channel(0, 0), 0x777);
  BOOST_REQUIRE_EQUAL(block_3.get_channel(1, 3), 0x888);
}
BOOST_AUTO_TEST_CASE(WIBFrame_StreamOperator)
{
  WIBFrame frame {};

  std::ostringstream ostr;
  ostr << frame;
  auto output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);
  BOOST_REQUIRE(!output.empty());
}

BOOST_AUTO_TEST_CASE(WIBFrame_FromRawData)
{
  WIBHeader header;
  header.timestamp_1 = 0x12345678;
  header.timestamp_2 = 0x9ABC;
  header.wib_counter_1 = 0xDEF;
  header.z = 1;
  ColdataBlock blocks[WIBFrame::s_num_block_per_frame];
  blocks[0].head.checksum_a_1 = 0x11;
  blocks[0].head.checksum_b_1 = 0x22;
  blocks[0].head.checksum_a_2 = 0x33;
  blocks[0].head.checksum_b_2 = 0x44;

  uint8_t* buff = static_cast<uint8_t*>(malloc(sizeof(header) + sizeof(blocks))); // NOLINT(build/unsigned)
  memcpy(buff, &header, sizeof(header));
  memcpy(buff + sizeof(header), blocks, sizeof(ColdataBlock) * WIBFrame::s_num_block_per_frame);

  WIBFrame* from_raw_data = reinterpret_cast<WIBFrame*>(buff); // NOLINT

  BOOST_REQUIRE_EQUAL(from_raw_data->get_wib_header()->get_timestamp(), 0x9ABC12345678);
  BOOST_REQUIRE_EQUAL(from_raw_data->get_coldata_header(0)->get_checksum_a(), 0x3311);
  BOOST_REQUIRE_EQUAL(from_raw_data->get_coldata_header(0)->get_checksum_b(), 0x4422);

  from_raw_data = nullptr;
  free(buff);
}

BOOST_AUTO_TEST_SUITE_END()

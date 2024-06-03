/**
 * @file TriggerRecordHeader_test.cxx TriggerRecordHeader class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

// Disable warnings in light of the use of intentially bad constructors during testing

#pragma GCC diagnostic ignored "-Walloc-size-larger-than="
#pragma GCC diagnostic ignored "-Warray-bounds"
#pragma GCC diagnostic ignored "-Wstringop-overflow="

#include "daqdataformats/TriggerRecordHeader.hpp"
#include "daqdataformats/TriggerRecordHeaderData.hpp"

#pragma GCC diagnostic pop
#pragma GCC diagnostic pop
#pragma GCC diagnostic pop

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE TriggerRecordHeader_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <cstring>
#include <limits>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(TriggerRecordHeader_test)

/**
 * @brief Check that TriggerRecords have appropriate Copy/Move semantics
 */
BOOST_AUTO_TEST_CASE(CopyAndMoveSemantics)
{
  BOOST_REQUIRE(std::is_copy_constructible_v<TriggerRecordHeader>);
  BOOST_REQUIRE(std::is_copy_assignable_v<TriggerRecordHeader>);
  BOOST_REQUIRE(std::is_move_constructible_v<TriggerRecordHeader>);
  BOOST_REQUIRE(std::is_move_assignable_v<TriggerRecordHeader>);
}

/**
 * @brief Check that TriggerRecordHeader constructors function correctly
 */
BOOST_AUTO_TEST_CASE(ExistingHeader)
{
  std::vector<ComponentRequest> components;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 12 };
  components.back().window_begin = 3;
  components.back().window_end = 4;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 56 };
  components.back().window_begin = 7;
  components.back().window_end = 8;

  auto header = new TriggerRecordHeader(components);
  header->set_run_number(9);
  header->set_trigger_number(10);
  header->set_trigger_timestamp(11);
  header->set_trigger_type(12);
  header->set_sequence_number(13);
  header->set_max_sequence_number(14);
  header->set_error_bit(TriggerRecordErrorBits::kMismatch, true);
  header->set_error_bit(TriggerRecordErrorBits::kUnassigned3, true);

  BOOST_REQUIRE_THROW(header->at(header->get_header().num_requested_components), std::range_error);
  BOOST_REQUIRE_THROW((*header)[header->get_header().num_requested_components], std::range_error);

  void* buff = malloc(header->get_total_size_bytes());
  std::memcpy(buff, header->get_storage_location(), header->get_total_size_bytes());

  // Constructor should copy header
  TriggerRecordHeader copy_header(const_cast<void*>(header->get_storage_location()), true);
  delete header; // NOLINT(build/raw_ownership)

  BOOST_REQUIRE_EQUAL(copy_header.get_run_number(), 9);
  BOOST_REQUIRE_EQUAL(copy_header.get_sequence_number(), 13);
  BOOST_REQUIRE_EQUAL(copy_header.get_max_sequence_number(), 14);
  BOOST_REQUIRE_EQUAL(copy_header.get_error_bit(static_cast<TriggerRecordErrorBits>(0)), false);
  BOOST_REQUIRE_EQUAL(copy_header.get_error_bit(static_cast<TriggerRecordErrorBits>(1)), true);
  BOOST_REQUIRE_EQUAL(copy_header.get_header().error_bits, 10);
  BOOST_REQUIRE_EQUAL(copy_header.at(0).window_begin, 3);
  BOOST_REQUIRE_EQUAL(copy_header[1].window_begin, 7);

  {
    // Test copy constructor
    TriggerRecordHeader copy_copy_header(copy_header);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_run_number(), 9);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_sequence_number(), 13);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_max_sequence_number(), 14);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_error_bit(static_cast<TriggerRecordErrorBits>(0)), false);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_error_bit(static_cast<TriggerRecordErrorBits>(1)), true);
    BOOST_REQUIRE_EQUAL(copy_copy_header.get_header().error_bits, 10);
    BOOST_REQUIRE_EQUAL(copy_copy_header.at(0).window_begin, 3);
    BOOST_REQUIRE_EQUAL(copy_copy_header[1].window_begin, 7);
  }
  {
    // Test copy assignment
    TriggerRecordHeader copy_assign_header = copy_header;
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_run_number(), 9);
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_sequence_number(), 13);
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_max_sequence_number(), 14);
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_error_bit(static_cast<TriggerRecordErrorBits>(0)), false);
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_error_bit(static_cast<TriggerRecordErrorBits>(1)), true);
    BOOST_REQUIRE_EQUAL(copy_assign_header.get_header().error_bits, 10);
    BOOST_REQUIRE_EQUAL(copy_assign_header.at(0).window_begin, 3);
    BOOST_REQUIRE_EQUAL(copy_assign_header[1].window_begin, 7);
  }

  {
    // Test Buffer adoption constructor
    TriggerRecordHeader buffer_header(buff, false);

    BOOST_REQUIRE_EQUAL(buffer_header.get_run_number(), 9);
    BOOST_REQUIRE_EQUAL(buffer_header.get_sequence_number(), 13);
    BOOST_REQUIRE_EQUAL(buffer_header.get_max_sequence_number(), 14);
    BOOST_REQUIRE_EQUAL(buffer_header.get_error_bit(static_cast<TriggerRecordErrorBits>(0)), false);
    BOOST_REQUIRE_EQUAL(buffer_header.get_error_bit(static_cast<TriggerRecordErrorBits>(1)), true);
    BOOST_REQUIRE_EQUAL(buffer_header.get_header().error_bits, 10);
    BOOST_REQUIRE_EQUAL(buffer_header.at(0).window_begin, 3);
    BOOST_REQUIRE_EQUAL(buffer_header[1].window_begin, 7);
  }

  BOOST_REQUIRE_EQUAL(*reinterpret_cast<uint32_t*>(buff), // NOLINT
                      TriggerRecordHeaderData::s_trigger_record_header_magic);

  free(buff);
}

BOOST_AUTO_TEST_CASE(MoveConstructor)
{
  std::vector<ComponentRequest> components;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 12 };
  components.back().window_begin = 3;
  components.back().window_end = 4;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 56 };
  components.back().window_begin = 7;
  components.back().window_end = 8;

  auto header = new TriggerRecordHeader(components);

  TriggerRecordHeader another_header(std::move(*header));

  delete header; // NOLINT We are specifically testing what happens when the original trh is deleted

  BOOST_REQUIRE_EQUAL(another_header.get_num_requested_components(), 2);
}

BOOST_AUTO_TEST_CASE(MoveAssignment)
{
  std::vector<ComponentRequest> components;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 12 };
  components.back().window_begin = 3;
  components.back().window_end = 4;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 56 };
  components.back().window_begin = 7;
  components.back().window_end = 8;

  auto header = new TriggerRecordHeader(components);

  auto another_header = std::move(*header);

  delete header; // NOLINT We are specifically testing what happens when the original trh is deleted

  BOOST_REQUIRE_EQUAL(another_header.get_num_requested_components(), 2);
}

BOOST_AUTO_TEST_CASE(BadConstructors)
{
  TriggerRecordHeaderData header_data;
  header_data.num_requested_components = std::numeric_limits<uint64_t>::max() - 10; // NOLINT(build/unsigned)
  header_data.run_number = 9;
  header_data.trigger_number = 10;
  header_data.trigger_timestamp = 11;
  header_data.trigger_type = 12;

  auto hdr = malloc(sizeof(TriggerRecordHeaderData) + sizeof(ComponentRequest));
  std::memcpy(hdr, &header_data, sizeof(TriggerRecordHeaderData));

  BOOST_REQUIRE_EXCEPTION(
    TriggerRecordHeader oversize_header(hdr, true), std::bad_alloc, [&](std::bad_alloc) { return true; });

  header_data.num_requested_components = 1;
  std::memcpy(hdr, &header_data, sizeof(TriggerRecordHeaderData));
  TriggerRecordHeader bad_header(hdr, false);
  BOOST_REQUIRE_EQUAL(bad_header.get_num_requested_components(), 1);

  reinterpret_cast<TriggerRecordHeaderData*>(hdr)->num_requested_components = // NOLINT
    std::numeric_limits<uint64_t>::max() - 10;                                // NOLINT(build/unsigned)
  BOOST_REQUIRE_EQUAL(bad_header.get_num_requested_components(),
                      std::numeric_limits<uint64_t>::max() - 10); // NOLINT(build/unsigned)

  BOOST_REQUIRE_EXCEPTION(
    TriggerRecordHeader header_inst = bad_header, std::bad_alloc, [&](std::bad_alloc) { return true; });

  free(hdr);
}

/**
 * @brief Test header field manipulation methods
 */
BOOST_AUTO_TEST_CASE(HeaderFields)
{
  std::vector<ComponentRequest> components;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 12 };
  components.back().window_begin = 3;
  components.back().window_end = 4;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 56 };
  components.back().window_begin = 7;
  components.back().window_end = 8;

  auto header = new TriggerRecordHeader(components);
  header->set_run_number(9);
  header->set_trigger_number(10);
  header->set_trigger_timestamp(11);
  header->set_trigger_type(12);
  header->set_sequence_number(13);
  header->set_max_sequence_number(14);
  header->set_error_bit(TriggerRecordErrorBits::kMismatch, true);
  header->set_error_bit(TriggerRecordErrorBits::kUnassigned31, true);

  auto header_data = header->get_header();
  BOOST_REQUIRE_EQUAL(header->get_run_number(), header_data.run_number);
  BOOST_REQUIRE_EQUAL(header->get_trigger_number(), header_data.trigger_number);
  BOOST_REQUIRE_EQUAL(header->get_trigger_timestamp(), header_data.trigger_timestamp);
  BOOST_REQUIRE_EQUAL(header->get_trigger_type(), header_data.trigger_type);
  BOOST_REQUIRE_EQUAL(header->get_sequence_number(), header_data.sequence_number);
  BOOST_REQUIRE_EQUAL(header->get_max_sequence_number(), header_data.max_sequence_number);
  BOOST_REQUIRE_EQUAL(header->get_num_requested_components(), 2);
  BOOST_REQUIRE_EQUAL(header->get_num_requested_components(), header_data.num_requested_components);
  BOOST_REQUIRE_EQUAL(header->get_error_bits().to_ulong(), 0x80000002);

  auto header_ptr = static_cast<const TriggerRecordHeaderData*>(header->get_storage_location());
  BOOST_REQUIRE_EQUAL(header_ptr->run_number, header_data.run_number);
  header->set_run_number(10);
  BOOST_REQUIRE(header_ptr->run_number != header_data.run_number);
  BOOST_REQUIRE_EQUAL(header_ptr->run_number, 10);
  header->set_error_bits(std::bitset<32>(0x11111111));
  BOOST_REQUIRE_EQUAL(header_ptr->error_bits, 0x11111111);
}

BOOST_AUTO_TEST_CASE(StreamOperator)
{
  std::vector<ComponentRequest> components;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 12 };
  components.back().window_begin = 3;
  components.back().window_end = 4;
  components.emplace_back();
  components.back().component = { SourceID::Subsystem::kDetectorReadout, 56 };
  components.back().window_begin = 7;
  components.back().window_end = 8;

  auto header = std::make_unique<TriggerRecordHeader>(components);
  header->set_run_number(9);
  header->set_trigger_number(10);
  header->set_trigger_timestamp(11);
  header->set_trigger_type(12);
  header->set_sequence_number(13);
  header->set_max_sequence_number(14);
  header->set_error_bit(TriggerRecordErrorBits::kMismatch, true);
  header->set_error_bit(TriggerRecordErrorBits::kUnassigned3, true);

  auto header_data = header->get_header();
  std::ostringstream oss;
  oss << header_data;
  std::istringstream iss(oss.str());
  TriggerRecordHeaderData trhd;
  iss >> trhd;
  BOOST_REQUIRE_EQUAL(trhd.run_number, header_data.run_number);
  BOOST_REQUIRE_EQUAL(trhd.trigger_number, header_data.trigger_number);
  BOOST_REQUIRE_EQUAL(trhd.trigger_timestamp, header_data.trigger_timestamp);
  BOOST_REQUIRE_EQUAL(trhd.trigger_type, header_data.trigger_type);
  BOOST_REQUIRE_EQUAL(trhd.sequence_number, header_data.sequence_number);
  BOOST_REQUIRE_EQUAL(trhd.max_sequence_number, header_data.max_sequence_number);
  BOOST_REQUIRE_EQUAL(trhd.num_requested_components, header_data.num_requested_components);
}

BOOST_AUTO_TEST_SUITE_END()

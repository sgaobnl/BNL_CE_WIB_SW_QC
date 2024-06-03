/**
 * @file TriggerRecordHeaderData_test.cxx TriggerRecordHeaderData class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/TriggerRecordHeaderData.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE TriggerRecordHeaderData_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(TriggerRecordHeaderData_test)

/**
 * @brief Test that TriggerRecordHeaderData::operator<< functions as expected
 */
BOOST_AUTO_TEST_CASE(StreamOperator)
{
  TriggerRecordHeaderData header;
  header.num_requested_components = 0;
  header.trigger_number = 1;
  header.trigger_timestamp = 2;
  header.run_number = 3;
  header.error_bits = 0xa5;
  header.trigger_type = 4;
  header.sequence_number = 5;
  header.max_sequence_number = 6;
  SourceID sid(SourceID::Subsystem::kTRBuilder, 99);
  header.element_id = sid;

  std::ostringstream ostr;
  ostr << header;
  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);

  BOOST_REQUIRE(!output.empty());
  auto pos = output.find("trigger_number: 1,");
  BOOST_REQUIRE(pos != std::string::npos);
  pos = output.find("trigger_timestamp: 2,");
  BOOST_REQUIRE(pos != std::string::npos);
  pos = output.find("run_number: 3,");
  BOOST_REQUIRE(pos != std::string::npos);

  std::istringstream istr(output);
  TriggerRecordHeaderData reconstituted_header;
  istr >> reconstituted_header;
  BOOST_REQUIRE_EQUAL(reconstituted_header.num_requested_components, 0);
  BOOST_REQUIRE_EQUAL(reconstituted_header.trigger_number, 1);
  BOOST_REQUIRE_EQUAL(reconstituted_header.trigger_timestamp, 2);
  BOOST_REQUIRE_EQUAL(reconstituted_header.run_number, 3);
  BOOST_REQUIRE_EQUAL(reconstituted_header.error_bits, 0xa5);
  BOOST_REQUIRE_EQUAL(reconstituted_header.trigger_type, 4);
  BOOST_REQUIRE_EQUAL(reconstituted_header.sequence_number, 5);
  BOOST_REQUIRE_EQUAL(reconstituted_header.max_sequence_number, 6);
  BOOST_REQUIRE_EQUAL(reconstituted_header.element_id.id, 99);
}

BOOST_AUTO_TEST_SUITE_END()

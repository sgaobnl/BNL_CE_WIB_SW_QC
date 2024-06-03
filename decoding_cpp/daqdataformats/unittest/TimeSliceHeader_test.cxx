/**
 * @file TimeSliceHeader_test.cxx TimeSliceHeader class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/TimeSliceHeader.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE TimeSliceHeader_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(TimeSliceHeader_test)

/**
 * @brief Test that TimeSliceHeader::operator<< functions as expected
 */
BOOST_AUTO_TEST_CASE(StreamOperator)
{
  TimeSliceHeader header;
  header.timeslice_number = 1;
  header.run_number = 2;
  SourceID sid(SourceID::Subsystem::kTRBuilder, 55);
  header.element_id = sid;

  std::ostringstream ostr;
  ostr << header;
  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);

  BOOST_REQUIRE(!output.empty());
  auto pos = output.find("timeslice_number: 1,");
  BOOST_REQUIRE(pos != std::string::npos);
  pos = output.find("run_number: 2");
  BOOST_REQUIRE(pos != std::string::npos);

  std::istringstream istr(output);
  TimeSliceHeader reconstituted_header;
  istr >> reconstituted_header;
  BOOST_REQUIRE_EQUAL(reconstituted_header.timeslice_number, 1);
  BOOST_REQUIRE_EQUAL(reconstituted_header.run_number, 2);
  BOOST_REQUIRE_EQUAL(reconstituted_header.element_id.id, 55);
}

BOOST_AUTO_TEST_SUITE_END()

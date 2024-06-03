/**
 * @file SourceID_test.cxx SourceID struct Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/SourceID.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE SourceID_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <functional>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(SourceID_test)

BOOST_AUTO_TEST_CASE(SubsystemConversion)
{
  BOOST_REQUIRE_EQUAL(SourceID::subsystem_to_string(SourceID::Subsystem::kUnknown), "Unknown");
  BOOST_REQUIRE_EQUAL(SourceID::string_to_subsystem("Unknown"), SourceID::Subsystem::kUnknown);

  BOOST_REQUIRE_EQUAL(SourceID::subsystem_to_string(SourceID::Subsystem::kDetectorReadout), "Detector_Readout");
  BOOST_REQUIRE_EQUAL(SourceID::string_to_subsystem("Detector_Readout"), SourceID::Subsystem::kDetectorReadout);

  BOOST_REQUIRE_EQUAL(SourceID::subsystem_to_string(SourceID::Subsystem::kHwSignalsInterface), "HW_Signals_Interface");
  BOOST_REQUIRE_EQUAL(SourceID::string_to_subsystem("HW_Signals_Interface"), SourceID::Subsystem::kHwSignalsInterface);

  BOOST_REQUIRE_EQUAL(SourceID::subsystem_to_string(SourceID::Subsystem::kTrigger), "Trigger");
  BOOST_REQUIRE_EQUAL(SourceID::string_to_subsystem("Trigger"), SourceID::Subsystem::kTrigger);

  BOOST_REQUIRE_EQUAL(SourceID::subsystem_to_string(SourceID::Subsystem::kTRBuilder), "TR_Builder");
  BOOST_REQUIRE_EQUAL(SourceID::string_to_subsystem("TR_Builder"), SourceID::Subsystem::kTRBuilder);
}

/**
 * @brief Test that SourceID::operator<< functions as expected
 */
BOOST_AUTO_TEST_CASE(StreamOperator)
{
  SourceID test = { SourceID::Subsystem::kDetectorReadout, 314159 };

  std::ostringstream ostr;
  ostr << test;

  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);

  BOOST_REQUIRE(!output.empty());

  auto pos = output.find(std::to_string(test.id));
  BOOST_REQUIRE(pos != std::string::npos);

  BOOST_TEST_MESSAGE("About to try to input from \"" << output << "\"");
  std::istringstream istr(output);
  SourceID test2;
  istr >> test2;
  BOOST_TEST_MESSAGE("Looks like the output-from-the-input is \"" << test2) << "\"";
  BOOST_REQUIRE_EQUAL(test.subsystem, test2.subsystem); // Recall that output was generated from streaming out a SourceID instance

  SourceID::Subsystem cat{ SourceID::Subsystem::kTrigger };
  std::ostringstream cat_ostr;
  cat_ostr << cat;
  std::istringstream cat_istr(cat_ostr.str());
  SourceID::Subsystem cat2{ SourceID::Subsystem::kUnknown };
  cat_istr >> cat2;

  BOOST_REQUIRE_EQUAL(cat, cat2);
}

/**
 * @brief Test that SourceID::operator< functions as expected
 */
BOOST_AUTO_TEST_CASE(ComparisonOperator)
{
  SourceID lesser{ SourceID::Subsystem::kDetectorReadout, 1 };
  SourceID greater{ SourceID::Subsystem::kDetectorReadout, 2 };

  BOOST_REQUIRE(lesser != greater);
  BOOST_REQUIRE(lesser == lesser);
  BOOST_REQUIRE(greater == greater);
  BOOST_REQUIRE(lesser < greater);
  BOOST_REQUIRE(!(greater < lesser));
}

BOOST_AUTO_TEST_CASE(Validity)
{
  SourceID test;
  BOOST_REQUIRE(!test.is_in_valid_state());

  test = { SourceID::Subsystem::kHwSignalsInterface, 3141592 };
  BOOST_REQUIRE(test.is_in_valid_state());

  test.id = SourceID::s_invalid_id;
  BOOST_REQUIRE(!test.is_in_valid_state());
}

BOOST_AUTO_TEST_SUITE_END()

/**
 * @file ComponentRequest_test.cxx ComponentRequest class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/ComponentRequest.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE ComponentRequest_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(ComponentRequest_test)

BOOST_AUTO_TEST_CASE(Constructor)
{
  SourceID test{ SourceID::Subsystem::kDetectorReadout, 12345 };

  ComponentRequest component(test, 3, 4);
  BOOST_REQUIRE_EQUAL(component.window_begin, 3);
  BOOST_REQUIRE_EQUAL(component.window_end, 4);
  BOOST_REQUIRE_EQUAL(component.component, test);
}

/**
 * @brief Test that ComponentRequest::operator<< functions as expected
 */
BOOST_AUTO_TEST_CASE(StreamOperator)
{
  ComponentRequest component;

  SourceID::ID_t arbitrary_id = 6789;
  SourceID test = { SourceID::Subsystem::kDetectorReadout, arbitrary_id };

  component.component = test;
  component.window_begin = 3;
  component.window_end = 4;

  std::ostringstream ostr;
  ostr << component;

  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);

  BOOST_REQUIRE(!output.empty());
  auto pos = output.find(std::to_string(arbitrary_id));
  BOOST_REQUIRE(pos != std::string::npos);
  pos = output.find("begin: 3,");
  BOOST_REQUIRE(pos != std::string::npos);

  std::istringstream istr(output);
  ComponentRequest component_from_stream;
  istr >> component_from_stream;
  BOOST_REQUIRE_EQUAL(component_from_stream.component, component.component);
  BOOST_REQUIRE_EQUAL(component_from_stream.window_begin, component.window_begin);
  BOOST_REQUIRE_EQUAL(component_from_stream.window_end, component.window_end);
}

BOOST_AUTO_TEST_SUITE_END()

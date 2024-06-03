
/**
 * @file DetID_test.cxx DetID class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2022.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "detdataformats/DetID.hpp"

#define BOOST_TEST_MODULE DetID_test 

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::detdataformats;

BOOST_AUTO_TEST_SUITE(DetID_test)

BOOST_AUTO_TEST_CASE(Comprehensive)
{

  DetID detid = { DetID::Subdetector::kND_GAr };

  BOOST_REQUIRE(detid.is_in_valid_state());

  std::ostringstream ostr;
  ostr << detid;
  std::string output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);

  BOOST_REQUIRE(!output.empty());
  auto pos = output.find("subdetector: ND_GAr");
  BOOST_REQUIRE(pos != std::string::npos);

  std::istringstream iss(ostr.str());
  DetID detid_from_stream;
  iss >> detid_from_stream;
  BOOST_REQUIRE_EQUAL(detid_from_stream.version, detid.version);
  BOOST_REQUIRE_EQUAL(detid_from_stream.subdetector, detid.subdetector);

  DetID detid_default;
  BOOST_REQUIRE(!detid_default.is_in_valid_state());

}

BOOST_AUTO_TEST_SUITE_END()

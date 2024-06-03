/**
 * @file WIBtoWIB2_test.cxx Unit Tests for the WIB -> WIB2 file converter
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE WIBtoWIB2_test // NOLINT

#include "boost/test/unit_test.hpp"

#include "rawdatautils/WIBtoWIB2.hpp"
#include "fddetdataformats/WIBFrame.hpp"

#include <random>

namespace dunedaq{
namespace rawdatautils{

BOOST_AUTO_TEST_SUITE(WIBtoWIB2_test)

std::mt19937 mt(1000007);

BOOST_AUTO_TEST_CASE(WIBtoWIB2_test1)
{

  std::uniform_real_distribution<double> dist(0, 4096);

  std::vector<int> adcs;
  for (int i = 0; i < 256; i++) {
    int num = dist(mt);
    adcs.push_back(num);
  }
  
  fddetdataformats::WIBFrame fr;
  for (int i = 0; i < 256; i++){
    fr.set_channel(i, adcs[i]);
  }
  auto header = fr.get_wib_header();
  header->version = 31;
  header->crate_no = 31;
  header->slot_no = 7;
  header->fiber_no = 7;
  fr.set_timestamp(1844674407370955161U); //2**48-1

  auto wib2fr = wibtowib2(&fr, 1844674407370955161U);
  for (int i = 0; i < 256; i++){
    BOOST_REQUIRE_EQUAL(adcs[i], wib2fr.get_adc(i));
  }
  BOOST_REQUIRE_EQUAL(wib2fr.header.version, 31);
  BOOST_REQUIRE_EQUAL(wib2fr.header.crate, 31);
  BOOST_REQUIRE_EQUAL(wib2fr.header.slot, 7);
  BOOST_REQUIRE_EQUAL(wib2fr.header.link, 7);
  BOOST_REQUIRE_EQUAL(wib2fr.get_timestamp(), 1844674407370955161U);
}

} // namespace dunedaq
} // namespace rawdatautils

BOOST_AUTO_TEST_SUITE_END()

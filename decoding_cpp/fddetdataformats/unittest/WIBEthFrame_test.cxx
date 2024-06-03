
/**
 * @file WIBEthFrame_test.cxx WIBEthFrame class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2022.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIBEthFrame.hpp"

#define BOOST_TEST_MODULE WIBEthFrame_test

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>
#include <random>

BOOST_AUTO_TEST_SUITE(WIBEthFrame_test)

BOOST_AUTO_TEST_CASE(WIBEthFrame_ADCDataMutators)
{
  // RNG with max 14 bit values
  std::random_device dev;
  std::mt19937 rng(dev());
  int max_adc_value = (unsigned)(1<<14)-1;
  std::uniform_int_distribution<std::mt19937::result_type> dist(1, max_adc_value);

  // Prepare source vector with ADC samples
  std::vector<std::vector<uint16_t>> v;
  for(int i=0; i<64; ++i) {
    v.emplace_back(std::vector<uint16_t>(64));
    for (int j=0; j<64; ++j) {
      auto rand_val = dist(rng);
      v[i][j] = ((uint16_t)rand_val);
    }
  }

  // Set ADCs from ADC samples
  dunedaq::fddetdataformats::WIBEthFrame wibethframe {};
  for(std::size_t i=0; i<v.size(); ++i) {
    for(std::size_t j=0; j<v[i].size(); ++j) {
      wibethframe.set_adc(i, j, v[i][j]);
    }
  }

  // Get ADCs and compare
  for(std::size_t i=0; i<v.size(); ++i) {
    for(std::size_t j=0; j<v[i].size(); ++j) {
      BOOST_REQUIRE_EQUAL(wibethframe.get_adc(i, j), v[i][j]);
    }
  }

}

BOOST_AUTO_TEST_SUITE_END()

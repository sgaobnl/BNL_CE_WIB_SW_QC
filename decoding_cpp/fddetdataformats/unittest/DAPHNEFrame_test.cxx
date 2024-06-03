
/**
 * @file DAPHNEFrame_test.cxx DAPHNEFrame class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2022.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/DAPHNEFrame.hpp"

#define BOOST_TEST_MODULE DAPHNEFrame_test

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>
#include <random>

BOOST_AUTO_TEST_SUITE(DAPHNEFrame_test)

BOOST_AUTO_TEST_CASE(WIBEthFrame_ADCDataMutators)
{
  std::random_device dev;
  std::mt19937 rng(dev());
  std::uniform_int_distribution<std::mt19937::result_type> dist(1,(1<<14)-1);
  std::vector<int> v;

  for(int i=0; i<320; i++) {
    v.push_back(dist(rng));
  }

  dunedaq::fddetdataformats::DAPHNEFrame daphneframe {};
  for(int i=0; i<320; i++) {
    daphneframe.set_adc(i, v[i]);
  }

  for(int i=0; i<320; i++) {
    BOOST_REQUIRE_EQUAL(daphneframe.get_adc(i), v[i]);
  }

}

BOOST_AUTO_TEST_SUITE_END()

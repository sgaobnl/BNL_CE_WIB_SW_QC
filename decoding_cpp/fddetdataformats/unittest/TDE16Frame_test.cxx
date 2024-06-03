
/**
 * @file TDE16Frame_test.cxx TDE16Frame class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2022.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/TDE16Frame.hpp"

#define BOOST_TEST_MODULE TDE16Frame_test 

#include "boost/test/unit_test.hpp"

#include <string>
#include <vector>

using namespace dunedaq::fddetdataformats;

BOOST_AUTO_TEST_SUITE(TDE16Frame_test)

BOOST_AUTO_TEST_CASE(TDE16Frame_StructMethods)
{
  TDE16Frame tde16frame {};

  BOOST_REQUIRE(tde16frame.get_daq_header() != nullptr);
  BOOST_REQUIRE(tde16frame.get_tde_header() != nullptr);
}

BOOST_AUTO_TEST_CASE(TDE16Frame_HeaderMutators)
{
  TDE16Frame tde16frame {};
  tde16frame.set_tde_errors(0xFC5F);
  tde16frame.set_timestamp(0x444455555555);

  BOOST_REQUIRE_EQUAL(tde16frame.get_tde_header()->tde_errors, 0xFC5F);
  BOOST_REQUIRE_EQUAL(tde16frame.get_daq_header()->timestamp, 0x444455555555);
}

BOOST_AUTO_TEST_CASE(TDE16Frame_StreamOperator)
{
  TDE16Frame tde16frame {};

  std::ostringstream ostr;
  ostr << tde16frame;
  auto output = ostr.str();
  BOOST_TEST_MESSAGE("Stream operator: " << output);
  BOOST_REQUIRE(!output.empty());
}

BOOST_AUTO_TEST_CASE(TDE16Frame_ADCDataMutators)
{
  TDE16Frame tde16frame {};
  for(int i=0; i<tot_adc16_samples; i++) { tde16frame.set_adc_sample(0x63, i); }

  for(int i=0; i<30; i++) { BOOST_REQUIRE_EQUAL(tde16frame.get_adc_sample(i), 0x63); }
  for(int i=tot_adc16_samples-20; i<tot_adc16_samples; i++) { BOOST_REQUIRE_EQUAL(tde16frame.get_adc_sample(i), 0x63); }
}

BOOST_AUTO_TEST_CASE(TDE16Frame_FromRawData)
{
  dunedaq::detdataformats::DAQEthHeader daq_header {};
  daq_header.timestamp = 0x222211111111;
  TDEHeader tde_header {};
  Sample samples_info[tot_adc16_samples] {};
  
  uint8_t* buff = static_cast<uint8_t*>(malloc(sizeof(daq_header)+sizeof(tde_header) + sizeof(samples_info))); 
  memcpy(buff, &daq_header, sizeof(daq_header));
  memcpy(buff + sizeof(daq_header) + sizeof(tde_header), samples_info, sizeof(Sample) * tot_adc16_samples);
  TDE16Frame* from_raw_data = reinterpret_cast<TDE16Frame*>(buff); 

  BOOST_REQUIRE_EQUAL(from_raw_data->get_timestamp(), 0x222211111111);

  from_raw_data = nullptr;
  free(buff);
}

BOOST_AUTO_TEST_SUITE_END()

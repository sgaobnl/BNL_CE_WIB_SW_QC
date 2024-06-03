/**
 * @file TimeSlice_test.cxx TimeSlice class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "daqdataformats/TimeSlice.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE TimeSlice_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <memory>
#include <string>
#include <utility>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(TimeSlice_test)

/**
 * @brief Check that TimeSlices have appropriate Copy/Move semantics
 */
BOOST_AUTO_TEST_CASE(CopyAndMoveSemantics)
{
  BOOST_REQUIRE(!std::is_copy_constructible_v<TimeSlice>);
  BOOST_REQUIRE(!std::is_copy_assignable_v<TimeSlice>);
  BOOST_REQUIRE(std::is_move_constructible_v<TimeSlice>);
  BOOST_REQUIRE(std::is_move_assignable_v<TimeSlice>);
}

BOOST_AUTO_TEST_CASE(InitializerConstructor)
{
  auto record = std::make_unique<TimeSlice>(1, 2);
  BOOST_REQUIRE_EQUAL(record->get_header().timeslice_number, 1);
  BOOST_REQUIRE_EQUAL(record->get_header().run_number, 2);
}

/**
 * @brief Test constructor that uses and existing TimeSliceHeader
 */
BOOST_AUTO_TEST_CASE(HeaderConstructor)
{

  TimeSliceHeader header;
  header.timeslice_number = 1;
  header.run_number = 2;
  auto record = std::make_unique<TimeSlice>(header);
  BOOST_REQUIRE_EQUAL(record->get_header().timeslice_number, 1);
  BOOST_REQUIRE_EQUAL(record->get_header().run_number, 2);
}

/**
 *@brief Test TimeSliceHeader manipulation methods
 */
BOOST_AUTO_TEST_CASE(HeaderManipulation)
{
  TimeSlice record(1, 2);
  BOOST_REQUIRE_EQUAL(record.get_header().timeslice_number, 1);
  BOOST_REQUIRE_EQUAL(record.get_header().run_number, 2);

  TimeSliceHeader new_header;
  new_header.timeslice_number = 3;
  new_header.run_number = 4;
  record.set_header(new_header);
  BOOST_REQUIRE_EQUAL(record.get_header().timeslice_number, 3);
  BOOST_REQUIRE_EQUAL(record.get_header().run_number, 4);
}

/**
 * @brief Test Fragment vector manipulation methods
 */
BOOST_AUTO_TEST_CASE(FragmentManipulation)
{
  TimeSlice record(1, 2);

  BOOST_REQUIRE_EQUAL(record.get_fragments_ref().size(), 0);

  std::vector<uint8_t> buf1(10);
  auto frag = std::make_unique<Fragment>(buf1.data(), buf1.size());
  record.add_fragment(std::move(frag));
  BOOST_REQUIRE_EQUAL(record.get_fragments_ref().size(), 1);
  BOOST_REQUIRE_EQUAL(record.get_fragments_ref()[0]->get_size(), sizeof(FragmentHeader) + 10);

  std::vector<std::unique_ptr<Fragment>> new_vector;
  record.set_fragments(std::move(new_vector));
  BOOST_REQUIRE_EQUAL(record.get_fragments_ref().size(), 0);
}

BOOST_AUTO_TEST_SUITE_END()

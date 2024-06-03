/**
 * @file Fragment_test.cxx Fragment class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

// Disable warnings in light of the use of intentially bad constructors during testing

#pragma GCC diagnostic ignored "-Warray-bounds"
#pragma GCC diagnostic ignored "-Wstringop-overflow="
#pragma GCC diagnostic ignored "-Walloc-size-larger-than="

#include "daqdataformats/Fragment.hpp"

#pragma GCC diagnostic pop
#pragma GCC diagnostic pop
#pragma GCC diagnostic pop

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE Fragment_test // NOLINT

#include "boost/test/unit_test.hpp"

#include <memory>
#include <string>
#include <utility>
#include <vector>

using namespace dunedaq::daqdataformats;

BOOST_AUTO_TEST_SUITE(Fragment_test)

/**
 * @brief Check that Fragments have appropriate Copy/Move semantics
 */
BOOST_AUTO_TEST_CASE(CopyAndMoveSemantics)
{
  BOOST_REQUIRE(!std::is_copy_constructible_v<Fragment>);
  BOOST_REQUIRE(!std::is_copy_assignable_v<Fragment>);
  BOOST_REQUIRE(std::is_move_constructible_v<Fragment>);
  BOOST_REQUIRE(std::is_move_assignable_v<Fragment>);
}

/**
 * @brief Test constructors that gather existing data buffers
 */
BOOST_AUTO_TEST_CASE(DataConstructors)
{
  std::vector<uint8_t> buf1(10);
  Fragment single_frag(buf1.data(), buf1.size());
  BOOST_REQUIRE_EQUAL(single_frag.get_size(), sizeof(FragmentHeader) + buf1.size());

  std::vector<uint8_t> buf2(20);
  Fragment collect_frag({ { buf1.data(), buf1.size() }, { buf2.data(), buf2.size() } });
  BOOST_REQUIRE_EQUAL(collect_frag.get_size(), sizeof(FragmentHeader) + buf1.size() + buf2.size());
}

/**
 * @brief Test construction of invalid Fragments
 */
BOOST_AUTO_TEST_CASE(BadConstructors)
{
  std::unique_ptr<Fragment> fragment_ptr{};

  BOOST_REQUIRE_EXCEPTION(fragment_ptr.reset(new Fragment(nullptr, size_t(100))),
                          std::invalid_argument,
                          [&](std::invalid_argument) { return true; });
  BOOST_REQUIRE_EXCEPTION(
    fragment_ptr.reset(new Fragment(nullptr, size_t(-1))), std::length_error, [&](std::length_error) { return true; });

  BOOST_REQUIRE_EXCEPTION(
    fragment_ptr.reset(new Fragment({ nullptr, size_t(-1) - sizeof(dunedaq::daqdataformats::FragmentHeader) })),
    std::bad_alloc,
    [&](std::bad_alloc) { return true; });

  auto bufsize = 10;
  std::vector<uint8_t> buf1(bufsize);
  fragment_ptr.reset(new Fragment(buf1.data(), buf1.size()));
  BOOST_REQUIRE_EQUAL(fragment_ptr->get_size(), sizeof(FragmentHeader) + bufsize);
}

/**
 * @brief Check that Fragment constructors function correctly
 */
BOOST_AUTO_TEST_CASE(ExistingFragmentConstructor)
{
  FragmentHeader header;
  header.size = sizeof(FragmentHeader) + 4;
  header.trigger_number = 1;
  header.trigger_timestamp = 2;
  header.run_number = 3;

  auto frag = malloc(sizeof(FragmentHeader) + 4);
  memcpy(frag, &header, sizeof(FragmentHeader));

  uint8_t one = 1, two = 2, three = 3, four = 4;                               // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader), &one, 1);       // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 1, &two, 1);   // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 2, &three, 1); // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 3, &four, 1);  // NOLINT(build/unsigned)

  {
    Fragment test_frag(frag, Fragment::BufferAdoptionMode::kReadOnlyMode);

    BOOST_REQUIRE_EQUAL(test_frag.get_storage_location(), frag);

    BOOST_REQUIRE_EQUAL(test_frag.get_trigger_number(), 1);
    BOOST_REQUIRE_EQUAL(test_frag.get_trigger_timestamp(), 2);
    BOOST_REQUIRE_EQUAL(test_frag.get_run_number(), 3);

    BOOST_REQUIRE_EQUAL(*static_cast<uint8_t*>(test_frag.get_data()), one);         // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 1), two);   // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 2), three); // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 3), four);  // NOLINT(build/unsigned)
  }
  free(frag); // Should not cause errors

  frag = malloc(sizeof(FragmentHeader) + 4);
  memcpy(frag, &header, sizeof(FragmentHeader));
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader), &four, 1);      // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 1, &three, 1); // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 2, &two, 1);   // NOLINT(build/unsigned)
  memcpy(static_cast<uint8_t*>(frag) + sizeof(FragmentHeader) + 3, &one, 1);   // NOLINT(build/unsigned)

  {
    Fragment test_frag(frag, Fragment::BufferAdoptionMode::kCopyFromBuffer);

    BOOST_REQUIRE(test_frag.get_storage_location() != frag);
    BOOST_REQUIRE_EQUAL(test_frag.get_trigger_number(), 1);
    BOOST_REQUIRE_EQUAL(test_frag.get_trigger_timestamp(), 2);
    BOOST_REQUIRE_EQUAL(test_frag.get_run_number(), 3);

    BOOST_REQUIRE_EQUAL(*static_cast<uint8_t*>(test_frag.get_data()), four);        // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 1), three); // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 2), two);   // NOLINT(build/unsigned)
    BOOST_REQUIRE_EQUAL(*(static_cast<uint8_t*>(test_frag.get_data()) + 3), one);   // NOLINT(build/unsigned)
  }

  {
    using blobtype_t = uint8_t; // NOLINT(build/unsigned)

    constexpr int blob1_num_elements = 123;
    constexpr int blob2_num_elements = 456;
    std::array<blobtype_t, blob1_num_elements> blob1;
    std::array<blobtype_t, blob2_num_elements> blob2;

    Fragment test_frag(
      std::vector<std::pair<void*, size_t>>({ { &blob1[0], blob1_num_elements }, { &blob2[0], blob2_num_elements } }));

    BOOST_REQUIRE_EQUAL(sizeof(FragmentHeader) + blob1_num_elements + blob2_num_elements, test_frag.get_size());
  }

  free(frag); // Should not cause errors
}

BOOST_AUTO_TEST_CASE(BadExistingFragmentConstructor)
{
  FragmentHeader header;
  header.size = -1;
  header.trigger_number = 1;
  header.trigger_timestamp = 2;
  header.run_number = 3;

  auto frag = malloc(sizeof(FragmentHeader) + 4);
  memcpy(frag, &header, sizeof(FragmentHeader));

  std::unique_ptr<Fragment> fragment_ptr{};
  BOOST_REQUIRE_EXCEPTION(fragment_ptr.reset(new Fragment(frag, Fragment::BufferAdoptionMode::kCopyFromBuffer)),
                          std::bad_alloc,
                          [&](std::bad_alloc) { return true; });
  free(frag);

  // Use fragment_ptr
  auto bufsize = 10;
  auto buf1 = malloc(bufsize);
  fragment_ptr.reset(new Fragment(buf1, size_t(bufsize)));
  BOOST_REQUIRE_EQUAL(fragment_ptr->get_size(), sizeof(FragmentHeader) + bufsize);
}

BOOST_AUTO_TEST_CASE(MoveConstructor)
{
  auto buf1 = malloc(10);
  auto single_frag = new Fragment(buf1, size_t(10));
  BOOST_REQUIRE_EQUAL(single_frag->get_size(), sizeof(FragmentHeader) + 10);

  Fragment another_frag(std::move(*single_frag));

  delete single_frag; // NOLINT We are specifically testing what happens when the original frag is deleted

  BOOST_REQUIRE_EQUAL(another_frag.get_size(), sizeof(FragmentHeader) + 10);
}

BOOST_AUTO_TEST_CASE(MoveAssignment)
{
  auto buf1 = malloc(10);
  auto single_frag = new Fragment(buf1, size_t(10));
  BOOST_REQUIRE_EQUAL(single_frag->get_size(), sizeof(FragmentHeader) + 10);

  auto another_frag = std::move(*single_frag);

  delete single_frag; // NOLINT We are specifically testing what happens when the original frag is deleted

  BOOST_REQUIRE_EQUAL(another_frag.get_size(), sizeof(FragmentHeader) + 10);
}

/**
 * @brief Test header field manipulation methods
 */
BOOST_AUTO_TEST_CASE(HeaderFields)
{

  FragmentHeader header;
  header.size = sizeof(FragmentHeader) + 4;
  header.trigger_number = 1;
  header.trigger_timestamp = 2;
  header.run_number = 3;
  header.window_begin = 4;
  header.window_end = 5;

  SourceID component{ SourceID::Subsystem::kDetectorReadout, 123456789 };
  header.element_id = component;

  header.error_bits = 0x12345678;
  header.fragment_type = 8;
  header.sequence_number = 9;

  auto buf1 = malloc(10);
  Fragment frag(buf1, size_t(10));
  BOOST_REQUIRE_EQUAL(frag.get_size(), sizeof(FragmentHeader) + 10);

  frag.set_header_fields(header);
  BOOST_REQUIRE_EQUAL(frag.get_size(), sizeof(FragmentHeader) + 10);
  BOOST_REQUIRE_EQUAL(frag.get_header().run_number, header.run_number);
  BOOST_REQUIRE_EQUAL(frag.get_trigger_number(), header.trigger_number);
  BOOST_REQUIRE_EQUAL(frag.get_run_number(), header.run_number);
  BOOST_REQUIRE_EQUAL(frag.get_trigger_timestamp(), header.trigger_timestamp);
  BOOST_REQUIRE_EQUAL(frag.get_window_begin(), header.window_begin);
  BOOST_REQUIRE_EQUAL(frag.get_window_end(), header.window_end);
  BOOST_REQUIRE_EQUAL(frag.get_element_id(), header.element_id);

  BOOST_REQUIRE_EQUAL(frag.get_error_bits().to_ulong(), header.error_bits);
  BOOST_REQUIRE_EQUAL(frag.get_error_bit(static_cast<FragmentErrorBits>(3)), true);

  BOOST_REQUIRE_EQUAL(frag.get_fragment_type_code(), header.fragment_type);
  BOOST_REQUIRE_EQUAL(static_cast<fragment_type_t>(frag.get_fragment_type()), header.fragment_type);

  BOOST_REQUIRE_EQUAL(frag.get_sequence_number(), header.sequence_number);

  auto theHeader = static_cast<const FragmentHeader*>(frag.get_storage_location());
  frag.set_trigger_number(0x11);
  BOOST_REQUIRE_EQUAL(theHeader->trigger_number, 0x11);
  frag.set_run_number(0x33);
  BOOST_REQUIRE_EQUAL(theHeader->run_number, 0x33);
  frag.set_trigger_timestamp(0x22);
  BOOST_REQUIRE_EQUAL(theHeader->trigger_timestamp, 0x22);
  frag.set_window_begin(0x44);
  BOOST_REQUIRE_EQUAL(theHeader->window_begin, 0x44);
  frag.set_window_end(0x55);
  BOOST_REQUIRE_EQUAL(theHeader->window_end, 0x55);
  frag.set_type(static_cast<FragmentType>(0x88));
  BOOST_REQUIRE_EQUAL(theHeader->fragment_type, 0x88);
  frag.set_sequence_number(0x99);
  BOOST_REQUIRE_EQUAL(theHeader->sequence_number, 0x99);

  SourceID new_component{ SourceID::Subsystem::kDetectorReadout, 0x6677 };
  frag.set_element_id(new_component);
  BOOST_REQUIRE_EQUAL(theHeader->element_id.subsystem, SourceID::Subsystem::kDetectorReadout);
  BOOST_REQUIRE_EQUAL(theHeader->element_id.id, 0x6677);

  std::bitset<32> no_errors(0);
  frag.set_error_bits(no_errors);
  BOOST_REQUIRE_EQUAL(theHeader->error_bits, 0);
  frag.set_error_bit(static_cast<FragmentErrorBits>(1), true);
  BOOST_REQUIRE_EQUAL(theHeader->error_bits, 2);
  frag.set_error_bit(static_cast<FragmentErrorBits>(1), false);
  BOOST_REQUIRE_EQUAL(theHeader->error_bits, 0);
}

BOOST_AUTO_TEST_SUITE_END()

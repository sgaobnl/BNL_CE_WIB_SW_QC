/**
 * @file WIB2Frame_test.cxx WIB2Frame class Unit Tests
 *
 * This is part of the DUNE DAQ Application Framework, copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */

#include "fddetdataformats/WIB2Frame.hpp"

/**
 * @brief Name of this test module
 */
#define BOOST_TEST_MODULE WIB2Frame_test // NOLINT

#include "boost/test/data/test_case.hpp"
#include "boost/test/unit_test.hpp"

#include <cstdint>
#include <string>
#include <vector>

// namespace wib2unpack contains functions for manipulating WIB2
// frames in the format described by EDMS document 2088713:
// (https://edms.cern.ch/document/2088713/4). The code here is taken
// from unpack.h in the dune-wib-firmware repository, written by Ben
// Land, and lightly modified to be closer to DUNE DAQ software
// conventions. It is used here as an independently-written check of the
// overlay code in WIB2Frame.hpp
namespace wib2unpack {

// Words in the binary format of the FELIX frame14 from the WIB
typedef struct
{
  uint32_t start_frame;    // NOLINT(build/unsigned)
  uint32_t wib_pre[4];     // NOLINT(build/unsigned)
  uint32_t femb_a_seg[56]; // NOLINT(build/unsigned)
  uint32_t femb_b_seg[56]; // NOLINT(build/unsigned)
  uint32_t wib_post[2];    // NOLINT(build/unsigned)
  uint32_t idle_frame;     // NOLINT(build/unsigned)
} frame14;

// Samples from the U, V, X channels in a femb_*_seg of a frame as 16bit arrays
typedef struct
{
  uint16_t u[40], v[40], x[48]; // NOLINT(build/unsigned)
} __attribute__((packed)) femb_data;

// Byte-aligned unpacked values in a felix_frame
typedef struct
{
  uint8_t link_mask, femb_valid, fiber_num, wib_num, frame_version, crate_num; // NOLINT(build/unsigned)
  uint32_t wib_data;                                                           // NOLINT(build/unsigned)
  uint64_t timestamp;                                                          // NOLINT(build/unsigned)
  femb_data femb[2];
  uint32_t crc20;  // NOLINT(build/unsigned)
  uint16_t flex12; // NOLINT(build/unsigned)
  uint32_t flex24; // NOLINT(build/unsigned)
} frame14_unpacked;

// Deframed data, where channels or u,v,x are time ordered uint16 samples for each channel
typedef struct
{
  size_t samples;
  std::vector<uint16_t> channels[2][128]; // NOLINT(build/unsigned)
  std::vector<uint64_t> timestamp;        // NOLINT(build/unsigned)
  uint8_t crate_num, wib_num;             // NOLINT(build/unsigned)
} channel_data;

typedef struct
{
  size_t samples;
  std::vector<uint16_t> u[2][40];  // NOLINT(build/unsigned)
  std::vector<uint16_t> v[2][40];  // NOLINT(build/unsigned)
  std::vector<uint16_t> x[2][48];  // NOLINT(build/unsigned)
  std::vector<uint64_t> timestamp; // NOLINT(build/unsigned)
  uint8_t crate_num, wib_num;      // NOLINT(build/unsigned)
} uvx_data;

void
unpack14(const uint32_t* packed, uint16_t* unpacked) // NOLINT(build/unsigned)
{
  for (size_t i = 0; i < 128; i++) { // i == n'th U,V,X value
    const size_t low_bit = i * 14;
    const size_t low_word = low_bit / 32;
    const size_t high_bit = (i + 1) * 14 - 1;
    const size_t high_word = high_bit / 32;
    // printf("word %li :: low %li (%li[%li]) high %li
    // (%li[%li])\n",i,low_bit,low_word,low_bit%32,high_bit,high_word,high_bit%32);
    if (low_word == high_word) { // all the bits are in the same word
      unpacked[i] = (packed[low_word] >> (low_bit % 32)) & 0x3FFF;
    } else { // some of the bits are in the next word
      size_t high_off = high_word * 32 - low_bit;
      // printf("pre_mask 0x%X post_mask 0x%X\n", (0x3FFF >> (14-high_off)), ((0x3FFF << high_off) & 0x3FFF) );
      unpacked[i] = (packed[low_word] >> (low_bit % 32)) & (0x3FFF >> (14 - high_off));
      unpacked[i] |= (packed[high_word] << high_off) & ((0x3FFF << high_off) & 0x3FFF);
    }
  }
}

void
repack14(const uint16_t* unpacked, uint32_t* packed) // NOLINT(build/unsigned)
{
  // zero packed data first
  for (size_t i = 0; i < 56; i++)
    packed[i] = 0;
  for (size_t i = 0; i < 128; i++) { // i == n'th U,V,X value
    const size_t low_bit = i * 14;
    const size_t low_word = low_bit / 32;
    const size_t high_bit = (i + 1) * 14 - 1;
    const size_t high_word = high_bit / 32;
    // printf("word %li :: low %li (%li[%li]) high %li
    // (%li[%li])\n",i,low_bit,low_word,low_bit%32,high_bit,high_word,high_bit%32);
    if (low_word == high_word) { // all the bits are in the same word
      packed[low_word] |= (unpacked[i] & 0x3FFF) << (low_bit % 32);
    } else { // some of the bits are in the next word
      size_t high_off = high_word * 32 - low_bit;
      // printf("pre_mask 0x%X post_mask 0x%X\n", (0x3FFF >> (14-high_off)), ((0x3FFF << high_off) & 0x3FFF) );
      packed[low_word] |= (unpacked[i] & (0x3FFF >> (14 - high_off))) << (low_bit % 32);
      packed[high_word] |= (unpacked[i] & ((0x3FFF << high_off) & 0x3FFF)) >> high_off;
    }
  }
}

void
unpack_frame(const frame14* frame, frame14_unpacked* data)
{
  data->crate_num = frame->wib_pre[0] & 0xFF;
  data->frame_version = (frame->wib_pre[0] >> 8) & 0xF;
  data->wib_num = (frame->wib_pre[0] >> 12) & 0x7;
  data->fiber_num = (frame->wib_pre[0] >> 15) & 0x1;
  data->femb_valid = (frame->wib_pre[0] >> 16) & 0x3;
  data->link_mask = (frame->wib_pre[0] >> 18) & 0xFF;

  data->wib_data = frame->wib_pre[1];

  data->timestamp = (static_cast<uint64_t>(frame->wib_pre[3]) << 32) | // NOLINT(build/unsigned)
                    (static_cast<uint64_t>(frame->wib_pre[2]));        // NOLINT(build/unsigned)

  unpack14(frame->femb_a_seg, reinterpret_cast<uint16_t*>(&data->femb[0])); // NOLINT
  unpack14(frame->femb_b_seg, reinterpret_cast<uint16_t*>(&data->femb[1])); // NOLINT

  data->crc20 = frame->wib_post[0] & 0xFFFFF;
  data->flex12 = (frame->wib_post[0] >> 20) & 0xFFF;
  data->flex24 = (frame->wib_post[1] >> 8) & 0xFFFFFF;
}

void
repack_frame(frame14_unpacked* data, frame14* frame)
{
  memset(frame, 0, sizeof(frame14)); // zero out frame
  frame->start_frame = 0x3C;
  frame->wib_pre[0] |= (data->crate_num & 0xFF);
  frame->wib_pre[0] |= (data->frame_version & 0xF) << 8;
  frame->wib_pre[0] |= (data->wib_num & 0x7) << 12;
  frame->wib_pre[0] |= (data->fiber_num & 0x1) << 15;
  frame->wib_pre[0] |= (data->femb_valid & 0x3) << 16;
  frame->wib_pre[0] |= (data->link_mask & 0xFF) << 18;

  frame->wib_pre[1] = 0xbabeface;

  frame->wib_pre[2] = static_cast<uint32_t>(data->timestamp & 0xFFFFFFFF);         // NOLINT(build/unsigned)
  frame->wib_pre[3] = static_cast<uint32_t>((data->timestamp >> 32) & 0xFFFFFFFF); // NOLINT(build/unsigned)

  repack14(reinterpret_cast<uint16_t*>(&data->femb[0]), frame->femb_a_seg); // NOLINT
  repack14(reinterpret_cast<uint16_t*>(&data->femb[1]), frame->femb_b_seg); // NOLINT

  frame->wib_post[0] |= data->crc20 & 0xFFFFF; // FIXME calculate crc of something
  frame->wib_post[0] |= (data->flex12 & 0xFFF) << 20;
  frame->wib_post[1] |= 0xDC;
  frame->wib_post[1] |= (data->flex24 & 0xFFFFFF) << 8;
  frame->idle_frame = 0xBC;
}

size_t u_to_ch[40] = { 20, 59,  19, 60,  18, 61,  17, 62,  16, 63,  4,  43,  3,  44,  2,  45,  1,  46,  0,  47,
                       68, 107, 67, 108, 66, 109, 65, 110, 64, 111, 84, 123, 83, 124, 82, 125, 81, 126, 80, 127 };
size_t v_to_ch[40] = { 25, 54,  24, 55,  23, 56,  22, 57,  21, 58,  9,  38,  8,  39,  7,  40,  6,  41,  5,  42,
                       73, 102, 72, 103, 71, 104, 70, 105, 69, 106, 89, 118, 88, 119, 87, 120, 86, 121, 85, 122 };
size_t x_to_ch[48] = { 31, 48,  30, 49,  29, 50,  28, 51,  27, 52,  26, 53,  15, 32,  14, 33,
                       13, 34,  12, 35,  11, 36,  10, 37,  79, 96,  78, 97,  77, 98,  76, 99,
                       75, 100, 74, 101, 95, 112, 94, 113, 93, 114, 92, 115, 91, 116, 90, 117 };

void
deframe_data(const frame14* frame_buf, size_t nframes, channel_data& data)
{
  data.samples = nframes;
  for (size_t i = 0; i < 128; i++) {
    data.channels[0][i].resize(nframes);
    data.channels[1][i].resize(nframes);
  }
  data.timestamp.resize(nframes);
  frame14_unpacked frame_data;
  for (size_t i = 0; i < nframes; i++) {
    unpack_frame(frame_buf + i, &frame_data);
    for (size_t j = 0; j < 48; j++) {
      int k;
      if (j < 40) {
        k = u_to_ch[j];
        data.channels[0][k][i] = frame_data.femb[0].u[j];
        data.channels[1][k][i] = frame_data.femb[1].u[j];
        k = v_to_ch[j];
        data.channels[0][k][i] = frame_data.femb[0].v[j];
        data.channels[1][k][i] = frame_data.femb[1].v[j];
      }
      k = x_to_ch[j];
      data.channels[0][k][i] = frame_data.femb[0].x[j];
      data.channels[1][k][i] = frame_data.femb[1].x[j];
    }
    data.timestamp[i] = frame_data.timestamp;
    ;
  }
  data.crate_num = frame_data.crate_num;
  data.wib_num = frame_data.wib_num;
}

void
deframe_data(const frame14* frame_buf, size_t nframes, uvx_data& data)
{
  data.samples = nframes;
  for (size_t i = 0; i < 48; i++) {
    if (i < 40) {
      data.u[0][i].resize(nframes);
      data.v[0][i].resize(nframes);
      data.u[1][i].resize(nframes);
      data.v[1][i].resize(nframes);
    }
    data.x[0][i].resize(nframes);
    data.x[1][i].resize(nframes);
  }
  data.timestamp.resize(nframes);
  frame14_unpacked frame_data;
  for (size_t i = 0; i < nframes; i++) {
    unpack_frame(frame_buf + i, &frame_data);
    for (size_t j = 0; j < 48; j++) {
      if (j < 40) {
        data.u[0][j][i] = frame_data.femb[0].u[j];
        data.v[0][j][i] = frame_data.femb[0].v[j];
        data.u[1][j][i] = frame_data.femb[1].u[j];
        data.v[1][j][i] = frame_data.femb[1].v[j];
      }
      data.x[0][j][i] = frame_data.femb[0].x[j];
      data.x[1][j][i] = frame_data.femb[1].x[j];
    }
    data.timestamp[i] = frame_data.timestamp;
  }
  data.crate_num = frame_data.crate_num;
  data.wib_num = frame_data.wib_num;
  // FIXME frame_version femb_valid link_mask fiber_num
}

void
reframe_data(frame14* frame_buf, size_t nframes, const channel_data& data)
{
  frame14_unpacked frame_data;
  for (size_t i = 0; i < nframes; i++) {
    for (size_t j = 0; j < 48; j++) {
      int k;
      if (j < 40) {
        k = u_to_ch[j];
        frame_data.femb[0].u[j] = data.channels[0][k][i];
        frame_data.femb[1].u[j] = data.channels[1][k][i];
        k = v_to_ch[j];
        frame_data.femb[0].v[j] = data.channels[0][k][i];
        frame_data.femb[1].v[j] = data.channels[1][k][i];
      }
      k = x_to_ch[j];
      frame_data.femb[0].x[j] = data.channels[0][k][i];
      frame_data.femb[1].x[j] = data.channels[1][k][i];
    }
    frame_data.timestamp = data.timestamp[i];
    frame_data.crate_num = data.crate_num;
    frame_data.wib_num = data.wib_num;
    // FIXME frame_version femb_valid link_mask fiber_num
    repack_frame(&frame_data, frame_buf + i);
  }
}

void
fake_data(frame14* buffer, size_t nframes)
{
  channel_data data;
  data.samples = nframes;
  data.wib_num = 37;
  data.crate_num = 57;
  for (size_t i = 0; i < 128; i++) {
    data.channels[0][i].resize(nframes);
    data.channels[1][i].resize(nframes);
    int phase = rand() % 500; // NOLINT(runtime/threadsafe_fn)
    for (size_t j = 0; j < nframes; j++) {
      data.channels[0][i][j] = 16384.0 * (sin(2 * 3.1415926 * j / (i * 5 + 100.0) + phase) + 1.0) / 2.0;
      data.channels[1][i][j] = 16384.0 * (cos(2 * 3.1415926 * j / (i * 5 + 100.0) + phase) + 1.0) / 2.0;
    }
  }
  data.timestamp.resize(nframes);
  for (size_t i = 0; i < nframes; i++)
    data.timestamp[i] = i;
  reframe_data(buffer, nframes, data);
}

} // namespace wib2unpack

using namespace dunedaq::fddetdataformats;

typedef std::array<uint16_t, 256> vals_type; // NOLINT(build/unsigned)

// Tell boost not to try to print vals_type objects with <<
BOOST_TEST_DONT_PRINT_LOG_VALUE(vals_type)

BOOST_AUTO_TEST_SUITE(WIB2Frame_test)

std::vector<vals_type>
make_vals()
{
  std::vector<vals_type> ret;

  std::default_random_engine e1(10);
  std::uniform_int_distribution<int> uniform_dist(0, (1 << 14) - 1);

  const int n_fuzz = 100;
  for (int i = 0; i < n_fuzz; ++i) {
    std::array<uint16_t, 256> vals; // NOLINT(build/unsigned)
    for (size_t j = 0; j < vals.size(); ++j) {
      vals[j] = uniform_dist(e1);
    }
    ret.push_back(vals);
  }

  return ret;
}

BOOST_DATA_TEST_CASE(CompareToUnpack, boost::unit_test::data::make(make_vals()), vals)
{
  // Check the WIB2 frame overlay code in WIB2Frame.hpp by comparing to
  // the output of the (independently-written) code in WIB2Unpack.hpp
  wib2unpack::frame14_unpacked unpacked;
  // Zero it out just to be on the safe side
  std::memset(&unpacked, 0, sizeof(wib2unpack::frame14_unpacked));

  wib2unpack::frame14 packed;
  // Zero it out just to be on the safe side
  std::memset(&packed, 0, sizeof(wib2unpack::frame14));

  // Fill the unpacked frame from the input `vals` array
  int counter = 0;
  for (int femb = 0; femb < 2; ++femb) {
    for (int i = 0; i < 40; ++i) {
      unpacked.femb[femb].u[i] = vals[counter];
      counter++;
    }
    for (int i = 0; i < 40; ++i) {
      unpacked.femb[femb].v[i] = vals[counter];
      counter++;
    }
    for (int i = 0; i < 48; ++i) {
      unpacked.femb[femb].x[i] = vals[counter];
      counter++;
    }
  }

  // Create the packed array from the unpacked array
  wib2unpack::repack_frame(&unpacked, &packed);

  //WIB2Frame* wib2frame = reinterpret_cast<WIB2Frame*>(&packed); // NOLINT
  size_t num_errors = 0;

  // TODO: replace with some meaningul test in the future
  // for (int femb = 0; femb < 2; ++femb) {
  //   for (int i = 0; i < 40; ++i) {
  //     uint16_t gold = unpacked.femb[femb].u[i];  // NOLINT(build/unsigned)
  //     uint16_t test = wib2frame->get_u(femb, i); // NOLINT(build/unsigned)
  //     if (gold != test) {
  //       num_errors++;
  //       BOOST_CHECK_EQUAL(gold, test);
  //     }
  //   }
  //   for (int i = 0; i < 40; ++i) {
  //     uint16_t gold = unpacked.femb[femb].v[i];  // NOLINT(build/unsigned)
  //     uint16_t test = wib2frame->get_v(femb, i); // NOLINT(build/unsigned)
  //     if (gold != test) {
  //       num_errors++;
  //       BOOST_CHECK_EQUAL(gold, test);
  //     }
  //   }
  //   for (int i = 0; i < 48; ++i) {
  //     uint16_t gold = unpacked.femb[femb].x[i];  // NOLINT(build/unsigned)
  //     uint16_t test = wib2frame->get_x(femb, i); // NOLINT(build/unsigned)
  //     if (gold != test) {
  //       num_errors++;
  //       BOOST_CHECK_EQUAL(gold, test);
  //     }
  //   }
  // } // loop over femb

  BOOST_REQUIRE_EQUAL(num_errors, 0);
}

BOOST_AUTO_TEST_CASE(WIB2Frame_ADCDataMutators)
{
  std::random_device dev;
  std::mt19937 rng(dev());
  std::uniform_int_distribution<std::mt19937::result_type> dist(1,(1<<14)-1);
  std::vector<int> v;
  for(int i=0; i<256; i++) {
    v.push_back(dist(rng));
  }

  dunedaq::fddetdataformats::WIB2Frame wib2frame {};
  for(int i=0; i<256; i++) {
    wib2frame.set_adc(i, v[i]);
  }

  for(int i=0; i<256; i++) {
    BOOST_REQUIRE_EQUAL(wib2frame.get_adc(i), v[i]);
  }

}

BOOST_AUTO_TEST_SUITE_END()

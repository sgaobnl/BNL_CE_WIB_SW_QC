/**
 * This is part of the DUNE DAQ , copyright 2020.
 * Licensing/copyright details are in the COPYING file that you should have
 * received with this code.
 */
#ifndef FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_SSPTYPES_HPP_
#define FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_SSPTYPES_HPP_

#include <cstdlib>

namespace dunedaq::fddetdataformats::ssp {

// Readable names for interface types
enum Comm_t
{
  kUSB,
  kEthernet,
  kEmulated
};

static const constexpr int max_control_data = 256; // Maximum size of packet payload on comms channel

//==============================================================================
// Enumerated Constants
// These are defined by the SSP hardware spec
//==============================================================================

// Command to send to SSP
enum commandConstants
{
  cmdNone = 0,
  // Basic Commands
  cmdRead = 1,
  cmdReadMask = 2,
  cmdWrite = 3,
  cmdWriteMask = 4,
  // Array Commands
  cmdArrayRead = 5,
  cmdArrayWrite = 6,
  // Fifo Commands
  cmdFifoRead = 7,
  cmdFifoWrite = 8,
  numCommands
};

// Holder for status returned from SSP
enum statusConstants
{
  statusNoError = 0,
  statusSendError = 1,
  statusReceiveError = 2,
  statusTimeoutError = 3,
  statusAddressError = 4,
  statusAlignError = 5,
  statusCommandError = 6,
  statusSizeError = 7,
  statusWriteError = 8 // Returned if read-only address is written
};

//==============================================================================
// Types
//==============================================================================

// Header to write out at top of millislice (i.e. this is the artdaq "metadata"
// for a fragment
struct MillisliceHeader
{
  unsigned long startTime;   // NOLINT
  unsigned long endTime;     // NOLINT
  unsigned long triggerTime; // NOLINT
  unsigned int length;       // NOLINT  // Packet Length including header)
  unsigned int nTriggers;    // NOLINT
  unsigned int triggerType;  // NOLINT

  inline static const size_t sizeInUInts = 9;
};

// Structure defined by hardware, i.e. hardware output can be written straight into this struct
struct EventHeader
{                                 // NOTE: Group fields are listed from MSB to LSB
  unsigned int header;            // NOLINT // 0xAAAAAAAA
  unsigned short length;          // NOLINT // Packet Length in unsigned ints (including header)
  unsigned short group1;          // NOLINT // Trigger Type, Status Flags, Header Type
  unsigned short triggerID;       // NOLINT // Trigger ID
  unsigned short group2;          // NOLINT // Module ID, Channel ID
  unsigned short timestamp[4];    // NOLINT // External Timestamp
                                  // Words 0-1 = Clocks since last sync pulse
                                  // Words 2-3 = Sync pulse count
  unsigned short peakSumLow;      // NOLINT // Lower 16 bits of Peak Sum
  unsigned short group3;          // NOLINT // Offset of Peak, Higher 8 bits of Peak Sum
  unsigned short preriseLow;      // NOLINT // Lower 16 bits of Prerise
  unsigned short group4;          // NOLINT // Lower 8 bits of integratedSum, Higher 8 bits of Prerise
  unsigned short intSumHigh;      // NOLINT // Upper 16 bits of integratedSum
  unsigned short baseline;        // NOLINT // Baseline
  unsigned short cfdPoint[4];     // NOLINT // CFD Timestamp Interpolation Points
  unsigned short intTimestamp[4]; // NOLINT // Internal Timestamp
                                  // Word 0 = Reserved for interpolation
                                  // Words 1-3 = 48 bit Timestamp
};
// static_assert(sizeof(struct EventHeader) == 12, "Check your assumptions on SSP EventHeader size");

// byte-level structure of command header to send to SSP
struct CtrlHeader
{
  unsigned int length;
  unsigned int address;
  unsigned int command;
  unsigned int size;
  unsigned int status;
};

// Struct containing header followed by payload.
// Since control packets are small, just allocate enough space to accommodate
// longest possible message
struct CtrlPacket
{
  CtrlHeader header;
  unsigned int data[max_control_data];
};

} // namespace dunedaq::fddetdataformats::ssp

#endif // FDDETDATAFORMATS_INCLUDE_FDDETDATAFORMATS_SSPTYPES_HPP_

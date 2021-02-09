#pragma once
#include <stdint.h>
#define PORT_NROWS 256
#define PORT_NCOLS 512
#define PORT_NROWS_WGAP 257
#define PORT_NCOLS_WGAP 515
#define NPIX_X_CHIP 256


typedef struct {
    uint64_t frameNumber;
    uint32_t expLength;
    uint32_t packetNumber;
    uint64_t bunchId;
    uint64_t timestamp;
    uint16_t modId;
    uint16_t row;
    uint16_t column;
    uint16_t reserved;
    uint32_t debug;
    uint16_t roundRNumber;
    uint8_t detType;
    uint8_t version;
    uint8_t packetmast[64];
} sls_detector_header;
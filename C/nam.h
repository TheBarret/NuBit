#ifndef NAM_H
#define NAM_H

#include <stdint.h>
#include <stdbool.h>


// NAM Constants


#define NAM_ENTRIES         256      // Number of associative entries
#define NAM_PATTERN_BITS    16       // Pattern width (matches CPU)
#define NAM_DATA_BITS       16       // Data width (matches CPU)

// I/O Ports (Memory-mapped)
#define NAM_PORT_BASE       0xFFF4
#define NAM_CTRL            (NAM_PORT_BASE + 0)   // 0xFFF4: Control
#define NAM_ADDR            (NAM_PORT_BASE + 1)   // 0xFFF5: Pattern/Address
#define NAM_DATA            (NAM_PORT_BASE + 2)   // 0xFFF6: Data
#define NAM_STATUS          (NAM_PORT_BASE + 3)   // 0xFFF7: Status

// Control register bits
#define NAM_CTRL_SEARCH     0x01   // 1 = Search for pattern
#define NAM_CTRL_STORE      0x02   // 1 = Store pattern
#define NAM_CTRL_DELETE     0x04   // 1 = Delete pattern
#define NAM_CTRL_CLEAR      0x08   // 1 = Clear all entries
#define NAM_CTRL_HAMMING    0x10   // 1 = Return Hamming distance

// Status register bits
#define NAM_STATUS_READY    0x01   // 1 = Ready for next operation
#define NAM_STATUS_FOUND    0x02   // 1 = Match found
#define NAM_STATUS_BUSY     0x04   // 1 = Operation in progress
#define NAM_STATUS_FULL     0x08   // 1 = Memory is full
#define NAM_STATUS_HIT      0x10   // 1 = Cache hit (if used as cache)


// NAM Entry Structure


typedef struct {
    uint16_t pattern;      // Pattern to match
    uint16_t data;         // Associated data
    uint8_t valid;         // 1 = entry valid
    uint8_t age;           // Age for LRU (if used as cache)
} NAMEntry;


// NAM Core Structure


typedef struct {
    NAMEntry entries[NAM_ENTRIES];
    uint16_t match_index;       // Index of last match
    uint16_t match_pattern;     // Pattern of last match
    uint16_t match_data;        // Data of last match
    uint8_t match_count;        // Number of matches found
    uint16_t hamming_distance;  // Hamming distance of last search

    // Statistics (optional)
    uint32_t hits;
    uint32_t misses;
    uint32_t searches;
    uint32_t stores;
} NAM;


// NAM Functions


void nam_init(NAM* nam);
void nam_reset(NAM* nam);

// Core operations
uint16_t nam_search(NAM* nam, uint16_t pattern);
uint16_t nam_search_hamming(NAM* nam, uint16_t pattern);
int nam_store(NAM* nam, uint16_t pattern, uint16_t data);
int nam_delete(NAM* nam, uint16_t pattern);
void nam_clear(NAM* nam);

// Utility functions
uint16_t nam_get_data(NAM* nam, uint16_t pattern);
uint16_t nam_get_pattern_at(NAM* nam, int index);
uint16_t nam_get_data_at(NAM* nam, int index);
int nam_get_match_count(NAM* nam);
uint16_t nam_get_hamming_distance(NAM* nam);

// Cache mode
uint16_t nam_cache_lookup(NAM* nam, uint16_t address);
void nam_cache_update(NAM* nam, uint16_t address, uint16_t data);

// Statistics
void nam_get_stats(NAM* nam, uint32_t* hits, uint32_t* misses,
                   uint32_t* searches, uint32_t* stores);

// Debug
void nam_dump(NAM* nam);

#endif // NAM_H

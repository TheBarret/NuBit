#include "nam.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


// Internal Helpers


static uint16_t hamming_distance(uint16_t a, uint16_t b) {
    uint16_t xor_result = a ^ b;
    uint16_t dist = 0;
    while (xor_result) {
        dist += xor_result & 1;
        xor_result >>= 1;
    }
    return dist;
}

static int find_empty_entry(NAM* nam) {
    for (int i = 0; i < NAM_ENTRIES; i++) {
        if (!nam->entries[i].valid) {
            return i;
        }
    }
    return -1;
}

static int find_pattern(NAM* nam, uint16_t pattern) {
    for (int i = 0; i < NAM_ENTRIES; i++) {
        if (nam->entries[i].valid && nam->entries[i].pattern == pattern) {
            return i;
        }
    }
    return -1;
}


// Initialization


void nam_init(NAM* nam) {
    memset(nam, 0, sizeof(NAM));
    nam_reset(nam);
}

void nam_reset(NAM* nam) {
    memset(nam->entries, 0, sizeof(nam->entries));
    nam->match_index = 0;
    nam->match_pattern = 0;
    nam->match_data = 0;
    nam->match_count = 0;
    nam->hamming_distance = 0;
    nam->hits = 0;
    nam->misses = 0;
    nam->searches = 0;
    nam->stores = 0;
}


// Core Operations


uint16_t nam_search(NAM* nam, uint16_t pattern) {
    nam->searches++;
    nam->match_count = 0;
    nam->match_index = 0;
    nam->match_pattern = 0;
    nam->match_data = 0;
    nam->hamming_distance = 0;

    // Exact match search
    for (int i = 0; i < NAM_ENTRIES; i++) {
        if (nam->entries[i].valid && nam->entries[i].pattern == pattern) {
            nam->match_count++;
            nam->match_index = i;
            nam->match_pattern = nam->entries[i].pattern;
            nam->match_data = nam->entries[i].data;
            nam->hits++;
            return nam->entries[i].data;
        }
    }

    // Not found
    nam->misses++;
    return 0xFFFF;
}

uint16_t nam_search_hamming(NAM* nam, uint16_t pattern) {
    nam->searches++;
    nam->match_count = 0;
    nam->match_index = 0;
    nam->match_pattern = 0;
    nam->match_data = 0;

    uint16_t best_match = 0xFFFF;
    uint16_t best_distance = 0xFFFF;
    int best_index = -1;

    // Find closest match by Hamming distance
    for (int i = 0; i < NAM_ENTRIES; i++) {
        if (nam->entries[i].valid) {
            uint16_t dist = hamming_distance(pattern, nam->entries[i].pattern);
            if (dist < best_distance) {
                best_distance = dist;
                best_match = nam->entries[i].data;
                best_index = i;
            }
        }
    }

    if (best_index >= 0) {
        nam->match_count = 1;
        nam->match_index = best_index;
        nam->match_pattern = nam->entries[best_index].pattern;
        nam->match_data = nam->entries[best_index].data;
        nam->hamming_distance = best_distance;
        nam->hits++;
        return best_match;
    }

    // No valid entries
    nam->misses++;
    return 0xFFFF;
}

int nam_store(NAM* nam, uint16_t pattern, uint16_t data) {
    nam->stores++;

    // Check if pattern already exists (update)
    int index = find_pattern(nam, pattern);
    if (index >= 0) {
        nam->entries[index].data = data;
        nam->entries[index].age = 0;
        return index;
    }

    // Find empty slot
    index = find_empty_entry(nam);
    if (index < 0) {
        // All entries full - could implement LRU, but for now fail
        return -1;
    }

    // Store new pattern
    nam->entries[index].pattern = pattern;
    nam->entries[index].data = data;
    nam->entries[index].valid = 1;
    nam->entries[index].age = 0;

    return index;
}

int nam_delete(NAM* nam, uint16_t pattern) {
    int index = find_pattern(nam, pattern);
    if (index < 0) {
        return -1;
    }

    nam->entries[index].valid = 0;
    nam->entries[index].pattern = 0;
    nam->entries[index].data = 0;
    return 0;
}

void nam_clear(NAM* nam) {
    nam_reset(nam);
}


// Utility Functions


uint16_t nam_get_data(NAM* nam, uint16_t pattern) {
    int index = find_pattern(nam, pattern);
    if (index >= 0) {
        return nam->entries[index].data;
    }
    return 0xFFFF;
}

uint16_t nam_get_pattern_at(NAM* nam, int index) {
    if (index >= 0 && index < NAM_ENTRIES && nam->entries[index].valid) {
        return nam->entries[index].pattern;
    }
    return 0xFFFF;
}

uint16_t nam_get_data_at(NAM* nam, int index) {
    if (index >= 0 && index < NAM_ENTRIES && nam->entries[index].valid) {
        return nam->entries[index].data;
    }
    return 0xFFFF;
}

int nam_get_match_count(NAM* nam) {
    return nam->match_count;
}

uint16_t nam_get_hamming_distance(NAM* nam) {
    return nam->hamming_distance;
}


// Cache Mode (Cache-like associative memory)


uint16_t nam_cache_lookup(NAM* nam, uint16_t address) {
    // Search for exact match
    uint16_t result = nam_search(nam, address);

    // If found, update age (LRU)
    if (result != 0xFFFF) {
        nam->entries[nam->match_index].age = 0;
        // Increment age of all other entries
        for (int i = 0; i < NAM_ENTRIES; i++) {
            if (nam->entries[i].valid && i != nam->match_index) {
                nam->entries[i].age++;
            }
        }
        return result;
    }

    return 0xFFFF;
}

void nam_cache_update(NAM* nam, uint16_t address, uint16_t data) {
    // Try to store (will update if exists, or add new)
    int index = nam_store(nam, address, data);

    // If store failed (full), evict oldest entry
    if (index < 0) {
        // Find oldest entry (highest age)
        int oldest = 0;
        uint8_t max_age = 0;
        for (int i = 0; i < NAM_ENTRIES; i++) {
            if (nam->entries[i].valid && nam->entries[i].age > max_age) {
                max_age = nam->entries[i].age;
                oldest = i;
            }
        }

        // Overwrite oldest
        nam->entries[oldest].pattern = address;
        nam->entries[oldest].data = data;
        nam->entries[oldest].valid = 1;
        nam->entries[oldest].age = 0;
    }
}


// Statistics


void nam_get_stats(NAM* nam, uint32_t* hits, uint32_t* misses,
                   uint32_t* searches, uint32_t* stores) {
    if (hits) *hits = nam->hits;
    if (misses) *misses = nam->misses;
    if (searches) *searches = nam->searches;
    if (stores) *stores = nam->stores;
}


// Debug


void nam_dump(NAM* nam) {
    printf("=== NAM Dump ===\n");
    printf("Entries: %d/%d valid\n", nam->match_count, NAM_ENTRIES);
    printf("Hits: %d, Misses: %d\n", nam->hits, nam->misses);
    printf("Searches: %d, Stores: %d\n", nam->searches, nam->stores);

    if (nam->match_count > 0) {
        printf("Last match: index=%d, pattern=0x%04X, data=0x%04X\n",
               nam->match_index, nam->match_pattern, nam->match_data);
        printf("Hamming distance: %d\n", nam->hamming_distance);
    }

    printf("\nEntries:\n");
    printf("Idx  Pattern  Data   Age  Valid\n");
    printf("----  -------  ------- ---  -----\n");
    for (int i = 0; i < NAM_ENTRIES; i++) {
        if (nam->entries[i].valid) {
            printf("%3d  0x%04X  0x%04X   %2d    %s\n",
                   i,
                   nam->entries[i].pattern,
                   nam->entries[i].data,
                   nam->entries[i].age,
                   "YES");
        }
    }
}

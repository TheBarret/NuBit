#ifndef NEURISTOR_H
#define NEURISTOR_H

#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/*
 neuristor.h
 version: 0.2
 Fixes:
 - Address packing collision
 - Disabled w_feedback feature (unstable)
 - Peek function safety
 - 3D address scaling (depth<<48 | row<<32 | col)

 */

typedef enum {
    NEURISTOR_NEGATIVE = -1,
    NEURISTOR_NEUTRAL  =  0,
    NEURISTOR_POSITIVE =  1
} NeuristorState;

typedef enum {
    NEURISTOR_UNSELECTED = 0,
    NEURISTOR_SELECTED   = 1
} NeuristorSelection;

typedef struct {
    NeuristorSelection status;
    NeuristorState state;
} NeuristorReadResult;

typedef struct {
    // Selection weights (pure coincident detection)
    float w_row;
    float w_col;
    float w_depth;
    float bias;

    // The 3-state core
    NeuristorState state;

    // 64-bit address to avoid packing collisions
    uint64_t address;

    // Metadata (diagnostic only)
    uint32_t row_idx;
    uint32_t col_idx;
    uint32_t depth_idx;
    uint64_t access_count;
    uint64_t last_access_time;

    // UNTESTED: Future hysteretic mode
    // When non-zero, selection becomes content-dependent.
    // Experimental purpose
    // Default: 0.0
    float w_feedback_reserved;
} Neuristor;

// --- Initialization ---
void neuristor_init(Neuristor* n, uint32_t row, uint32_t col);
void neuristor_init_3d(Neuristor* n, uint32_t row, uint32_t col, uint32_t depth);
void neuristor_init_custom(Neuristor* n,
                           float w_row, float w_col,
                           float w_depth,
                           float bias);

// --- Core Operations ---
NeuristorSelection neuristor_activate(const Neuristor* n,
                                       int row_signal,
                                       int col_signal,
                                       int depth_signal);

NeuristorReadResult neuristor_read(Neuristor* n,
                                    int row_signal,
                                    int col_signal,
                                    int depth_signal);

void neuristor_write(Neuristor* n,
                     int row_signal,
                     int col_signal,
                     int depth_signal,
                     NeuristorState new_state);

void neuristor_refresh(Neuristor* n,
                       int row_signal,
                       int col_signal,
                       int depth_signal,
                       NeuristorState saved_state);

// --- Debug/Diagnostic (Non-destructive) ---
static inline NeuristorState neuristor_peek(const Neuristor* n) {
    return n->state;  // Safe: no side effects
}

static inline uint64_t neuristor_get_address(const Neuristor* n) {
    return n->address;
}

// --- Convenience ---
void neuristor_erase(Neuristor* n,
                     int row_signal,
                     int col_signal,
                     int depth_signal);

void neuristor_reset_stats(Neuristor* n);
const char* neuristor_state_to_string(NeuristorState state);

static inline int neuristor_state_to_binary(NeuristorState state) {
    return (state == NEURISTOR_POSITIVE) ? 1 : 0;
}

static inline NeuristorState neuristor_binary_to_state(int bit) {
    assert(bit == 0 || bit == 1);
    return (bit == 1) ? NEURISTOR_POSITIVE : NEURISTOR_NEGATIVE;
}

#endif // NEURISTOR_H

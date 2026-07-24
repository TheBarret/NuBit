#include "neuristor.h"
#include <stdio.h>
#include <string.h>
#include <time.h>


/*
 neuristor.c
 version: 0.2
 */

// --- Constants ---
static const float DEFAULT_BIAS = -1.5f;
static const float SELECTION_THRESHOLD = 0.0f;

// --- Initialization ---

void neuristor_init(Neuristor* n, uint32_t row, uint32_t col) {
    assert(n != NULL);

    n->w_row = 1.0f;
    n->w_col = 1.0f;
    n->w_depth = 0.0f;
    n->bias = DEFAULT_BIAS;
    n->w_feedback_reserved = 0.0f;  // Reserved, not used

    n->state = NEURISTOR_NEUTRAL;
    n->address = ((uint64_t)row << 32) | col;  // 64-bit, no collision
    n->row_idx = row;
    n->col_idx = col;
    n->depth_idx = 0;
    n->access_count = 0;
    n->last_access_time = 0;
}

void neuristor_init_3d(Neuristor* n, uint32_t row, uint32_t col, uint32_t depth) {
    assert(n != NULL);

    neuristor_init(n, row, col);
    n->w_depth = 1.0f;
    n->depth_idx = depth;
    n->address = ((uint64_t)depth << 48) | ((uint64_t)row << 32) | col;
}

void neuristor_init_custom(Neuristor* n,
                           float w_row, float w_col,
                           float w_depth,
                           float bias) {
    assert(n != NULL);

    n->w_row = w_row;
    n->w_col = w_col;
    n->w_depth = w_depth;
    n->bias = bias;
    n->w_feedback_reserved = 0.0f;  // Always zero for now

    n->state = NEURISTOR_NEUTRAL;
    n->address = 0;
    n->row_idx = 0;
    n->col_idx = 0;
    n->depth_idx = 0;
    n->access_count = 0;
    n->last_access_time = 0;
}

// --- Core Operations ---

NeuristorSelection neuristor_activate(const Neuristor* n,
                                       int row_signal,
                                       int col_signal,
                                       int depth_signal) {
    assert(n != NULL);
    assert(row_signal == 0 || row_signal == 1);
    assert(col_signal == 0 || col_signal == 1);
    assert(depth_signal == 0 || depth_signal == 1);

    // Pure coincident selection - NO feedback
    float linear = (n->w_row * (float)row_signal) +
                   (n->w_col * (float)col_signal) +
                   (n->w_depth * (float)depth_signal) +
                   n->bias;

    return (linear > SELECTION_THRESHOLD) ? NEURISTOR_SELECTED : NEURISTOR_UNSELECTED;
}

NeuristorReadResult neuristor_read(Neuristor* n,
                                    int row_signal,
                                    int col_signal,
                                    int depth_signal) {
    assert(n != NULL);

    NeuristorReadResult result = {
        .status = NEURISTOR_UNSELECTED,
        .state = NEURISTOR_NEUTRAL
    };

    if (neuristor_activate(n, row_signal, col_signal, depth_signal) == NEURISTOR_SELECTED) {
        result.status = NEURISTOR_SELECTED;
        result.state = n->state;
        n->state = NEURISTOR_NEUTRAL;  // Destructive read

        n->access_count++;
        n->last_access_time = clock();
    }

    return result;
}

void neuristor_write(Neuristor* n,
                     int row_signal,
                     int col_signal,
                     int depth_signal,
                     NeuristorState new_state) {
    assert(n != NULL);
    assert(new_state >= NEURISTOR_NEGATIVE && new_state <= NEURISTOR_POSITIVE);

    if (neuristor_activate(n, row_signal, col_signal, depth_signal) == NEURISTOR_SELECTED) {
        n->state = new_state;
        n->access_count++;
        n->last_access_time = clock();
    }
}

void neuristor_refresh(Neuristor* n,
                       int row_signal,
                       int col_signal,
                       int depth_signal,
                       NeuristorState saved_state) {
    assert(n != NULL);
    assert(saved_state >= NEURISTOR_NEGATIVE && saved_state <= NEURISTOR_POSITIVE);

    if (neuristor_activate(n, row_signal, col_signal, depth_signal) == NEURISTOR_SELECTED) {
        n->state = saved_state;
        n->access_count++;
        n->last_access_time = clock();
    }
}

// --- Convenience ---

void neuristor_erase(Neuristor* n,
                     int row_signal,
                     int col_signal,
                     int depth_signal) {
    neuristor_write(n, row_signal, col_signal, depth_signal, NEURISTOR_NEUTRAL);
}

void neuristor_reset_stats(Neuristor* n) {
    assert(n != NULL);
    n->access_count = 0;
    n->last_access_time = 0;
}

// --- State Conversion ---

const char* neuristor_state_to_string(NeuristorState state) {
    switch (state) {
        case NEURISTOR_NEGATIVE: return "-";
        case NEURISTOR_NEUTRAL:  return "0";
        case NEURISTOR_POSITIVE: return "+";
        default: return "?";
    }
}

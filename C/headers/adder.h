#ifndef ADDER_H
#define ADDER_H

#include <stdint.h>
#include "gates.h"

/* Todo:
 Eliminate Runtime Allocations (Zero Heap Churn)
 Move the temporary buffers inside Adder struct so allocation happens only once during adder_init().
 typedef struct {
     ...
     int* original_P; // Pre-allocated in adder_init
 } Adder;

 */
typedef struct {
    int bits;
    Gate and_gate;
    Gate or_gate;
    XorGate xor_gate;

    int* A_bits;
    int* B_bits;
    int* G;
    int* P;
    int* G_temp;
    int* P_temp;
    int* carries;
    int* S;
    uint64_t mask;
} Adder;

void adder_init(Adder* adder, int bits);
void adder_free(Adder* adder);
int adder_forward(Adder* adder, uint64_t A, uint64_t B, int cin, uint64_t* result);

// debugger utilities
void adder_debug(Adder* adder, const char* label);

#endif // ADDER_H

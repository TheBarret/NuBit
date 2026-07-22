#ifndef GATES_H
#define GATES_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float w1;
    float w2;
    float bias;
} Gate;

typedef struct {
    float w1;
    float bias;
} NotGate;

typedef struct {
    Gate or_gate;
    Gate nand_gate;
    Gate and_gate;
    int* temp1;      // Pre-allocated buffers
    int* temp2;
    int max_n;       // For bounds checking
} XorGate;

// --- Base Gate ---
void gate_init(Gate* g, float w1, float w2, float bias);
void and_gate_init(Gate* g);
void or_gate_init(Gate* g);
void nand_gate_init(Gate* g);
void nor_gate_init(Gate* g);

void gate_forward(const Gate* g, const int* x1, const int* x2, int n, int* out);
int gate_forward_single(const Gate* g, int x1, int x2);

// --- Not Gate ---
void not_gate_init(NotGate* g);
void not_gate_forward(const NotGate* g, const int* x, int n, int* out);
int not_gate_forward_single(const NotGate* g, int x);

// --- Xor Gate ---
void xor_gate_init(XorGate* g, int max_n);
void xor_gate_free(XorGate* g);
void xor_gate_forward(XorGate* g, const int* x1, const int* x2, int n, int* out);
int xor_gate_forward_single(XorGate* g, int x1, int x2);

#endif // GATES_H

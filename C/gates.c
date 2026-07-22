#include "gates.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

// --- Base Gate ---
void gate_init(Gate* g, float w1, float w2, float bias) {
    g->w1 = w1;
    g->w2 = w2;
    g->bias = bias;
}

void and_gate_init(Gate* g)  { gate_init(g, 1.0f, 1.0f, -1.5f); }
void or_gate_init(Gate* g)   { gate_init(g, 1.0f, 1.0f, -0.5f); }
void nand_gate_init(Gate* g) { gate_init(g, -1.0f, -1.0f, 1.5f); }
void nor_gate_init(Gate* g)  { gate_init(g, -1.0f, -1.0f, 0.5f); }

void gate_forward(const Gate* g, const int* x1, const int* x2, int n, int* out) {
    for (int i = 0; i < n; i++) {
        float linear = (g->w1 * (float)x1[i]) + (g->w2 * (float)x2[i]) + g->bias;
        out[i] = (linear > 0.0f) ? 1 : 0;
    }
}

int gate_forward_single(const Gate* g, int x1, int x2) {
    float linear = (g->w1 * (float)x1) + (g->w2 * (float)x2) + g->bias;
    return (linear > 0.0f) ? 1 : 0;
}

// --- Not Gate ---
void not_gate_init(NotGate* g) {
    g->w1 = -1.0f;
    g->bias = 0.5f;
}

void not_gate_forward(const NotGate* g, const int* x, int n, int* out) {
    for (int i = 0; i < n; i++) {
        float linear = (g->w1 * (float)x[i]) + g->bias;
        out[i] = (linear > 0.0f) ? 1 : 0;
    }
}

int not_gate_forward_single(const NotGate* g, int x) {
    float linear = (g->w1 * (float)x) + g->bias;
    return (linear > 0.0f) ? 1 : 0;
}

// --- Xor Gate ---
void xor_gate_init(XorGate* g, int max_n) {
    and_gate_init(&g->and_gate);
    or_gate_init(&g->or_gate);
    nand_gate_init(&g->nand_gate);
    g->max_n = max_n;
    g->temp1 = (int*)calloc(max_n, sizeof(int));
    g->temp2 = (int*)calloc(max_n, sizeof(int));
    assert(g->temp1 != NULL && g->temp2 != NULL);
}

void xor_gate_free(XorGate* g) {
    free(g->temp1);
    free(g->temp2);
}

void xor_gate_forward(XorGate* g, const int* x1, const int* x2, int n, int* out) {
    assert(n <= g->max_n);
    gate_forward(&g->or_gate, x1, x2, n, g->temp1);
    gate_forward(&g->nand_gate, x1, x2, n, g->temp2);
    gate_forward(&g->and_gate, g->temp1, g->temp2, n, out);
}

int xor_gate_forward_single(XorGate* g, int x1, int x2) {
    int or_out = gate_forward_single(&g->or_gate, x1, x2);
    int nand_out = gate_forward_single(&g->nand_gate, x1, x2);
    return gate_forward_single(&g->and_gate, or_out, nand_out);
}

#include "gates.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

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

// version 1.0
// void xor_gate_forward(XorGate* g, const int* x1, const int* x2, int n, int* out) {
//    assert(n <= g->max_n);
//    gate_forward(&g->or_gate, x1, x2, n, g->temp1);
//    gate_forward(&g->nand_gate, x1, x2, n, g->temp2);
//    gate_forward(&g->and_gate, g->temp1, g->temp2, n, out);
// }

// version 2.0 - stack-allocated arrays
void xor_gate_forward(XorGate* g, const int* x1, const int* x2, int n, int* out) {
    assert(n <= g->max_n);

    // Use stack-allocated temp arrays
    // This avoids any issues with the pre-allocated buffers
    int temp1[64];
    int temp2[64];

    if (n > 64) {
        // Fallback to heap allocation for very large n
        int* t1 = (int*)malloc(n * sizeof(int));
        int* t2 = (int*)malloc(n * sizeof(int));
        if (!t1 || !t2) {
            free(t1);
            free(t2);
            return;
        }
        gate_forward(&g->or_gate, x1, x2, n, t1);
        gate_forward(&g->nand_gate, x1, x2, n, t2);
        gate_forward(&g->and_gate, t1, t2, n, out);
        free(t1);
        free(t2);
    } else {
        gate_forward(&g->or_gate, x1, x2, n, temp1);
        gate_forward(&g->nand_gate, x1, x2, n, temp2);
        gate_forward(&g->and_gate, temp1, temp2, n, out);
    }
}

// debug-helper version
/* void xor_gate_forward(XorGate* g, const int* x1, const int* x2, int n, int* out) {
    assert(n <= g->max_n);

    printf("\n=== XOR GATE DEBUG ===\n");
    printf("n=%d, max_n=%d\n", n, g->max_n);

    // Print input bits
    printf("x1: ");
    for (int i = n-1; i >= 0; i--) printf("%d", x1[i]);
    printf("\n");
    printf("x2: ");
    for (int i = n-1; i >= 0; i--) printf("%d", x2[i]);
    printf("\n");

    // Print gate weights
    printf("OR gate: w1=%.1f, w2=%.1f, bias=%.1f\n",
           g->or_gate.w1, g->or_gate.w2, g->or_gate.bias);
    printf("NAND gate: w1=%.1f, w2=%.1f, bias=%.1f\n",
           g->nand_gate.w1, g->nand_gate.w2, g->nand_gate.bias);
    printf("AND gate: w1=%.1f, w2=%.1f, bias=%.1f\n",
           g->and_gate.w1, g->and_gate.w2, g->and_gate.bias);

    int temp1[64];
    int temp2[64];

    gate_forward(&g->or_gate, x1, x2, n, temp1);
    printf("OR output: ");
    for (int i = n-1; i >= 0; i--) printf("%d", temp1[i]);
    printf("\n");

    gate_forward(&g->nand_gate, x1, x2, n, temp2);
    printf("NAND output: ");
    for (int i = n-1; i >= 0; i--) printf("%d", temp2[i]);
    printf("\n");

    gate_forward(&g->and_gate, temp1, temp2, n, out);
    printf("AND output (XOR): ");
    for (int i = n-1; i >= 0; i--) printf("%d", out[i]);
    printf("\n");
    } */

int xor_gate_forward_single(XorGate* g, int x1, int x2) {
    int or_out = gate_forward_single(&g->or_gate, x1, x2);
    int nand_out = gate_forward_single(&g->nand_gate, x1, x2);
    return gate_forward_single(&g->and_gate, or_out, nand_out);
}

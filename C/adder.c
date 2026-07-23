#include "adder.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

void adder_init(Adder* adder, int bits) {
    assert(bits > 0 && bits <= 64);
    adder->bits = bits;

    // DESIGN SHIFT: Handle 64-bit shift edge case. (1ULL << 64) is undefined in C.
    adder->mask = (bits == 64) ? ~0ULL : ((1ULL << bits) - 1);

    and_gate_init(&adder->and_gate);
    or_gate_init(&adder->or_gate);
    xor_gate_init(&adder->xor_gate, bits); // Pass max_n for temp buffer allocation

    adder->A_bits  = (int*)calloc(bits, sizeof(int));
    adder->B_bits  = (int*)calloc(bits, sizeof(int));
    adder->G       = (int*)calloc(bits, sizeof(int));
    adder->P       = (int*)calloc(bits, sizeof(int));
    adder->G_temp  = (int*)calloc(bits, sizeof(int));
    adder->P_temp  = (int*)calloc(bits, sizeof(int));
    adder->carries = (int*)calloc(bits + 1, sizeof(int));
    adder->S       = (int*)calloc(bits, sizeof(int));
}

void adder_free(Adder* adder) {
    xor_gate_free(&adder->xor_gate);
    free(adder->A_bits);
    free(adder->B_bits);
    free(adder->G);
    free(adder->P);
    free(adder->G_temp);
    free(adder->P_temp);
    free(adder->carries);
    free(adder->S);
}

static inline void int_to_bits(uint64_t val, int bits, int* out) {
    for (int i = 0; i < bits; i++) {
        out[i] = (val >> i) & 1;
    }
}

static inline void compute_generate_propagate(Adder* adder) {
    gate_forward(&adder->and_gate, adder->A_bits, adder->B_bits, adder->bits, adder->G);
    xor_gate_forward(&adder->xor_gate, adder->A_bits, adder->B_bits, adder->bits, adder->P);
}

static void compute_carries_kogge_stone(Adder* adder, int cin) {
    int N = adder->bits;

    // Save original P before Kogge-Stone modifies it
    int* original_P = (int*)malloc(N * sizeof(int));
    memcpy(original_P, adder->P, N * sizeof(int));

    int* G_curr = adder->G;
    int* P_curr = adder->P;
    int* G_next = adder->G_temp;
    int* P_next = adder->P_temp;
    int* carries = adder->carries;

    // Inject carry-in
    G_curr[0] = G_curr[0] | (P_curr[0] & cin);

    int stride = 1;
    while (stride < N) {
        // 1. Copy unchanged prefix
        for (int i = 0; i < stride; i++) {
            G_next[i] = G_curr[i];
            P_next[i] = P_curr[i];
        }
        // 2. Compute new values using the OLD state (G_curr, P_curr)
        for (int i = stride; i < N; i++) {
            G_next[i] = G_curr[i] | (P_curr[i] & G_curr[i - stride]);
            P_next[i] = P_curr[i] & P_curr[i - stride];
        }

        // DESIGN SHIFT: Pointer swapping (O(1)) instead of memcpy (O(N)).
        int* temp_G = G_curr; G_curr = G_next; G_next = temp_G;
        int* temp_P = P_curr; P_curr = P_next; P_next = temp_P;

        stride <<= 1;
    }

    // Ensure final results are in the primary adder->G and adder->P buffers
    if (G_curr != adder->G) {
        memcpy(adder->G, G_curr, N * sizeof(int));
        memcpy(adder->P, P_curr, N * sizeof(int));
    }

    // Restore original P for sum computation (P XOR carries)
    memcpy(adder->P, original_P, N * sizeof(int));
    free(original_P);

    // Construct carries array
    carries[0] = cin;
    for (int i = 0; i < N; i++) {
        carries[i + 1] = adder->G[i];
    }
}

int adder_forward(Adder* adder, uint64_t A, uint64_t B, int cin, uint64_t* result) {
    // Mask inputs to bit width
    int_to_bits(A & adder->mask, adder->bits, adder->A_bits);
    int_to_bits(B & adder->mask, adder->bits, adder->B_bits);

    compute_generate_propagate(adder);
    compute_carries_kogge_stone(adder, cin);

    // Sum = P ^ C (where C = carries[0..N-1])
    // DESIGN SHIFT: Passing adder->carries with size 'bits' perfectly
    // mimics Python's carries[:-1] slice.
    xor_gate_forward(&adder->xor_gate, adder->P, adder->carries, adder->bits, adder->S);

    // Reconstruct integer result
    uint64_t res = 0;
    for (int i = 0; i < adder->bits; i++) {
        res |= ((uint64_t)adder->S[i]) << i;
    }

    *result = res & adder->mask;
    return adder->carries[adder->bits];
}

// debugger
void adder_debug(Adder* adder, const char* label) {
    printf("\n=== ADDER DEBUG: %s ===\n", label);
    printf("bits: %d\n", adder->bits);

    printf("A_bits: ");
    for (int i = adder->bits - 1; i >= 0; i--) printf("%d", adder->A_bits[i]);
    printf("\n");

    printf("B_bits: ");
    for (int i = adder->bits - 1; i >= 0; i--) printf("%d", adder->B_bits[i]);
    printf("\n");

    printf("G (generate): ");
    for (int i = adder->bits - 1; i >= 0; i--) printf("%d", adder->G[i]);
    printf("\n");

    printf("P (propagate): ");
    for (int i = adder->bits - 1; i >= 0; i--) printf("%d", adder->P[i]);
    printf("\n");

    printf("carries: ");
    for (int i = adder->bits; i >= 0; i--) printf("%d", adder->carries[i]);
    printf("\n");

    printf("S (sum): ");
    for (int i = adder->bits - 1; i >= 0; i--) printf("%d", adder->S[i]);
    printf("\n");

    // Reconstruct result for verification
    uint64_t res = 0;
    for (int i = 0; i < adder->bits; i++) {
        res |= ((uint64_t)adder->S[i]) << i;
    }
    printf("Reconstructed result: %" PRIu64 " (0x%04" PRIX64 ")\n", res, res);
    printf("carry out: %d\n", adder->carries[adder->bits]);
}

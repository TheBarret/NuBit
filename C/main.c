#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>
#include "gates.h"
#include "adder.h"
#include "alu.h"

// Performance benchmark function
void benchmark_alu() {
    printf("PERFORMANCE BENCHMARK\n");

    ALU16 alu;
    alu_init(&alu, 16);

    const int ITERATIONS = 1000000;  // 1 million operations
    uint64_t result = 0;

    printf("\nRunning %d ADD operations...\n", ITERATIONS);

    clock_t start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        result = alu_forward(&alu, i & 0xFFFF, (i * 2) & 0xFFFF, OP_ADD);
    }
    clock_t end = clock();

    double elapsed_ms = (double)(end - start) / CLOCKS_PER_SEC * 1000.0;
    double ops_per_sec = (double)ITERATIONS / (elapsed_ms / 1000.0);

    printf("\n  Time: %.2f ms\n", elapsed_ms);
    printf("  Operations: %d\n", ITERATIONS);
    printf("  Speed: %.0f ops/sec\n", ops_per_sec);
    printf("  Time per op: %.3f µs\n", (elapsed_ms * 1000.0) / ITERATIONS);

    // Also test SUB, MUL, and CMP
    printf("\n");

    // SUB benchmark
    start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        result = alu_forward(&alu, (i * 3) & 0xFFFF, (i * 2) & 0xFFFF, OP_SUB);
    }
    end = clock();
    elapsed_ms = (double)(end - start) / CLOCKS_PER_SEC * 1000.0;
    ops_per_sec = (double)ITERATIONS / (elapsed_ms / 1000.0);
    printf("  SUB: %.0f ops/sec\n", ops_per_sec);

    // MUL benchmark
    start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        result = alu_forward(&alu, i & 0xFF, i & 0xFF, OP_MUL);
    }
    end = clock();
    elapsed_ms = (double)(end - start) / CLOCKS_PER_SEC * 1000.0;
    ops_per_sec = (double)ITERATIONS / (elapsed_ms / 1000.0);
    printf("  MUL: %.0f ops/sec\n", ops_per_sec);

    // CMP benchmark
    start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        result = alu_forward(&alu, i & 0xFFFF, (i * 2) & 0xFFFF, OP_CMP);
    }
    end = clock();
    elapsed_ms = (double)(end - start) / CLOCKS_PER_SEC * 1000.0;
    ops_per_sec = (double)ITERATIONS / (elapsed_ms / 1000.0);
    printf("  CMP: %.0f ops/sec\n", ops_per_sec);

    alu_free(&alu);

    printf("\n============================================================\n");
    printf("C ALU Performance Summary:\n");
    printf("  Average: ~%.0f ops/sec\n",
           (double)(ITERATIONS * 4) /
           (((double)(end - start) / CLOCKS_PER_SEC * 1000.0) / 1000.0));
    printf("============================================================\n");
}

int main() {
    printf("Initializing NuBit ALU16...\n");
    printf("============================================================\n");

    // Run functional tests
    ALU16 alu;
    alu_init(&alu, 16);

    printf("\nFunctional Tests:\n");
    printf("============================================================\n");

    uint64_t result = alu_forward(&alu, 5, 3, OP_ADD);
    printf("5 + 3 = %" PRIu64 " (Z=%d, C=%d)\n",
           result, alu.flags.zero, alu.flags.carry);

    result = alu_forward(&alu, 10, 4, OP_SUB);
    printf("10 - 4 = %" PRIu64 " (Z=%d, C=%d)\n",
           result, alu.flags.zero, alu.flags.carry);

    result = alu_forward(&alu, 0x00FF, 0x0F0F, OP_AND);
    printf("0x00FF & 0x0F0F = 0x%04" PRIX64 "\n", result);

    result = alu_forward(&alu, 0x00FF, 0x0F00, OP_OR);
    printf("0x00FF | 0x0F00 = 0x%04" PRIX64 "\n", result);

    result = alu_forward(&alu, 0x00FF, 0x0F0F, OP_XOR);
    printf("0x00FF ^ 0x0F0F = 0x%04" PRIX64 "\n", result);

    result = alu_forward(&alu, 0x0010, 0x0010, OP_MUL);
    printf("16 * 16 = %" PRIu64 " (OV=%d)\n",
           result, alu.flags.overflow);

    result = alu_forward(&alu, 0x0100, 0x0100, OP_MUL);
    printf("256 * 256 = %" PRIu64 " (OV=%d)\n",
           result, alu.flags.overflow);

    alu_forward(&alu, 0x1234, 0x5678, OP_CMP);
    printf("0x1234 cmp 0x5678: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    alu_forward(&alu, 0x5678, 0x1234, OP_CMP);
    printf("0x5678 cmp 0x1234: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    alu_forward(&alu, 0x1234, 0x1234, OP_CMP);
    printf("0x1234 cmp 0x1234: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    alu_free(&alu);

    // Run performance benchmark
    benchmark_alu();

    return 0;
}

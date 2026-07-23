#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>
#include "gates.h"
#include "adder.h"
#include "alu.h"

#define ITERATIONS 1000000

typedef struct {
    const char* label;
    double elapsed_ms;
    int iterations;
} BenchResult;

// Runs one op benchmark and returns timing. `result_sink` is written to
// on every iteration so the compiler can't optimize the loop away.
static BenchResult run_bench(ALU16* alu, const char* label, Opcode op,
                              uint16_t (*a_fn)(int), uint16_t (*b_fn)(int),
                              uint64_t* result_sink) {
    clock_t start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        *result_sink = alu_forward(alu, a_fn(i), b_fn(i), op);
    }
    clock_t end = clock();

    BenchResult r;
    r.label = label;
    r.elapsed_ms = (double)(end - start) / CLOCKS_PER_SEC * 1000.0;
    r.iterations = ITERATIONS;
    return r;
}

static void print_bench(const BenchResult* r) {
    double ops_per_sec = (double)r->iterations / (r->elapsed_ms / 1000.0);
    double us_per_op = (r->elapsed_ms * 1000.0) / r->iterations;
    printf("  %-4s %10.0f ops/sec  (%.3f ms total, %.3f µs/op)\n",
           r->label, ops_per_sec, r->elapsed_ms, us_per_op);
}

// --- Operand generators (kept identical to the original per-op patterns) ---
static uint16_t add_a(int i) { return i & 0xFFFF; }
static uint16_t add_b(int i) { return (i * 2) & 0xFFFF; }
static uint16_t sub_a(int i) { return (i * 3) & 0xFFFF; }
static uint16_t sub_b(int i) { return (i * 2) & 0xFFFF; }
static uint16_t mul_a(int i) { return i & 0xFF; }
static uint16_t mul_b(int i) { return i & 0xFF; }
static uint16_t cmp_a(int i) { return i & 0xFFFF; }
static uint16_t cmp_b(int i) { return (i * 2) & 0xFFFF; }

void benchmark_alu(void) {
    printf("PERFORMANCE BENCHMARK\n\n");

    ALU16 alu;
    alu_init(&alu, 16);
    uint64_t sink = 0;

    BenchResult results[4];
    results[0] = run_bench(&alu, "ADD", OP_ADD, add_a, add_b, &sink);
    results[1] = run_bench(&alu, "SUB", OP_SUB, sub_a, sub_b, &sink);
    results[2] = run_bench(&alu, "MUL", OP_MUL, mul_a, mul_b, &sink);
    results[3] = run_bench(&alu, "CMP", OP_CMP, cmp_a, cmp_b, &sink);

    alu_free(&alu);

    printf("Ran %d ops each, %d ops total:\n", ITERATIONS, ITERATIONS * 4);
    for (int i = 0; i < 4; i++) {
        print_bench(&results[i]);
    }

    // Correct weighted average: total ops actually run divided by total
    // wall-clock time actually spent, NOT a plain mean of the four rates
    // above (which would over-weight fast ops) and NOT reusing a single
    // loop's timing for all four (the bug in the previous version).
    double total_ms = 0.0;
    int total_ops = 0;
    for (int i = 0; i < 4; i++) {
        total_ms += results[i].elapsed_ms;
        total_ops += results[i].iterations;
    }
    double avg_ops_per_sec = (double)total_ops / (total_ms / 1000.0);

    printf("\n============================================================\n");
    printf("C ALU Performance Summary:\n");
    printf("  Total time:  %.2f ms\n", total_ms);
    printf("  Total ops:   %d\n", total_ops);
    printf("  Average:     ~%.0f ops/sec (total ops / total time)\n", avg_ops_per_sec);
    printf("============================================================\n");

    (void)sink; // silence unused-after-last-write warning, if any
}

static void run_functional_tests(void) {
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
    printf("16 * 16 = %" PRIu64 " (OV=%d)\n", result, alu.flags.overflow);

    result = alu_forward(&alu, 0x0100, 0x0100, OP_MUL);
    printf("256 * 256 = %" PRIu64 " (OV=%d)\n", result, alu.flags.overflow);

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
}

int main(void) {
    printf("Initializing NuBit ALU16...\n");
    printf("============================================================\n");

    run_functional_tests();
    benchmark_alu();

    return 0;
}

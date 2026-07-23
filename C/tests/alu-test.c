// alu_test.c
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include "alu.h"

void test_add(ALU16* alu) {
    printf("\n=== ADD TESTS ===\n");

    // Basic addition
    struct { uint64_t a, b, expected; int carry_expected; } add_tests[] = {
        {0, 0, 0, 0},
        {1, 1, 2, 0},
        {5, 3, 8, 0},
        {10, 20, 30, 0},
        {0xFFFF, 1, 0, 1},  // Overflow
        {0xFFFE, 2, 0, 1},  // Overflow
        {0xFFFF, 0, 0xFFFF, 0},
        {0x7FFF, 1, 0x8000, 0},  // Max positive
        {0x8000, 1, 0x8001, 0},
        {0xFF00, 0x00FF, 0xFFFF, 0},
        {0x0F0F, 0xF0F0, 0xFFFF, 0},
        {0x5555, 0xAAAA, 0xFFFF, 0},
        {0x3333, 0xCCCC, 0xFFFF, 0},
    };

    int total_tests = sizeof(add_tests) / sizeof(add_tests[0]);
    int passed = 0;

    for (int i = 0; i < total_tests; i++) {
        uint64_t result = alu_forward(alu, add_tests[i].a, add_tests[i].b, OP_ADD);
        uint64_t expected = add_tests[i].expected;
        int carry = alu->flags.carry;
        int expected_carry = add_tests[i].carry_expected;

        if (result == expected && carry == expected_carry) {
            printf("  PASS: %5" PRIu64 " + %5" PRIu64 " = %5" PRIu64 " (carry=%d)\n",
                   add_tests[i].a, add_tests[i].b, result, carry);
            passed++;
        } else {
            printf("  FAIL: %5" PRIu64 " + %5" PRIu64 " = %5" PRIu64 " (expected %5" PRIu64 ", carry=%d expected %d)\n",
                   add_tests[i].a, add_tests[i].b, result, expected, carry, expected_carry);
        }
    }
    printf("  ADD: %d/%d passed\n", passed, total_tests);
}

void test_sub(ALU16* alu) {
    printf("\n=== SUB TESTS ===\n");

    struct { uint64_t a, b, expected; int borrow_expected; } sub_tests[] = {
        {0, 0, 0, 0},
        {5, 3, 2, 0},
        {10, 20, 0xFFF6, 1},  // Borrow (10 - 20 = -10 mod 65536)
        {0xFFFF, 1, 0xFFFE, 0},
        {1, 0xFFFF, 2, 1},    // 1 - (-1) = 2 with borrow
        {0x8000, 1, 0x7FFF, 0},
        {0x7FFF, 0x8000, 0xFFFF, 1},  // Borrow
        {0x5555, 0xAAAA, 0xAAAB, 1},  // Borrow
        {0xAAAA, 0x5555, 0x5555, 0},
        {0xFF00, 0x00FF, 0xFE01, 0},
        {0x1234, 0x1234, 0, 0},
        {0xFFFF, 0xFFFF, 0, 0},
    };

    int total_tests = sizeof(sub_tests) / sizeof(sub_tests[0]);
    int passed = 0;

    for (int i = 0; i < total_tests; i++) {
        uint64_t result = alu_forward(alu, sub_tests[i].a, sub_tests[i].b, OP_SUB);
        uint64_t expected = sub_tests[i].expected;
        int borrow = alu->flags.carry;  // Borrow is stored in carry flag
        int expected_borrow = sub_tests[i].borrow_expected;

        if (result == expected && borrow == expected_borrow) {
            printf("  PASS: %5" PRIu64 " - %5" PRIu64 " = %5" PRIu64 " (borrow=%d)\n",
                   sub_tests[i].a, sub_tests[i].b, result, borrow);
            passed++;
        } else {
            printf("  FAIL: %5" PRIu64 " - %5" PRIu64 " = %5" PRIu64 " (expected %5" PRIu64 ", borrow=%d expected %d)\n",
                   sub_tests[i].a, sub_tests[i].b, result, expected, borrow, expected_borrow);
        }
    }
    printf("  SUB: %d/%d passed\n", passed, total_tests);
}

void test_mul(ALU16* alu) {
    printf("\n=== MUL TESTS ===\n");

    struct { uint64_t a, b, expected; int overflow_expected; } mul_tests[] = {
        {0, 0, 0, 0},
        {1, 1, 1, 0},
        {2, 3, 6, 0},
        {5, 5, 25, 0},
        {10, 20, 200, 0},
        {16, 16, 256, 0},
        {0x00FF, 0x00FF, 0xFE01, 0},      // 255 * 255 = 65025 (no overflow)
        {0x0100, 0x0100, 0, 1},           // 256 * 256 = 65536 (overflow)
        {0xFFFF, 1, 0xFFFF, 0},           // -1 * 1 = -1 (no overflow)
        {0xFFFF, 0xFFFF, 1, 1},           // -1 * -1 = 1 (overflow in 16-bit)
        {0x7FFF, 2, 0xFFFE, 0},           // 32767 * 2 = 65534 (no overflow)
        {0x8000, 2, 0, 1},                // -32768 * 2 = -65536 (overflow)
        {0x1234, 0x5678, 0x0060, 1},      // FIXED: 0x1234*0x5678 = 0x06260060 (overflow)
        {0xAAAA, 0x5555, 0x1C72, 1},      // FIXED: 0xAAAA*0x5555 = 0x38E31C72 (overflow)
    };

    int total_tests = sizeof(mul_tests) / sizeof(mul_tests[0]);
    int passed = 0;

    for (int i = 0; i < total_tests; i++) {
        uint64_t result = alu_forward(alu, mul_tests[i].a, mul_tests[i].b, OP_MUL);
        uint64_t expected = mul_tests[i].expected;
        int overflow = alu->flags.overflow;
        int expected_overflow = mul_tests[i].overflow_expected;

        if (result == expected && overflow == expected_overflow) {
            printf("  PASS: %5" PRIu64 " * %5" PRIu64 " = %5" PRIu64 " (OV=%d)\n",
                   mul_tests[i].a, mul_tests[i].b, result, overflow);
            passed++;
        } else {
            printf("  FAIL: %5" PRIu64 " * %5" PRIu64 " = %5" PRIu64 " (expected %5" PRIu64 ", OV=%d expected %d)\n",
                   mul_tests[i].a, mul_tests[i].b, result, expected, overflow, expected_overflow);
        }
    }
    printf("  MUL: %d/%d passed\n", passed, total_tests);
}

void test_bitwise(ALU16* alu) {
    printf("\n=== BITWISE TESTS ===\n");

    struct { uint64_t a, b, and_expected, or_expected, xor_expected; } bitwise_tests[] = {
        {0x0000, 0x0000, 0x0000, 0x0000, 0x0000},
        {0xFFFF, 0x0000, 0x0000, 0xFFFF, 0xFFFF},
        {0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0x0000},
        {0xF0F0, 0x0F0F, 0x0000, 0xFFFF, 0xFFFF},
        {0xAAAA, 0x5555, 0x0000, 0xFFFF, 0xFFFF},
        {0x1234, 0x5678, 0x1230, 0x567C, 0x444C},
        {0x00FF, 0x0F0F, 0x000F, 0x0FFF, 0x0FF0},
        {0xFF00, 0x00FF, 0x0000, 0xFFFF, 0xFFFF},
        {0xABCD, 0x1234, 0x0204, 0xBBFD, 0xB9F9},
    };

    int total_tests = sizeof(bitwise_tests) / sizeof(bitwise_tests[0]);
    int and_passed = 0, or_passed = 0, xor_passed = 0;

    for (int i = 0; i < total_tests; i++) {
        // Test AND
        uint64_t and_result = alu_forward(alu, bitwise_tests[i].a, bitwise_tests[i].b, OP_AND);
        if (and_result == bitwise_tests[i].and_expected) {
            and_passed++;
        } else {
            printf("  AND FAIL: 0x%04X & 0x%04X = 0x%04X (expected 0x%04X)\n",
                   (unsigned int)bitwise_tests[i].a, (unsigned int)bitwise_tests[i].b,
                   (unsigned int)and_result, (unsigned int)bitwise_tests[i].and_expected);
        }

        // Test OR
        uint64_t or_result = alu_forward(alu, bitwise_tests[i].a, bitwise_tests[i].b, OP_OR);
        if (or_result == bitwise_tests[i].or_expected) {
            or_passed++;
        } else {
            printf("  OR FAIL: 0x%04X | 0x%04X = 0x%04X (expected 0x%04X)\n",
                   (unsigned int)bitwise_tests[i].a, (unsigned int)bitwise_tests[i].b,
                   (unsigned int)or_result, (unsigned int)bitwise_tests[i].or_expected);
        }

        // Test XOR
        uint64_t xor_result = alu_forward(alu, bitwise_tests[i].a, bitwise_tests[i].b, OP_XOR);
        if (xor_result == bitwise_tests[i].xor_expected) {
            xor_passed++;
        } else {
            printf("  XOR FAIL: 0x%04X ^ 0x%04X = 0x%04X (expected 0x%04X)\n",
                   (unsigned int)bitwise_tests[i].a, (unsigned int)bitwise_tests[i].b,
                   (unsigned int)xor_result, (unsigned int)bitwise_tests[i].xor_expected);
        }
    }
    printf("  AND: %d/%d passed\n", and_passed, total_tests);
    printf("  OR:  %d/%d passed\n", or_passed, total_tests);
    printf("  XOR: %d/%d passed\n", xor_passed, total_tests);
}

void test_cmp(ALU16* alu) {
    printf("\n=== CMP TESTS ===\n");

    struct { uint64_t a, b; int z, l, g; } cmp_tests[] = {
        // Equal cases
        {0, 0, 1, 0, 0},
        {0xFFFF, 0xFFFF, 1, 0, 0},
        {0x1234, 0x1234, 1, 0, 0},

        // Positive vs positive (unsigned comparison works same as signed)
        {5, 3, 0, 0, 1},       // 5 > 3
        {3, 5, 0, 1, 0},       // 3 < 5
        {0x5678, 0x1234, 0, 0, 1},  // 0x5678 > 0x1234
        {0x1234, 0x5678, 0, 1, 0},  // 0x1234 < 0x5678

        // Signed comparison: negative vs positive
        {0x0000, 0xFFFF, 0, 0, 1},   // FIXED: 0 > -1 (signed)
        {0xFFFF, 0x0000, 0, 1, 0},   // FIXED: -1 < 0 (signed)

        // Signed comparison: negative vs negative
        {0x8000, 0x7FFF, 0, 1, 0},   // -32768 < 32767
        {0x7FFF, 0x8000, 0, 0, 1},   // 32767 > -32768

        // Signed comparison: both negative
        {0x8000, 0x8001, 0, 1, 0},   // -32768 < -32767
        {0x8001, 0x8000, 0, 0, 1},   // -32767 > -32768
    };

    int total_tests = sizeof(cmp_tests) / sizeof(cmp_tests[0]);
    int passed = 0;

    for (int i = 0; i < total_tests; i++) {
        alu_forward(alu, cmp_tests[i].a, cmp_tests[i].b, OP_CMP);
        int z = alu->flags.zero;
        int l = alu->flags.less;
        int g = alu->flags.greater;
        int ez = cmp_tests[i].z;
        int el = cmp_tests[i].l;
        int eg = cmp_tests[i].g;

        if (z == ez && l == el && g == eg) {
            printf("  PASS: 0x%04X cmp 0x%04X: Z=%d L=%d G=%d\n",
                   (unsigned int)cmp_tests[i].a, (unsigned int)cmp_tests[i].b, z, l, g);
            passed++;
        } else {
            printf("  FAIL: 0x%04X cmp 0x%04X: Z=%d L=%d G=%d (expected Z=%d L=%d G=%d)\n",
                   (unsigned int)cmp_tests[i].a, (unsigned int)cmp_tests[i].b,
                   z, l, g, ez, el, eg);
        }
    }
    printf("  CMP: %d/%d passed\n", passed, total_tests);
}

void test_alu_edge_cases(ALU16* alu) {
    printf("\n=== EDGE CASE TESTS ===\n");

    int passed = 0;
    int total = 0;

    // Test all zero
    uint64_t result = alu_forward(alu, 0, 0, OP_ADD);
    printf("  ADD(0,0) = %" PRIu64 " (Z=%d) ", result, alu->flags.zero);
    if (result == 0 && alu->flags.zero == 1) { printf("PASS\n"); passed++; }
    else { printf("FAIL\n"); }
    total++;

    // Test all ones addition
    result = alu_forward(alu, 0xFFFF, 0xFFFF, OP_ADD);
    printf("  ADD(0xFFFF,0xFFFF) = 0x%04X (carry=%d) ", (unsigned int)result, alu->flags.carry);
    if (result == 0xFFFE && alu->flags.carry == 1) { printf("PASS\n"); passed++; }
    else { printf("FAIL\n"); }
    total++;

    // Test overflow addition
    result = alu_forward(alu, 0xFFFF, 1, OP_ADD);
    printf("  ADD(0xFFFF,1) = 0x%04X (carry=%d) ", (unsigned int)result, alu->flags.carry);
    if (result == 0 && alu->flags.carry == 1) { printf("PASS\n"); passed++; }
    else { printf("FAIL\n"); }
    total++;

    // Test multiplication overflow - FIXED
    result = alu_forward(alu, 0xFFFF, 2, OP_MUL);
    printf("  MUL(0xFFFF,2) = 0x%04X (OV=%d) ", (unsigned int)result, alu->flags.overflow);
    if (result == 0xFFFE && alu->flags.overflow == 1) { printf("PASS\n"); passed++; }
    else { printf("FAIL\n"); }
    total++;

    // Test negative subtraction
    result = alu_forward(alu, 1, 2, OP_SUB);
    printf("  SUB(1,2) = 0x%04X (borrow=%d) ", (unsigned int)result, alu->flags.carry);
    if (result == 0xFFFF && alu->flags.carry == 1) { printf("PASS\n"); passed++; }
    else { printf("FAIL\n"); }
    total++;

    printf("  EDGE CASES: %d/%d passed\n", passed, total);
}

int main() {
    printf("========================================\n");
    printf("  ALU16 CORE TESTERS\n");

    ALU16 alu;
    alu_init(&alu, 16);

    test_add(&alu);
    test_sub(&alu);
    test_mul(&alu);
    test_bitwise(&alu);
    test_cmp(&alu);
    test_alu_edge_cases(&alu);

    alu_free(&alu);

    printf("\n========================================\n");
    printf("  ALL TESTS COMPLETE\n");

    return 0;
}

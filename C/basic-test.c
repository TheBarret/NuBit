// test_adder.c - minimal adder test
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include "adder.h"

// void adder_debug(Adder* adder, const char* label);

void test_adder_simple() {
    Adder adder;
    adder_init(&adder, 4);  // Start with 4-bit for easier debugging

    printf("=== Testing 4-bit Adder ===\n\n");

    // Test 1: 5 + 3 = 8 (0101 + 0011 = 1000)
    uint64_t result;
    int carry = adder_forward(&adder, 5, 3, 0, &result);
    printf("5 + 3 = %" PRIu64 " (carry=%d)\n", result, carry);
    adder_debug(&adder, "5+3");

    printf("\n----------------------------------------\n\n");

    // Test 2: 0 + 0 = 0
    carry = adder_forward(&adder, 0, 0, 0, &result);
    printf("0 + 0 = %" PRIu64 " (carry=%d)\n", result, carry);
    adder_debug(&adder, "0+0");

    printf("\n----------------------------------------\n\n");

    // Test 3: 15 + 1 = 16 (1111 + 0001 = 10000, carry=1)
    carry = adder_forward(&adder, 15, 1, 0, &result);
    printf("15 + 1 = %" PRIu64 " (carry=%d)\n", result, carry);
    adder_debug(&adder, "15+1");

    adder_free(&adder);
}

int main() {
    test_adder_simple();
    return 0;
}

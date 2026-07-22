#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include "gates.h"
#include "adder.h"
#include "alu.h"

int main() {
    printf("Initializing NuBit ALU16...\n");

    ALU16 alu;
    alu_init(&alu, 16);

    printf("Testing ALU16 operations:\n");
    printf("============================================================\n");

    // Test ADD
    uint64_t result = alu_forward(&alu, 5, 3, OP_ADD);
    printf("5 + 3 = %" PRIu64 " (Z=%d, C=%d)\n",
           result, alu.flags.zero, alu.flags.carry);

    // Test SUB
    result = alu_forward(&alu, 10, 4, OP_SUB);
    printf("10 - 4 = %" PRIu64 " (Z=%d, C=%d)\n",
           result, alu.flags.zero, alu.flags.carry);

    // Test AND
    result = alu_forward(&alu, 0x00FF, 0x0F0F, OP_AND);
    printf("0x00FF & 0x0F0F = 0x%04" PRIX64 "\n", result);

    // Test OR
    result = alu_forward(&alu, 0x00FF, 0x0F00, OP_OR);
    printf("0x00FF | 0x0F00 = 0x%04" PRIX64 "\n", result);

    // Test XOR
    result = alu_forward(&alu, 0x00FF, 0x0F0F, OP_XOR);
    printf("0x00FF ^ 0x0F0F = 0x%04" PRIX64 "\n", result);

    // Test MUL
    result = alu_forward(&alu, 0x0010, 0x0010, OP_MUL);
    printf("16 * 16 = %" PRIu64 " (OV=%d)\n",
           result, alu.flags.overflow);

    // Test MUL overflow
    result = alu_forward(&alu, 0x0100, 0x0100, OP_MUL);
    printf("256 * 256 = %" PRIu64 " (OV=%d)\n",
           result, alu.flags.overflow);

    // Test CMP
    alu_forward(&alu, 0x1234, 0x5678, OP_CMP);
    printf("0x1234 cmp 0x5678: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    alu_forward(&alu, 0x5678, 0x1234, OP_CMP);
    printf("0x5678 cmp 0x1234: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    alu_forward(&alu, 0x1234, 0x1234, OP_CMP);
    printf("0x1234 cmp 0x1234: Z=%d, L=%d, G=%d\n",
           alu.flags.zero, alu.flags.less, alu.flags.greater);

    printf("============================================================\n");
    printf("All tests complete!\n");

    alu_free(&alu);
    return 0;
}

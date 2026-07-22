#include "alu.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

// =====================================================================
// HELPER FUNCTIONS
// =====================================================================

static inline void int_to_bits(uint64_t val, int bits, int* out) {
    for (int i = 0; i < bits; i++) {
        out[i] = (val >> i) & 1;
    }
}

static inline uint64_t bits_to_int(const int* bits, int n) {
    uint64_t res = 0;
    for (int i = 0; i < n; i++) {
        res |= ((uint64_t)bits[i]) << i;
    }
    return res;
}

// =====================================================================
// SUBTRACTOR
// =====================================================================

void subtractor_init(Subtractor* sub, int bits) {
    sub->bits = bits;
    sub->mask = (bits == 64) ? ~0ULL : ((1ULL << bits) - 1);
    not_gate_init(&sub->not_gate);
    adder_init(&sub->adder, bits);
    sub->B_inv_bits = (int*)calloc(bits, sizeof(int));
}

void subtractor_free(Subtractor* sub) {
    adder_free(&sub->adder);
    free(sub->B_inv_bits);
}

int subtractor_forward(Subtractor* sub, uint64_t A, uint64_t B, uint64_t* result) {
    A &= sub->mask;
    B &= sub->mask;

    // Use neural NOT gate for authenticity
    int_to_bits(B, sub->bits, sub->B_inv_bits);
    not_gate_forward(&sub->not_gate, sub->B_inv_bits, sub->bits, sub->B_inv_bits);

    uint64_t B_neg = bits_to_int(sub->B_inv_bits, sub->bits);

    // Add 1 to get two's complement
    uint64_t B_neg_plus_1 = 0;
    adder_forward(&sub->adder, B_neg, 1, 0, &B_neg_plus_1);

    // A - B = A + (-B)
    int carry = adder_forward(&sub->adder, A, B_neg_plus_1, 0, result);
    *result &= sub->mask;

    // Borrow is inverse of carry
    return carry ? 0 : 1;
}

// =====================================================================
// MULTIPLIER (Shift-and-Add)
// =====================================================================

void multiplier_init(SAMultiplier* mul, int bits) {
    mul->bits = bits;
    mul->mask = (bits == 64) ? ~0ULL : ((1ULL << bits) - 1);
    mul->full_mask = (bits * 2 == 64) ? ~0ULL : ((1ULL << (bits * 2)) - 1);
    adder_init(&mul->adder, bits * 2);
}

void multiplier_free(SAMultiplier* mul) {
    adder_free(&mul->adder);
}

uint64_t multiplier_forward(SAMultiplier* mul, uint64_t A, uint64_t B) {
    A &= mul->mask;
    B &= mul->mask;

    uint64_t result = 0;
    for (int i = 0; i < mul->bits; i++) {
        if ((B >> i) & 1) {
            uint64_t shifted = A << i;
            uint64_t temp_res = 0;
            adder_forward(&mul->adder, result, shifted, 0, &temp_res);
            result = temp_res;
        }
    }
    return result & mul->full_mask;
}

// =====================================================================
// BITWISE LOGIC
// =====================================================================

void bitwise_init(BitWiseLogic* bw, int bits, int gate_type) {
    bw->bits = bits;
    bw->gate_type = gate_type;

    and_gate_init(&bw->and_gate);
    or_gate_init(&bw->or_gate);

    if (gate_type == 2) {
        xor_gate_init(&bw->xor_gate, bits);
    }

    bw->A_bits = (int*)calloc(bits, sizeof(int));
    bw->B_bits = (int*)calloc(bits, sizeof(int));
    bw->result_bits = (int*)calloc(bits, sizeof(int));
}

void bitwise_free(BitWiseLogic* bw) {
    if (bw->gate_type == 2) {
        xor_gate_free(&bw->xor_gate);
    }
    free(bw->A_bits);
    free(bw->B_bits);
    free(bw->result_bits);
}

uint64_t bitwise_forward(BitWiseLogic* bw, uint64_t A, uint64_t B) {
    int_to_bits(A, bw->bits, bw->A_bits);
    int_to_bits(B, bw->bits, bw->B_bits);

    if (bw->gate_type == 0) {
        gate_forward(&bw->and_gate, bw->A_bits, bw->B_bits, bw->bits, bw->result_bits);
    } else if (bw->gate_type == 1) {
        gate_forward(&bw->or_gate, bw->A_bits, bw->B_bits, bw->bits, bw->result_bits);
    } else {
        xor_gate_forward(&bw->xor_gate, bw->A_bits, bw->B_bits, bw->bits, bw->result_bits);
    }

    return bits_to_int(bw->result_bits, bw->bits);
}

// =====================================================================
// COMPARATOR
// =====================================================================

void comparator_init(Comparator* cmp, int bits) {
    cmp->bits = bits;
    xor_gate_init(&cmp->xor_gate, bits);
    cmp->A_bits = (int*)calloc(bits, sizeof(int));
    cmp->B_bits = (int*)calloc(bits, sizeof(int));
    cmp->xor_results = (int*)calloc(bits, sizeof(int));
}

void comparator_free(Comparator* cmp) {
    xor_gate_free(&cmp->xor_gate);
    free(cmp->A_bits);
    free(cmp->B_bits);
    free(cmp->xor_results);
}

CmpResult comparator_forward(Comparator* cmp, uint64_t A, uint64_t B) {
    int_to_bits(A, cmp->bits, cmp->A_bits);
    int_to_bits(B, cmp->bits, cmp->B_bits);

    xor_gate_forward(&cmp->xor_gate, cmp->A_bits, cmp->B_bits, cmp->bits, cmp->xor_results);

    CmpResult res = {1, 0, 0};

    for (int i = cmp->bits - 1; i >= 0; i--) {
        if (cmp->xor_results[i] == 1) {
            res.equal = 0;
            if (cmp->A_bits[i] == 0 && cmp->B_bits[i] == 1) {
                res.less_than = 1;
            } else {
                res.greater_than = 1;
            }
            break;
        }
    }

    return res;
}

// =====================================================================
// ALU16
// =====================================================================

void alu_init(ALU16* alu, int bits) {
    adder_init(&alu->adder, bits);
    subtractor_init(&alu->subtractor, bits);
    bitwise_init(&alu->and_logic, bits, 0);
    bitwise_init(&alu->or_logic, bits, 1);
    bitwise_init(&alu->xor_logic, bits, 2);
    multiplier_init(&alu->multiplier, bits);
    comparator_init(&alu->comparator, bits);

    alu->flags = (ALUFlags){0, 0, 0, 0, 0};
}

void alu_free(ALU16* alu) {
    adder_free(&alu->adder);
    subtractor_free(&alu->subtractor);
    bitwise_free(&alu->and_logic);
    bitwise_free(&alu->or_logic);
    bitwise_free(&alu->xor_logic);
    multiplier_free(&alu->multiplier);
    comparator_free(&alu->comparator);
}

uint64_t alu_forward(ALU16* alu, uint64_t A, uint64_t B, Opcode op) {
    // All operations computed in parallel (authentic hardware model)
    uint64_t add_result = 0;
    int add_carry = adder_forward(&alu->adder, A, B, 0, &add_result);
    add_result &= 0xFFFF;

    uint64_t sub_result = 0;
    int sub_borrow = subtractor_forward(&alu->subtractor, A, B, &sub_result);
    sub_result &= 0xFFFF;

    uint64_t and_result = bitwise_forward(&alu->and_logic, A, B);
    uint64_t or_result = bitwise_forward(&alu->or_logic, A, B);
    uint64_t xor_result = bitwise_forward(&alu->xor_logic, A, B);

    uint64_t mul_full = multiplier_forward(&alu->multiplier, A, B);
    uint64_t mul_result = mul_full & 0xFFFF;
    uint64_t mul_overflow = (mul_full >> 16) & 0xFFFF;

    CmpResult cmp_result = comparator_forward(&alu->comparator, A, B);

    // Result lookup
    uint64_t result = 0;
    switch (op) {
        case OP_ADD: result = add_result; break;
        case OP_SUB: result = sub_result; break;
        case OP_AND: result = and_result; break;
        case OP_OR:  result = or_result; break;
        case OP_XOR: result = xor_result; break;
        case OP_MUL: result = mul_result; break;
        case OP_CMP: result = 0; break;
        default: result = 0; break;
    }

    // Reset flags
    alu->flags.zero = 0;
    alu->flags.carry = 0;
    alu->flags.overflow = 0;
    alu->flags.less = 0;
    alu->flags.greater = 0;

    // Update flags
    if (op == OP_CMP) {
        alu->flags.zero = cmp_result.equal;
        alu->flags.less = cmp_result.less_than;
        alu->flags.greater = cmp_result.greater_than;
    } else {
        alu->flags.zero = (result == 0) ? 1 : 0;

        if (op == OP_ADD) alu->flags.carry = add_carry;
        else if (op == OP_SUB) alu->flags.carry = sub_borrow;

        if (op == OP_MUL && mul_overflow != 0) {
            alu->flags.overflow = 1;
        }
    }

    return result;
}

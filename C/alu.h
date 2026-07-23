#ifndef ALU_H
#define ALU_H

#include <stdint.h>
#include <stdbool.h>
#include "gates.h"
#include "adder.h"

// =====================================================================
// DESIGN SHIFT 1: Enums instead of Class Constants
// Python uses classes with constants (Opcode.ADD = 0x0).
// C uses `enum`, which provides free type-checking and cleaner code.
// =====================================================================
typedef enum {
    OP_ADD   = 0x0,
    OP_SUB   = 0x1,
    OP_AND   = 0x2,
    OP_OR    = 0x3,
    OP_XOR   = 0x4,
    OP_MUL   = 0x5,
    OP_CMP   = 0x6,
    OP_LDI   = 0x7,
    OP_LDI16 = 0x8,
    OP_LD    = 0x9,
    OP_ST    = 0xA,
    OP_JMP   = 0xB,
    OP_JZ    = 0xC,
    OP_JNZ   = 0xD,
    OP_SYS   = 0xE,
    OP_HALT  = 0xF
} Opcode;

// =====================================================================
// DESIGN SHIFT 2: Structs instead of Dicts for Flags
// Python uses a dictionary for flags. C uses a struct, which is
// contiguous in memory, strictly typed, and much faster to reset.
// =====================================================================
typedef struct {
    int zero;
    int carry;
    int overflow;
    int less;
    int greater;
} ALUFlags;

// --- Subtractor ---
typedef struct {
    int bits;
    NotGate not_gate;
    Adder adder;
    uint64_t mask;
    int* B_inv_bits; // Pre-allocated buffer for ~B
} Subtractor;

void subtractor_init(Subtractor* sub, int bits);
void subtractor_free(Subtractor* sub);
int subtractor_forward(Subtractor* sub, uint64_t A, uint64_t B, uint64_t* result);

// --- Multiplier (Shift-and-Add) ---
typedef struct {
    int bits;
    Adder adder; // Needs 2*bits width for full product
    uint64_t mask;
    uint64_t full_mask;
} SAMultiplier;

void multiplier_init(SAMultiplier* mul, int bits);
void multiplier_free(SAMultiplier* mul);
uint64_t multiplier_forward(SAMultiplier* mul, uint64_t A, uint64_t B);

// --- BitWise Logic ---
typedef struct {
    int bits;
    int gate_type; // 0=AND, 1=OR, 2=XOR
    Gate and_gate;
    Gate or_gate;
    XorGate xor_gate;
    int* A_bits;
    int* B_bits;
    int* result_bits;
} BitWiseLogic;

void bitwise_init(BitWiseLogic* bw, int bits, int gate_type);
void bitwise_free(BitWiseLogic* bw);
uint64_t bitwise_forward(BitWiseLogic* bw, uint64_t A, uint64_t B);

// --- Comparator ---
typedef struct {
    int bits;
    XorGate xor_gate;
    int* A_bits;
    int* B_bits;
    int* xor_results;
} Comparator;

typedef struct {
    int equal;
    int less_than;
    int greater_than;
} CmpResult;

void comparator_init(Comparator* cmp, int bits);
void comparator_free(Comparator* cmp);
CmpResult comparator_forward(Comparator* cmp, uint64_t A, uint64_t B);

// --- ALU16 ---
typedef struct {
    Adder adder;
    Subtractor subtractor;
    BitWiseLogic and_logic;
    BitWiseLogic or_logic;
    BitWiseLogic xor_logic;
    SAMultiplier multiplier;
    Comparator comparator;
    ALUFlags flags;
} ALU16;

void alu_init(ALU16* alu, int bits);
void alu_free(ALU16* alu);
uint64_t alu_forward(ALU16* alu, uint64_t A, uint64_t B, Opcode op);

#endif // ALU_H

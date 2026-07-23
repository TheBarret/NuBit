// test_cpu.c - Complete CPU test harness
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <assert.h>
#include "cpu.h"

// ============================================================
// 1. SIMPLE MEMORY BUS IMPLEMENTATION
// ============================================================

uint16_t memory[65536];  // 64KB memory

uint16_t bus_tick(Bus* bus) {
    if (bus->rd) {
        bus->data_in = memory[bus->addr];
        return bus->data_in;
    } else if (bus->wr) {
        memory[bus->addr] = bus->data_out;
        return bus->data_out;
    }
    return 0;
}

void bus_init(Bus* bus) {
    memset(memory, 0, sizeof(memory));
    bus->addr = 0;
    bus->data_in = 0;
    bus->data_out = 0;
    bus->rd = 0;
    bus->wr = 0;
    bus->tick = bus_tick;
}

void cpu_load_program(CPU16* cpu, const uint16_t* program, int size) {
    for (int i = 0; i < size && i < 65536; i++) {
        memory[i] = program[i];
    }
    cpu->pc = 0x0000;
}

// ============================================================
// 2. TEST HELPER: Verify Register Values
// ============================================================

#define ASSERT_REG(cpu, reg, expected) \
    do { \
        if ((cpu)->regs[reg] != (expected)) { \
            printf("  FAIL: R%d = 0x%04X (expected 0x%04X)\n", \
                   reg, (cpu)->regs[reg], (expected)); \
            return false; \
        } \
    } while(0)

#define ASSERT_PC(cpu, expected) \
    do { \
        if ((cpu)->pc != (expected)) { \
            printf("  FAIL: PC = 0x%04X (expected 0x%04X)\n", \
                   (cpu)->pc, (expected)); \
            return false; \
        } \
    } while(0)

#define ASSERT_FLAG(cpu, flag, expected) \
    do { \
        if ((cpu)->alu.flags.flag != (expected)) { \
            printf("  FAIL: flag %s = %d (expected %d)\n", \
                   #flag, (cpu)->alu.flags.flag, (expected)); \
            return false; \
        } \
    } while(0)

// ============================================================
// 3. INSTRUCTION MACROS (for building programs)
// ============================================================

#define INSTR(op, dest, src1, src2)  ((op << 12) | (dest << 8) | (src1 << 4) | src2)

#define ADD(d, s1, s2)  INSTR(OP_ADD, d, s1, s2)
#define SUB(d, s1, s2)  INSTR(OP_SUB, d, s1, s2)
#define AND(d, s1, s2)  INSTR(OP_AND, d, s1, s2)
#define OR(d, s1, s2)   INSTR(OP_OR, d, s1, s2)
#define XOR(d, s1, s2)  INSTR(OP_XOR, d, s1, s2)
#define MUL(d, s1, s2)  INSTR(OP_MUL, d, s1, s2)
#define CMP(s1, s2)     INSTR(OP_CMP, 0, s1, s2)
#define LDI(d, imm)     INSTR(OP_LDI, d, 0, imm)
#define LDI16(d)        INSTR(OP_LDI16, d, 0, 0)
#define LD(d, s1)       INSTR(OP_LD, d, s1, 0)
#define ST(d, s1)       INSTR(OP_ST, d, s1, 0)
#define JMP(s1)         INSTR(OP_JMP, 0, s1, 0)
#define JZ(s1)          INSTR(OP_JZ, 0, s1, 0)
#define JNZ(s1)         INSTR(OP_JNZ, 0, s1, 0)
#define HALT()          INSTR(OP_HALT, 0, 0, 0)
#define SYS(id, r1, r2)     INSTR(OP_SYS, id, r1, r2)
#define DATA(value)     (value & 0xFFFF)

// ============================================================
// 4. TEST CASES
// ============================================================

bool test_add(CPU16* cpu) {
    printf("  ADD test...\n");

    uint16_t program[] = {
        LDI(1, 5),      // R1 = 5
        LDI(2, 3),      // R2 = 3
        ADD(0, 1, 2),   // R0 = R1 + R2
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_REG(cpu, 0, 8);
    ASSERT_FLAG(cpu, zero, 0);
    ASSERT_FLAG(cpu, carry, 0);

    printf("    PASS\n");
    return true;
}

bool test_sub(CPU16* cpu) {
    printf("  SUB test...\n");

    uint16_t program[] = {
        LDI(1, 10),     // R1 = 10
        LDI(2, 4),      // R2 = 4
        SUB(0, 1, 2),   // R0 = R1 - R2
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_REG(cpu, 0, 6);
    ASSERT_FLAG(cpu, zero, 0);
    ASSERT_FLAG(cpu, carry, 0);

    printf("    PASS\n");
    return true;
}

bool test_mul(CPU16* cpu) {
    printf("  MUL test...\n");

    uint16_t program[] = {
        LDI16(1),       // Address 0: R1 = next word (16)
        DATA(16),       // Address 1: data
        LDI16(2),       // Address 2: R2 = next word (16)
        DATA(16),       // Address 3: data
        MUL(0, 1, 2),   // Address 4: R0 = R1 * R2
        HALT()          // Address 5
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_REG(cpu, 0, 256);
    printf("    PASS\n");
    return true;
}

bool test_ldi16(CPU16* cpu) {
    printf("  LDI16 test...\n");

    uint16_t program[] = {
        LDI16(0),       // R0 = next word (0x1234)
        DATA(0x1234),
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_REG(cpu, 0, 0x1234);

    printf("    PASS\n");
    return true;
}

bool test_ld_st(CPU16* cpu) {
    printf("  LD/ST test...\n");

    uint16_t program[] = {
        LDI16(0),       // Address 0: R0 = next word (0x1000)
        DATA(0x1000),   // Address 1: data
        LDI16(1),       // Address 2: R1 = next word (0xABCD)
        DATA(0xABCD),   // Address 3: data
        ST(0, 1),       // Address 4: memory[R0] = R1
        LD(2, 0),       // Address 5: R2 = memory[R0]
        HALT()          // Address 6
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_REG(cpu, 2, 0xABCD);
    printf("    PASS\n");
    return true;
}

bool test_jmp(CPU16* cpu) {
    printf("  JMP test...\n");

    // Jump target: address 8 (LDI16(0) with data 42)
    uint16_t program[] = {
        LDI16(0),       // Address 0: R0 = 10
        DATA(10),       // Address 1
        LDI16(1),       // Address 2: R1 = 8 (jump target)
        DATA(8),        // Address 3
        JMP(1),         // Address 4: Jump to R1 (address 8)
        LDI16(0),       // Address 5: Skipped
        DATA(99),       // Address 6
        HALT(),         // Address 7: Skipped
        LDI16(0),       // Address 8: R0 = 42
        DATA(42),       // Address 9
        HALT()          // Address 10
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 15, false);

    ASSERT_REG(cpu, 0, 42);
    printf("    PASS\n");
    return true;
}

bool test_jz(CPU16* cpu) {
    printf("  JZ test...\n");

    // Jump target: address 9 (LDI16(0) with data 42)
    uint16_t program[] = {
        LDI(0, 5),          // Address 0: R0 = 5
        LDI(1, 5),          // Address 1: R1 = 5
        SUB(2, 0, 1),       // Address 2: R2 = R0 - R1 = 0 (Z=1)
        LDI16(3),           // Address 3: R3 = 9 (jump target)
        DATA(9),            // Address 4: <-- CHANGED from 8 to 9
        JZ(3),              // Address 5: Jump if Z=1
        LDI16(0),           // Address 6: Skipped
        DATA(99),           // Address 7: Skipped
        HALT(),             // Address 8: Skipped
        LDI16(0),           // Address 9: Should execute
        DATA(42),           // Address 10
        HALT()              // Address 11
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 15, false);

    ASSERT_REG(cpu, 0, 42);
    printf("    PASS\n");
    return true;
}

bool test_jnz(CPU16* cpu) {
    printf("  JNZ test...\n");

    // Jump target: address 9 (LDI16(0) with data 42)
    uint16_t program[] = {
        LDI(0, 5),          // Address 0: R0 = 5
        LDI(1, 3),          // Address 1: R1 = 3
        SUB(2, 0, 1),       // Address 2: R2 = R0 - R1 = 2 (Z=0)
        LDI16(3),           // Address 3: R3 = 9 (jump target)
        DATA(9),            // Address 4
        JNZ(3),             // Address 5: Jump if Z=0
        LDI16(0),           // Address 6: Skipped
        DATA(99),           // Address 7
        HALT(),             // Address 8: Skipped
        LDI16(0),           // Address 9: Should execute
        DATA(42),           // Address 10
        HALT()              // Address 11
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 15, false);

    ASSERT_REG(cpu, 0, 42);
    printf("    PASS\n");
    return true;
}

bool test_cmp_flags(CPU16* cpu) {
    printf("  CMP flags test...\n");

    // Test: Compare R0=5, R1=3 -> G=1
    uint16_t program[] = {
        LDI(0, 5),
        LDI(1, 3),
        CMP(0, 1),          // Compare R0, R1
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    ASSERT_FLAG(cpu, zero, 0);
    ASSERT_FLAG(cpu, less, 0);
    ASSERT_FLAG(cpu, greater, 1);

    printf("    PASS\n");
    return true;
}

bool test_flags_persist(CPU16* cpu) {
    printf("  Flags persistence test...\n");

    // Test that flags persist across operations
    uint16_t program[] = {
        LDI(0, 5),
        LDI(1, 3),
        CMP(0, 1),          // G=1
        LDI(2, 42),         // LDI should NOT change flags
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 0;
    cpu_run(cpu, 10, false);

    // Flags should still be G=1 from CMP
    ASSERT_FLAG(cpu, zero, 0);
    ASSERT_FLAG(cpu, less, 0);
    ASSERT_FLAG(cpu, greater, 1);

    printf("    PASS\n");
    return true;
}

bool test_sys(CPU16* cpu) {
    printf("  SYS test (PRINT_STR & PRINT_INT)...\n");

    // Simulating assembler output for:
    //   msg: .cstr "Hi\n"
    //   val: .d 42
    uint16_t program[] = {
        // Address 0-3: Setup string "Hi\n" (H=0x48, i=0x69, \n=0x0A, \0=0x00)
        DATA(0x0048), // 'H' (Address 0)
        DATA(0x0069), // 'i' (Address 1)
        DATA(0x000A), // '\n' (Address 2)
        DATA(0x0000), // '\0' (Address 3)
        // Address 4: Setup integer 42
        DATA(42),     // (Address 4)
        // Address 5: LDI16 R1, 0  (Load address of "Hi\n" into R1)
        INSTR(OP_LDI16, 1, 0, 0),
        DATA(0),
        // Address 7: SYS 0, R1, R0 (Print string at address in R1)
        SYS(0, 1, 0),
        // Address 8: LDI16 R2, 4 (Load address of 42 into R2)
        INSTR(OP_LDI16, 2, 0, 0),
        DATA(4),
        // Address 10: LD R3, R2   (Load value 42 from memory into R3)
        INSTR(OP_LD, 3, 2, 0),
        // Address 11: SYS 1, R3, R0 (Print integer in R3)
        SYS(1, 3, 0),
        // Address 12: SYS 2, R3, R0 (Print char '4' as example, or just halt)
        HALT()
    };

    cpu_load_program(cpu, program, sizeof(program)/sizeof(program[0]));
    cpu->pc = 5; // Start execution at the LDI16 to skip raw data
    cpu_run(cpu, 15, false);

    // If we reached here without crashing, and output was generated, it passed.
    // We can verify PC halted at the end.
    ASSERT_PC(cpu, 13); // PC should be at HALT + 1

    printf("    PASS\n");
    return true;
}

// ============================================================
// 5. RUN ALL TESTS
// ============================================================

int main() {
    printf("========================================\n");
    printf("  CPU16 CORE TESTERS\n");

    Bus bus;
    bus_init(&bus);

    CPU16 cpu;
    cpu_init(&cpu, &bus);

    int passed = 0;
    int total = 0;

    // Run all tests
    struct { bool (*func)(CPU16*); const char* name; } tests[] = {
        {test_add, "ADD"},
        {test_sub, "SUB"},
        {test_mul, "MUL"},
        {test_ldi16, "LDI16"},
        {test_ld_st, "LD/ST"},
        {test_jmp, "JMP"},
        {test_jz, "JZ"},
        {test_jnz, "JNZ"},
        {test_cmp_flags, "CMP flags"},
        {test_flags_persist, "Flags persist"},
        {test_sys, "System calls"}
    };

    for (int i = 0; i < sizeof(tests)/sizeof(tests[0]); i++) {
        // Reset CPU before each test
        memset(cpu.regs, 0, sizeof(cpu.regs));
        cpu.pc = 0;
        cpu.halted = false;
        memset(memory, 0, sizeof(memory));
        bus_init(&bus);
        cpu_init(&cpu, &bus);

        printf("[%d/%d] ", i+1, (int)(sizeof(tests)/sizeof(tests[0])));
        if (tests[i].func(&cpu)) {
            passed++;
        }
        total++;
    }

    cpu_free(&cpu);

    printf("\n========================================\n");
    printf("  RESULTS: %d/%d tests passed\n", passed, total);
    printf("========================================\n");

    return (passed == total) ? 0 : 1;
}

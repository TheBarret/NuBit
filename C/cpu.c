#include "cpu.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Forward declarations for instruction handlers
static bool op_add(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_sub(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_and(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_or(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_xor(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_mul(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_cmp(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_ldi(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_ldi16(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_ld(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_st(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_jmp(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_jz(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_jnz(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
static bool op_halt(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);

// CPU Initialization
void cpu_init(CPU16* cpu, Bus* bus) {
    cpu->bus = bus;
    alu_init(&cpu->alu, 16);
    memset(cpu->regs, 0, sizeof(cpu->regs));
    cpu->pc = 0x0000;
    cpu->halted = false;

    // DESIGN SHIFT FIX: Zero-initialize dispatch table first
    memset(cpu->dispatch, 0, sizeof(cpu->dispatch));

    // Build dispatch table
    cpu->dispatch[OP_ADD] = op_add;
    cpu->dispatch[OP_SUB] = op_sub;
    cpu->dispatch[OP_AND] = op_and;
    cpu->dispatch[OP_OR] = op_or;
    cpu->dispatch[OP_XOR] = op_xor;
    cpu->dispatch[OP_MUL] = op_mul;
    cpu->dispatch[OP_CMP] = op_cmp;
    cpu->dispatch[OP_LDI] = op_ldi;
    cpu->dispatch[OP_LDI16] = op_ldi16;
    cpu->dispatch[OP_LD] = op_ld;
    cpu->dispatch[OP_ST] = op_st;
    cpu->dispatch[OP_JMP] = op_jmp;
    cpu->dispatch[OP_JZ] = op_jz;
    cpu->dispatch[OP_JNZ] = op_jnz;
    // OP_HALT = 0xF is set below
    cpu->dispatch[OP_HALT] = op_halt;
    // Slot 0xE (14) remains NULL = unknown opcode
}

void cpu_free(CPU16* cpu) {
    alu_free(&cpu->alu);
}

// Bus Interface
uint16_t cpu_read_memory(CPU16* cpu, uint16_t addr) {
    cpu->bus->addr = addr & 0xFFFF;
    cpu->bus->rd = 1;
    cpu->bus->wr = 0;
    uint16_t result = cpu->bus->tick(cpu->bus);
    cpu->bus->rd = 0;  // Reset to idle
    return result;
}

void cpu_write_memory(CPU16* cpu, uint16_t addr, uint16_t data) {
    cpu->bus->addr = addr & 0xFFFF;
    cpu->bus->data_out = data & 0xFFFF;
    cpu->bus->wr = 1;
    cpu->bus->rd = 0;
    cpu->bus->tick(cpu->bus);
    cpu->bus->wr = 0;  // Reset to idle
}

// Fetch/Decode/Execute
/* uint16_t cpu_fetch(CPU16* cpu) {
    if (cpu->halted) {
        return 0;
    }
    uint16_t instruction = cpu_read_memory(cpu, cpu->pc);
    cpu->pc = (cpu->pc + 1) & 0xFFFF;
    return instruction;
    } */
// debugger version
uint16_t cpu_fetch(CPU16* cpu) {
    if (cpu->halted) {
        return 0;
    }
    uint16_t instruction = cpu_read_memory(cpu, cpu->pc);
    printf(" * (FETCH: PC=0x%04X IR=0x%04X)\n", cpu->pc, instruction);
    cpu->pc = (cpu->pc + 1) & 0xFFFF;
    return instruction;
}

void cpu_decode(uint16_t instruction, uint8_t* op, uint8_t* dest, uint8_t* src1, uint8_t* src2) {
    *op = (instruction >> 12) & 0xF;
    *dest = (instruction >> 8) & 0xF;
    *src1 = (instruction >> 4) & 0xF;
    *src2 = instruction & 0xF;
}

bool cpu_execute(CPU16* cpu, uint16_t instruction) {
    uint8_t op, dest, src1, src2;
    cpu_decode(instruction, &op, &dest, &src1, &src2);

    // DESIGN SHIFT: Function pointer dispatch (O(1)) instead of dict lookup
    bool (*handler)(CPU16*, uint8_t, uint8_t, uint8_t) = cpu->dispatch[op];

    if (handler == NULL) {
        printf("  WARNING: Unknown opcode 0x%X\n", op);
        return true;
    }

    return handler(cpu, dest, src1, src2);
}

// Generic ALU Operation Helper
static bool op_alu(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2, Opcode opcode) {
    uint64_t result = alu_forward(&cpu->alu, cpu->regs[src1], cpu->regs[src2], opcode);
    cpu->regs[dest] = (uint16_t)(result & 0xFFFF);
    return true;
}

// Instruction Handlers
static bool op_add(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_ADD);
}

static bool op_sub(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_SUB);
}

static bool op_and(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_AND);
}

static bool op_or(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_OR);
}

static bool op_xor(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_XOR);
}

static bool op_mul(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    return op_alu(cpu, dest, src1, src2, OP_MUL);
}

static bool op_cmp(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    (void)dest;  // Suppress unused parameter warning
    (void)src2;
    alu_forward(&cpu->alu, cpu->regs[src1], cpu->regs[src2], OP_CMP);
    return true;
}

static bool op_ldi(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Load 4-bit immediate
    cpu->regs[dest] = src2;
    return true;
}

static bool op_ldi16(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Load 16-bit immediate (next word in memory)
    cpu->regs[dest] = cpu_read_memory(cpu, cpu->pc);
    cpu->pc = (cpu->pc + 1) & 0xFFFF;
    return true;
}

static bool op_ld(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Load from memory address in register
    uint16_t addr = cpu->regs[src1];
    cpu->regs[dest] = cpu_read_memory(cpu, addr);
    return true;
}

static bool op_st(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Store register to memory address in register
    uint16_t addr = cpu->regs[dest];
    uint16_t value = cpu->regs[src1];
    cpu_write_memory(cpu, addr, value);
    return true;
}

static bool op_jmp(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Unconditional jump
    cpu->pc = cpu->regs[src1];
    return true;
}

static bool op_jz(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Jump if zero flag set
    if (cpu->alu.flags.zero == 1) {
        cpu->pc = cpu->regs[src1];
    }
    return true;
}

static bool op_jnz(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Jump if zero flag not set
    if (cpu->alu.flags.zero == 0) {
        cpu->pc = cpu->regs[src1];
    }
    return true;
}

static bool op_halt(CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2) {
    // Halt CPU
    cpu->halted = true;
    return false;
}

// Main Execution Loop
int cpu_run(CPU16* cpu, int max_cycles, bool verbose) {
    int cycles = 0;
    bool running = true;

    while (running && cycles < max_cycles) {
        uint16_t instruction = cpu_fetch(cpu);

        if (verbose) {
            uint8_t op, dest, src1, src2;
            cpu_decode(instruction, &op, &dest, &src1, &src2);
            printf("  [%3d] PC=%04X IR=%04X OP=%X R%d,R%d,R%d  "
                   "flags={Z=%d,C=%d,O=%d,L=%d,G=%d}\n",
                   cycles, (cpu->pc - 1) & 0xFFFF, instruction, op, dest, src1, src2,
                   cpu->alu.flags.zero, cpu->alu.flags.carry, cpu->alu.flags.overflow,
                   cpu->alu.flags.less, cpu->alu.flags.greater);
        }

        running = cpu_execute(cpu, instruction);
        cycles++;
    }

    return cycles;
}

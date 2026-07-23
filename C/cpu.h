#ifndef CPU_H
#define CPU_H

#include <stdint.h>
#include <stdbool.h>
#include "alu.h"

// Forward declaration of Bus struct
/*typedef struct Bus Bus;
// Bus Interface
struct Bus {
    uint16_t addr;
    uint16_t data_in;   // Data read from memory
    uint16_t data_out;  // Data to write to memory
    int rd;             // Read signal (1 = reading)
    int wr;             // Write signal (1 = writing)
    uint16_t (*tick)(Bus* bus);  // Use Bus*, not struct Bus*
    };*/

typedef struct Bus Bus;
struct Bus {
    uint16_t addr;
    uint16_t data_in;
    uint16_t data_out;
    int rd;
    int wr;
    uint16_t (*tick)(Bus* bus);
};

// CPU16 Structure
typedef struct CPU16 {
    Bus* bus;
    ALU16 alu;
    uint16_t regs[16];
    uint16_t pc;
    bool halted;
    bool (*dispatch[16])(struct CPU16* cpu, uint8_t dest, uint8_t src1, uint8_t src2);
} CPU16;

// Function Declarations
void cpu_init(CPU16* cpu, Bus* bus);
void cpu_free(CPU16* cpu);

// Bus interface
uint16_t cpu_read_memory(CPU16* cpu, uint16_t addr);
void cpu_write_memory(CPU16* cpu, uint16_t addr, uint16_t data);

// Fetch/Decode/Execute
uint16_t cpu_fetch(CPU16* cpu);
void cpu_decode(uint16_t instruction, uint8_t* op, uint8_t* dest, uint8_t* src1, uint8_t* src2);
bool cpu_execute(CPU16* cpu, uint16_t instruction);

// Main loop
int cpu_run(CPU16* cpu, int max_cycles, bool verbose);

#endif // CPU_H

#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <unistd.h>  // for isatty
#include "cpu.h"
#include "bus.h"

int main(int argc, char** argv) {
    Bus bus;
    CPU16 cpu;

    bus_init(&bus);
    cpu_init(&cpu, &bus);

    // Load program from file (not stdin)
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <program.hex>\n", argv[0]);
        return 1;
    }

    FILE* prog = fopen(argv[1], "r");
    if (!prog) {
        fprintf(stderr, "Error: Cannot open %s\n", argv[1]);
        return 1;
    }

    uint16_t addr = 0;
    char line[16];
    while (fgets(line, sizeof(line), prog)) {
        uint16_t word = (uint16_t)strtol(line, NULL, 16);
        bus_write(&bus, addr++, word);
    }
    fclose(prog);

    // Set stack pointer
    cpu.regs[15] = 0xFFF0;

    // Run - stdin is now free for user input!
    printf("\n=== NubitVM Execution ===\n");
    int cycles = cpu_run(&cpu, 100000, false);
    printf("\n=== Halted after %d cycles ===\n", cycles);

    cpu_free(&cpu);
    return 0;
}

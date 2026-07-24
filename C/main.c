#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <unistd.h>  // for isatty
#include "cpu.h"
#include "bus.h"

// Read hex from stdin and run the program
int run_pipeline_mode(void) {
    Bus bus;
    bus_init(&bus);

    CPU16 cpu;
    cpu_init(&cpu, &bus);

    // Read hex words from stdin
    uint16_t addr = 0;
    uint32_t word;
    int count = 0;

    while (scanf("%4" SCNx32, &word) == 1) {
        bus_write(&bus, addr++, (uint16_t)word);
        count++;
    }

    if (count == 0) {
        fprintf(stderr, "No program loaded from stdin\n");
        return 1;
    }

    // Set PC to 0 and run
    cpu.pc = 0x0000;
    cpu.halted = false;

    // Run with verbose output (optional)
    int cycles = cpu_run(&cpu, 100000, true);

    //printf("\nCycles executed: %d\n", cycles);

    cpu_free(&cpu);
    return 0;
}

int main(int argc, char** argv) {
    // Check if we're in pipeline mode (stdin has data, or -p flag)
    if (argc > 1 && strcmp(argv[1], "-p") == 0) {
        return run_pipeline_mode();
    }

    // If stdin is not a terminal and has data, run pipeline mode
    if (!isatty(fileno(stdin))) {
        return run_pipeline_mode();
    }

    return 0;
}

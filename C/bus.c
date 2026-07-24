// bus.c - Neuristor-fabric memory bus
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include "headers/cpu.h"
#include "memory/neuristor.h"

#define ADDR_ROW_BITS 8
#define ADDR_COL_BITS 8
#define ROWS (1 << ADDR_ROW_BITS)   // 256
#define COLS (1 << ADDR_COL_BITS)   // 256
#define NUM_PLANES 16

static Neuristor* planes[NUM_PLANES];  // heap-allocated, one 256x256 grid per bit

static void addr_to_rowcol(uint16_t addr, uint32_t* row, uint32_t* col) {
    *row = (addr >> ADDR_COL_BITS) & (ROWS - 1);
    *col = addr & (COLS - 1);
}

uint16_t bus_tick(Bus* bus) {
    uint32_t row, col;
    addr_to_rowcol(bus->addr, &row, &col);

    if (bus->rd) {
        uint16_t word = 0;
        for (int i = 0; i < NUM_PLANES; i++) {
            Neuristor* cell = &planes[i][row * COLS + col];
            NeuristorReadResult r = neuristor_read(cell, 1, 1, 1);
            if (r.state == NEURISTOR_POSITIVE) word |= (1u << i);
            neuristor_refresh(cell, 1, 1, 1, r.state);  // restore, hidden from CPU
            //if (bus->debug) {
            //                printf("%s", neuristor_state_to_string(r.state));
            //            }
        }
        bus->data_in = word;
        return word;
    } else if (bus->wr) {
        for (int i = 0; i < NUM_PLANES; i++) {
            Neuristor* cell = &planes[i][row * COLS + col];
            NeuristorState bit = (bus->data_out & (1u << i)) ? NEURISTOR_POSITIVE : NEURISTOR_NEGATIVE;
            neuristor_write(cell, 1, 1, 1, bit);
            //if (bus->debug) printf("%s", neuristor_state_to_string(bit));
        }
        return bus->data_out;
    }
    return 0;
}

void bus_init(Bus* bus) {
    for (int i = 0; i < NUM_PLANES; i++) {
        planes[i] = malloc(sizeof(Neuristor) * ROWS * COLS);
        for (int r = 0; r < ROWS; r++) {
            for (int c = 0; c < COLS; c++) {
                neuristor_init(&planes[i][r * COLS + c], r, c);
            }
        }
    }
    bus->addr = 0;
    bus->data_in = 0;
    bus->data_out = 0;
    bus->rd = 0;
    bus->wr = 0;
    bus->tick = bus_tick;
}

uint16_t bus_read(Bus* bus, uint16_t addr) {
    bus->addr = addr;
    bus->rd = 1;
    bus->wr = 0;
    uint16_t result = bus->tick(bus);
    bus->rd = 0;
    return result;
}

void bus_write(Bus* bus, uint16_t addr, uint16_t data) {
    bus->addr = addr;
    bus->data_out = data;
    bus->rd = 0;
    bus->wr = 1;
    bus->tick(bus);
    bus->wr = 0;
}

void bus_load_hex(Bus* bus, const uint16_t* program, int size) {
    for (int i = 0; i < size && i < 65536; i++) {
        bus_write(bus, (uint16_t)i, program[i]);
    }
}

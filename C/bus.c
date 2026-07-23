// bus.c - Simple memory bus
#include <stdint.h>
#include <string.h>
#include "cpu.h"

static uint16_t memory[65536];  // 64KB memory

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
        memory[i] = program[i];
    }
}

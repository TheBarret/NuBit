#ifndef BUS_H
#define BUS_H

#include <stdint.h>
#include "cpu.h"

void bus_init(Bus* bus);
uint16_t bus_read(Bus* bus, uint16_t addr);
void bus_write(Bus* bus, uint16_t addr, uint16_t data);
void bus_load_hex(Bus* bus, const uint16_t* program, int size);

#endif // BUS_H

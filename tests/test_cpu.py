# test_cpu16.py

import numpy as np
from storage import UnifiedBus, Memory
from machine16 import CPU16, Opcode

def test_cpu16():
    """Test the new CPU16 architecture."""

    # Setup
    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))

    cpu = CPU16(bus)

    # Test program: 5 + 3 = 8
    # Uses LDI16 to load 16-bit values
    program = [
        (Opcode.LDI16 << 12) | (0 << 8),  # LDI16 R0 (next word is immediate)
        0x0005,                           # Value 5
        (Opcode.LDI16 << 12) | (1 << 8),  # LDI16 R1
        0x0003,                           # Value 3
        (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,  # ADD R2, R0, R1
        (Opcode.HALT << 12)               # HALT
    ]

    # Load program
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)

    cpu.pc = 0x0100

    # Run with verbose output
    cycles = cpu.run(max_cycles=20, verbose=True)

    print("\n" + "=" * 60)
    print(f"Executed {cycles} cycles")
    print(f"R0: {cpu.regs[0]} (expected 5)")
    print(f"R1: {cpu.regs[1]} (expected 3)")
    print(f"R2: {cpu.regs[2]} (expected 8)")
    print(f"Flags: {cpu.alu.flags}")

    if cpu.regs[2] == 8:
        print("PASSED")
    else:
        print("FAILED")

if __name__ == "__main__":
    test_cpu16()

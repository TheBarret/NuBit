# test16.py

import numpy as np
from storage import UnifiedBus, Memory
from machine16 import CPU16

def test_cpu():
    """Test CPU with bus and memory."""
    print("=" * 60)
    print("CPU16 TEST")
    print("=" * 60)

    # Setup
    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))

    cpu = CPU16(bus)

    # Program: 5 + 3 = 8 using LDI
    # 0x0100: LDI R0, 5     (op=7, dest=0, src1=0, imm=5) → 0x7005
    # 0x0101: LDI R1, 3     (op=7, dest=1, src1=0, imm=3) → 0x7103
    # 0x0102: ADD R2, R0, R1 (op=0, dest=2, src1=0, src2=1) → 0x0201
    # 0x0103: HALT          (op=15, all zeros) → 0xF000

    program = [
        0x7005,  # LDI R0, 5
        0x7103,  # LDI R1, 3
        0x0201,  # ADD R2, R0, R1
        0xF000   # HALT
    ]

    # Load program into memory
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)

    # Set PC
    cpu.pc = 0x0100

    print("Program loaded at 0x0100:")
    for i in range(5):
        inst = mem.read(0x0100 + i)
        print(f"  0x{0x0100+i:04X}: 0x{inst:04X}")

    # Run
    cycles = cpu.run()
    print(f"\nExecuted {cycles} cycles")
    print(f"R0: {cpu.regs[0]} (expected 5)")
    print(f"R1: {cpu.regs[1]} (expected 3)")
    print(f"R2: {cpu.regs[2]} (expected 8)")

    if cpu.regs[2] == 8:
        print("PASSED")
    else:
        print("FAILED")

    # Bus stats
    print(f"\nBus stats:")
    print(f"  Cycles: {bus.cycles}")
    print(f"  Last op: {bus.last_op}")
    print(f"  Memory stats: {mem.get_stats()}")

if __name__ == "__main__":
    test_cpu()

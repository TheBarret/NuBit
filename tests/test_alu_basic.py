# test_alu_basic.py
import numpy as np
from storage import UnifiedBus, Memory
from machine16 import CPU16, Opcode

def setup_cpu():
    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))
    cpu = CPU16(bus)
    cpu.pc = 0x0100
    return cpu, mem

def run_program(cpu, mem, program):
    """Load and run program, return registers and flags."""
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)
    cpu.pc = 0x0100
    cpu.run(max_cycles=50, verbose=False)
    return cpu.regs.copy(), cpu.alu.flags.copy()

def test_alu_ops():
    tests = [
        ("ADD", Opcode.ADD, 5, 3, 8),
        ("SUB", Opcode.SUB, 10, 4, 6),
        ("AND", Opcode.AND, 0b1010, 0b1100, 0b1000),
        ("OR",  Opcode.OR,  0b1010, 0b1100, 0b1110),
        ("XOR", Opcode.XOR, 0b1010, 0b1100, 0b0110),
    ]

    passed = 0
    for name, op, a, b, expected in tests:
        cpu, mem = setup_cpu()

        # Load R0=a, R1=b, compute op, halt
        program = [
            (Opcode.LDI16 << 12) | (0 << 8),
            a,
            (Opcode.LDI16 << 12) | (1 << 8),
            b,
            (op << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12)
        ]

        regs, _ = run_program(cpu, mem, program)
        result = regs[2]

        status = "✓" if result == expected else "✗"
        print(f"{status} {name}: {a} {name} {b} = {result} (expected {expected})")
        passed += (result == expected)

    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    test_alu_ops()

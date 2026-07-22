# test_alu_mul_cmp.py
import numpy as np
from storage import UnifiedBus, Memory
from machine16 import CPU16, Opcode, Flag

def setup_cpu():
    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))
    cpu = CPU16(bus)
    cpu.pc = 0x0100
    return cpu, mem

def run_program(cpu, mem, program):
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)
    cpu.pc = 0x0100
    cpu.run(max_cycles=50, verbose=False)
    return cpu.regs.copy(), cpu.alu.flags.copy()

def test_mul():
    tests = [
        (2, 3, 6, "no overflow"),
        (0x0010, 0x0010, 0x0100, "no overflow"),
        (0xFFFF, 1, 0xFFFF, "no overflow"),
        (0x0100, 0x0100, 0x0000, "overflow"),  # 256*256=65536 -> 0x0000
    ]

    passed = 0
    for a, b, expected, desc in tests:
        cpu, mem = setup_cpu()
        program = [
            (Opcode.LDI16 << 12) | (0 << 8), a,
            (Opcode.LDI16 << 12) | (1 << 8), b,
            (Opcode.MUL << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12)
        ]

        regs, flags = run_program(cpu, mem, program)
        result = regs[2]
        overflow = flags[Flag.OVERFLOW]

        status = "✓" if result == expected else "✗"
        overflow_status = f"overflow={overflow}" if overflow else "no overflow"
        print(f"{status} {a} * {b} = {result:04X} (expected {expected:04X}) [{overflow_status}]")
        passed += (result == expected)

    print(f"Passed: {passed}/{len(tests)}")
    return passed == len(tests)

def test_cmp():
    print("\n" + "=" * 60)
    print("COMPARISON TESTS")
    print("=" * 60)

    tests = [
        (5, 5, (1, 0, 0), "equal"),
        (3, 5, (0, 1, 0), "less"),
        (5, 3, (0, 0, 1), "greater"),
        (0, 0xFFFF, (0, 1, 0), "less (unsigned)"),
    ]

    passed = 0
    for a, b, expected_flags, desc in tests:
        cpu, mem = setup_cpu()
        program = [
            (Opcode.LDI16 << 12) | (0 << 8), a,
            (Opcode.LDI16 << 12) | (1 << 8), b,
            (Opcode.CMP << 12) | (0 << 4) | 1,  # CMP R0, R1
            (Opcode.HALT << 12)
        ]

        _, flags = run_program(cpu, mem, program)
        zero, less, greater = flags[Flag.ZERO], flags[Flag.LESS], flags[Flag.GREATER]
        got = (zero, less, greater)

        status = "✓" if got == expected_flags else "✗"
        print(f"{status} {a} cmp {b}: {got} (expected {expected_flags}) [{desc}]")
        passed += (got == expected_flags)

    print(f"Passed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    test_mul()
    test_cmp()

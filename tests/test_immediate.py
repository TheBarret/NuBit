# test_immediate.py
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
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)
    cpu.pc = 0x0100
    cpu.run(max_cycles=50, verbose=False)
    return cpu.regs.copy(), cpu.alu.flags.copy()

def test_immediate():
    tests = []

    # Test 1: LDI (4-bit immediate)
    tests.append({
        'name': 'LDI 4-bit',
        'program': [
            (Opcode.LDI << 12) | (0 << 8) | 0x5,  # LDI R0, 5
            (Opcode.LDI << 12) | (1 << 8) | 0xA,  # LDI R1, 10
            (Opcode.LDI << 12) | (2 << 8) | 0xF,  # LDI R2, 15
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[0] == 5 and regs[1] == 10 and regs[2] == 15,
        'desc': 'LDI should load 4-bit immediate (0-15)'
    })

    # Test 2: LDI16 (16-bit immediate)
    tests.append({
        'name': 'LDI16 16-bit',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x1234,  # LDI16 R0, 0x1234
            (Opcode.LDI16 << 12) | (1 << 8), 0xABCD,  # LDI16 R1, 0xABCD
            (Opcode.LDI16 << 12) | (2 << 8), 0xFFFF,  # LDI16 R2, 0xFFFF
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[0] == 0x1234 and regs[1] == 0xABCD and regs[2] == 0xFFFF,
        'desc': 'LDI16 should load 16-bit immediate'
    })

    # Test 3: LDI16 with PC increment (2 words)
    tests.append({
        'name': 'LDI16 PC increment',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0xAAAA,  # R0 = 0xAAAA
            (Opcode.LDI16 << 12) | (1 << 8), 0xBBBB,  # R1 = 0xBBBB
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[0] == 0xAAAA and regs[1] == 0xBBBB,
        'desc': 'LDI16 should increment PC by 2 (opcode + immediate)'
    })

    # Test 4: LDI and LDI16 combined
    tests.append({
        'name': 'LDI + LDI16 combined',
        'program': [
            (Opcode.LDI << 12) | (0 << 8) | 0x7,        # R0 = 7
            (Opcode.LDI16 << 12) | (1 << 8), 0x00FF,   # R1 = 0x00FF
            (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,  # R2 = R0 + R1 = 7 + 255 = 262
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[2] == 262,
        'desc': 'LDI and LDI16 should work together'
    })

    # Test 5: LDI zero and max values
    tests.append({
        'name': 'LDI boundary values',
        'program': [
            (Opcode.LDI << 12) | (0 << 8) | 0x0,        # R0 = 0
            (Opcode.LDI << 12) | (1 << 8) | 0xF,        # R1 = 15
            (Opcode.LDI16 << 12) | (2 << 8), 0x0000,   # R2 = 0x0000
            (Opcode.LDI16 << 12) | (3 << 8), 0xFFFF,   # R3 = 0xFFFF
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[0] == 0 and regs[1] == 15 and regs[2] == 0 and regs[3] == 0xFFFF,
        'desc': 'LDI/LDI16 should handle boundary values (0, 15, 0x0000, 0xFFFF)'
    })

    passed = 0
    for test in tests:
        cpu, mem = setup_cpu()
        regs, _ = run_program(cpu, mem, test['program'])
        result = test['check'](regs)
        status = "✓" if result else "✗"
        print(f"{status} {test['name']}: {test['desc']}")
        if not result:
            print(f"    Regs: R0={regs[0]:04X} R1={regs[1]:04X} R2={regs[2]:04X} R3={regs[3]:04X}")
        passed += result

    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    test_immediate()

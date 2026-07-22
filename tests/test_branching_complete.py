# test_branching_complete.py
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
    cpu.run(max_cycles=100, verbose=False)
    return cpu.regs.copy(), cpu.alu.flags.copy()

def test_branching():
    tests = []

    # Test 1: JZ when Z=1 (should jump)
    # Layout:
    # 0x0100-0x0103: Setup (LDI16 R0,5 and LDI16 R1,5)
    # 0x0104: CMP R0,R1 -> Z=1
    # 0x0105-0x0106: LDI16 R2, TARGET
    # 0x0107: JZ R2
    # 0x0108-0x0109: LDI16 R3, 0xFFFF (skipped)
    # 0x010A: HALT
    # TARGET = 0x010B: LDI16 R3, 0xAAAA
    # 0x010C: immediate
    # 0x010D: HALT
    tests.append({
        'name': 'JZ (Z=1) jump',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0005,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0005,
            (Opcode.CMP << 12) | (0 << 4) | 1,
            (Opcode.LDI16 << 12) | (2 << 8), 0x010B,  # TARGET
            (Opcode.JZ << 12) | (2 << 4),
            (Opcode.LDI16 << 12) | (3 << 8), 0xFFFF,  # Skipped
            (Opcode.HALT << 12),
            # TARGET at 0x010B
            (Opcode.LDI16 << 12) | (3 << 8), 0xAAAA,
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0xAAAA,
        'desc': 'JZ should jump when Z=1'
    })

    # Test 2: JZ when Z=0 (should NOT jump)
    tests.append({
        'name': 'JZ (Z=0) no jump',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0005,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0003,
            (Opcode.CMP << 12) | (0 << 4) | 1,
            (Opcode.LDI16 << 12) | (2 << 8), 0x010B,  # Target (won't jump)
            (Opcode.JZ << 12) | (2 << 4),
            (Opcode.LDI16 << 12) | (3 << 8), 0xBBBB,  # Executed
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0xBBBB,
        'desc': 'JZ should NOT jump when Z=0'
    })

    # Test 3: JNZ when Z=0 (should jump)
    tests.append({
        'name': 'JNZ (Z=0) jump',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0005,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0003,
            (Opcode.CMP << 12) | (0 << 4) | 1,
            (Opcode.LDI16 << 12) | (2 << 8), 0x010B,  # TARGET
            (Opcode.JNZ << 12) | (2 << 4),
            (Opcode.LDI16 << 12) | (3 << 8), 0xCCCC,  # Skipped
            (Opcode.HALT << 12),
            # TARGET at 0x010B
            (Opcode.LDI16 << 12) | (3 << 8), 0xDDDD,
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0xDDDD,
        'desc': 'JNZ should jump when Z=0'
    })

    # Test 4: JNZ when Z=1 (should NOT jump)
    tests.append({
        'name': 'JNZ (Z=1) no jump',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0005,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0005,
            (Opcode.CMP << 12) | (0 << 4) | 1,
            (Opcode.LDI16 << 12) | (2 << 8), 0x010B,  # Target (won't jump)
            (Opcode.JNZ << 12) | (2 << 4),
            (Opcode.LDI16 << 12) | (3 << 8), 0xEEEE,  # Executed
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0xEEEE,
        'desc': 'JNZ should NOT jump when Z=1'
    })

    # Test 5: JMP unconditional
    tests.append({
        'name': 'JMP unconditional',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0106,  # TARGET = 0x0106 (next free address)
            (Opcode.JMP << 12) | (0 << 4),
            (Opcode.LDI16 << 12) | (3 << 8), 0xFFFF,  # Skipped
            (Opcode.HALT << 12),
            # TARGET at 0x0106
            (Opcode.LDI16 << 12) | (3 << 8), 0x1234,
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0x1234,
        'desc': 'JMP should always jump'
    })

    passed = 0
    for test in tests:
        cpu, mem = setup_cpu()
        regs, _ = run_program(cpu, mem, test['program'])
        result = test['check'](regs)
        status = "✓" if result else "✗"
        print(f"{status} {test['name']}: {test['desc']}")
        passed += result

    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    test_branching()

# test_memory.py
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

def test_memory_ops():
    tests = []

    # Test 1: LD - Load from memory into register
    # Store value 0x1234 at address 0x2000, then load into R3
    tests.append({
        'name': 'LD (load from memory)',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x2000,  # R0 = address
            (Opcode.LDI16 << 12) | (1 << 8), 0x1234,  # R1 = value to store
            (Opcode.ST << 12) | (0 << 8) | (1 << 4),  # ST [R0], R1
            (Opcode.LDI16 << 12) | (2 << 8), 0x2000,  # R2 = address again
            (Opcode.LD << 12) | (3 << 8) | (2 << 4),  # LD R3, [R2]
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0x1234,
        'desc': 'LD should load value from memory'
    })

    # Test 2: ST - Store register to memory
    # Store R1 value to address in R0, verify memory content
    tests.append({
        'name': 'ST (store to memory)',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x3000,  # R0 = address
            (Opcode.LDI16 << 12) | (1 << 8), 0x5678,  # R1 = value to store
            (Opcode.ST << 12) | (0 << 8) | (1 << 4),  # ST [R0], R1
            (Opcode.LDI16 << 12) | (2 << 8), 0x3000,  # R2 = address
            (Opcode.LD << 12) | (3 << 8) | (2 << 4),  # LD R3, [R2] (verify)
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[3] == 0x5678,
        'desc': 'ST should store register to memory'
    })

    # Test 3: LD with indirect addressing (R1 contains address)
    tests.append({
        'name': 'LD indirect',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x4000,  # R0 = address
            (Opcode.LDI16 << 12) | (1 << 8), 0x9ABC,  # R1 = value
            (Opcode.ST << 12) | (0 << 8) | (1 << 4),  # ST [R0], R1
            (Opcode.LDI16 << 12) | (2 << 8), 0x4000,  # R2 = address
            (Opcode.LDI16 << 12) | (3 << 8), 0x4000,  # R3 = address
            (Opcode.LD << 12) | (4 << 8) | (3 << 4),  # LD R4, [R3]
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[4] == 0x9ABC,
        'desc': 'LD should work with register-indirect addressing'
    })

    # Test 4: Memory persistence - write then read different address
    tests.append({
        'name': 'Memory persistence',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x5000,  # R0 = address1
            (Opcode.LDI16 << 12) | (1 << 8), 0xDEAD,  # R1 = value1
            (Opcode.ST << 12) | (0 << 8) | (1 << 4),  # ST [R0], R1
            (Opcode.LDI16 << 12) | (2 << 8), 0x6000,  # R2 = address2
            (Opcode.LDI16 << 12) | (3 << 8), 0xBEEF,  # R3 = value2
            (Opcode.ST << 12) | (2 << 8) | (3 << 4),  # ST [R2], R3
            (Opcode.LDI16 << 12) | (4 << 8), 0x5000,  # R4 = address1
            (Opcode.LD << 12) | (5 << 8) | (4 << 4),  # LD R5, [R4] (should be DEAD)
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[5] == 0xDEAD,
        'desc': 'Memory should persist values at different addresses'
    })

    # Test 5: ST with immediate address (using LDI16 first)
    tests.append({
        'name': 'ST then LD with same address',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x7000,  # R0 = address
            (Opcode.LDI16 << 12) | (1 << 8), 0xF00D,  # R1 = value
            (Opcode.ST << 12) | (0 << 8) | (1 << 4),  # ST [R0], R1
            (Opcode.LD << 12) | (2 << 8) | (0 << 4),  # LD R2, [R0] (read back)
            (Opcode.HALT << 12),
        ],
        'check': lambda regs: regs[2] == 0xF00D,
        'desc': 'ST then LD should return same value'
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
    test_memory_ops()

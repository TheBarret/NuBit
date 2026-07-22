# test_edge_cases.py
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

def test_edge_cases():
    tests = []

    # Test 1: ADD overflow (0xFFFF + 1 = 0x0000, carry=1)
    tests.append({
        'name': 'ADD overflow',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0xFFFF,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0001,
            (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.CARRY] == 1 and cpu.alu.flags[Flag.ZERO] == 1,
        'desc': '0xFFFF + 1 = 0x0000 with carry=1, zero=1'
    })

    # Test 2: SUB underflow (0x0000 - 1 = 0xFFFF, borrow=1)
    tests.append({
        'name': 'SUB underflow',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0000,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0001,
            (Opcode.SUB << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0xFFFF and cpu.alu.flags[Flag.CARRY] == 1,
        'desc': '0x0000 - 1 = 0xFFFF with borrow=1'
    })

    # Test 3: MUL overflow (0x0100 * 0x0100 = 0x0000 overflow=1)
    tests.append({
        'name': 'MUL overflow',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0100,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0100,
            (Opcode.MUL << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.OVERFLOW] == 1,
        'desc': '0x0100 * 0x0100 = 0x0000 with overflow=1'
    })

    # Test 4: ADD max (0x7FFF + 0x0001 = 0x8000, no overflow flag for add)
    tests.append({
        'name': 'ADD max positive',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x7FFF,
            (Opcode.LDI16 << 12) | (1 << 8), 0x0001,
            (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x8000 and cpu.alu.flags[Flag.ZERO] == 0,
        'desc': '0x7FFF + 1 = 0x8000'
    })

    # Test 5: Zero flag after ADD
    tests.append({
        'name': 'Zero flag ADD',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x1234,
            (Opcode.LDI16 << 12) | (1 << 8), 0xEDCC,  # 0x1234 + 0xEDCC = 0x0000
            (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.ZERO] == 1,
        'desc': '0x1234 + 0xEDCC = 0x0000 sets Z=1'
    })

    # Test 6: Zero flag after SUB
    tests.append({
        'name': 'Zero flag SUB',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x1234,
            (Opcode.LDI16 << 12) | (1 << 8), 0x1234,
            (Opcode.SUB << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.ZERO] == 1,
        'desc': '0x1234 - 0x1234 = 0x0000 sets Z=1'
    })

    # Test 7: Zero flag after MUL
    tests.append({
        'name': 'Zero flag MUL',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x0000,
            (Opcode.LDI16 << 12) | (1 << 8), 0xFFFF,
            (Opcode.MUL << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.ZERO] == 1,
        'desc': '0x0000 * 0xFFFF = 0x0000 sets Z=1'
    })

    # Test 8: Carry flag after ADD without overflow
    tests.append({
        'name': 'Carry flag ADD',
        'program': [
            (Opcode.LDI16 << 12) | (0 << 8), 0x8000,
            (Opcode.LDI16 << 12) | (1 << 8), 0x8000,
            (Opcode.ADD << 12) | (2 << 8) | (0 << 4) | 1,
            (Opcode.HALT << 12),
        ],
        'check': lambda cpu: cpu.regs[2] == 0x0000 and cpu.alu.flags[Flag.CARRY] == 1,
        'desc': '0x8000 + 0x8000 = 0x0000 with carry=1'
    })

    passed = 0
    for test in tests:
        cpu, mem = setup_cpu()
        regs, _ = run_program(cpu, mem, test['program'])

        # If check expects a CPU object, pass it, else use regs
        try:
            # Try to see if the check function expects cpu
            import inspect
            if inspect.signature(test['check']).parameters:
                # If it has parameters, pass cpu
                result = test['check'](cpu)
            else:
                result = test['check'](regs)
        except:
            # Fallback: try with regs
            result = test['check'](regs)

        status = "✓" if result else "✗"
        print(f"{status} {test['name']}: {test['desc']}")
        if not result:
            print(f"    Regs: R0={cpu.regs[0]:04X} R1={cpu.regs[1]:04X} R2={cpu.regs[2]:04X}")
            print(f"    Flags: Z={cpu.alu.flags[Flag.ZERO]} C={cpu.alu.flags[Flag.CARRY]} V={cpu.alu.flags[Flag.OVERFLOW]}")
        passed += result

    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    test_edge_cases()

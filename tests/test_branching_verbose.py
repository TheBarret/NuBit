# test_branching_verbose.py
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

def run_program_verbose(cpu, mem, program):
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)
    cpu.pc = 0x0100

    print("\nExecuting program...")
    print("=" * 60)
    cycles = 0
    while not cpu.halted and cycles < 30:
        pc_before = cpu.pc
        instruction = cpu.fetch()
        op, dest, src1, src2 = cpu.decode(instruction)

        print(f"Cycle {cycles:2d}: PC={pc_before:04X} IR={instruction:04X} OP={op:X} R{dest},R{src1},R{src2}")
        print(f"  Regs: R0={cpu.regs[0]:04X} R1={cpu.regs[1]:04X} R2={cpu.regs[2]:04X} R3={cpu.regs[3]:04X}")
        print(f"  Flags: Z={cpu.alu.flags[Flag.ZERO]} C={cpu.alu.flags[Flag.CARRY]} V={cpu.alu.flags[Flag.OVERFLOW]}")

        cpu.execute(instruction)
        cycles += 1

    print("=" * 60)
    print(f"Halted: {cpu.halted}, Cycles: {cycles}")
    return cpu.regs.copy(), cpu.alu.flags.copy()

def test_jmp_debug():
    print("=" * 60)
    print("JMP INSTRUCTION")

    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))
    cpu = CPU16(bus)

    program = [
        (Opcode.LDI16 << 12) | (0 << 8), 0x0106,  # R0=0x0106 (target LDI16)
        (Opcode.JMP << 12) | (0 << 4),             # JMP R0
        (Opcode.LDI16 << 12) | (3 << 8), 0xFFFF,  # Should be skipped
        (Opcode.HALT << 12),
        # Target at 0x0106
        (Opcode.LDI16 << 12) | (3 << 8), 0x1234,  # R3=0x1234
        (Opcode.HALT << 12),
    ]

    regs, _ = run_program_verbose(cpu, mem, program)
    print(f"\nFinal R3: {regs[3]:04X} (expected 0x1234)")
    print(f"Result: {'PASSED' if regs[3] == 0x1234 else 'FAILED'}")

if __name__ == "__main__":
    test_jmp_debug()

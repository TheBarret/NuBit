import numpy as np

from storage import UnifiedBus, Memory
from nubit2 import Adder, Subtractor, BitWiseLogic, SAMultiplier, Comparator


# ISA Definition

class Opcode:
    """Instruction set opcodes - single source of truth."""
    ADD  = 0x0  # ADD  Rd, Rs1, Rs2
    SUB  = 0x1  # SUB  Rd, Rs1, Rs2
    AND  = 0x2  # AND  Rd, Rs1, Rs2
    OR   = 0x3  # OR   Rd, Rs1, Rs2
    XOR  = 0x4  # XOR  Rd, Rs1, Rs2
    MUL  = 0x5  # MUL  Rd, Rs1, Rs2
    CMP  = 0x6  # CMP  Rs1, Rs2
    LDI  = 0x7  # LDI  Rd, imm4
    LDI16 = 0x8 # LDI16 Rd (next word is 16-bit immediate)
    LD   = 0x9  # LD   Rd, [Rs1]
    ST   = 0xA  # ST   [Rd], Rs1
    JMP  = 0xB  # JMP  Rs1
    JZ   = 0xC  # JZ   Rs1
    JNZ  = 0xD  # JNZ  Rs1
    HALT = 0xF  # HALT


class Flag:
    """ALU flag indices."""
    ZERO = 'zero'
    CARRY = 'carry'
    OVERFLOW = 'overflow'
    LESS = 'less'
    GREATER = 'greater'


# ALU

class ALU16:
    """
    16-bit ALU with parallel computation (authentic hardware model).
    All functional units fire every cycle; result selected by opcode.
    """

    def __init__(self):
        self.adder = Adder(16)
        self.subtractor = Subtractor(16)
        self.and_logic = BitWiseLogic(16, 'AND')
        self.or_logic = BitWiseLogic(16, 'OR')
        self.xor_logic = BitWiseLogic(16, 'XOR')
        self.multiplier = SAMultiplier(16)
        self.comparator = Comparator(16)

        self.flags = {
            Flag.ZERO: 0,
            Flag.CARRY: 0,
            Flag.OVERFLOW: 0,
            Flag.LESS: 0,
            Flag.GREATER: 0
        }

    def forward(self, A, B, op):
        """Execute ALU operation and update flags."""
        # Parallel computation (authentic)
        add_result, add_carry = self.adder.forward(A, B)
        sub_result, sub_borrow = self.subtractor.forward(A, B)
        and_result = self.and_logic.forward(A, B)
        or_result = self.or_logic.forward(A, B)
        xor_result = self.xor_logic.forward(A, B)

        mul_full = self.multiplier.forward(A, B)
        mul_result = mul_full & 0xFFFF
        mul_overflow = (mul_full >> 16) & 0xFFFF

        cmp_result = self.comparator.forward(A, B)

        # Result lookup table (replaces mux for clarity)
        results = {
            Opcode.ADD: add_result,
            Opcode.SUB: sub_result,
            Opcode.AND: and_result,
            Opcode.OR: or_result,
            Opcode.XOR: xor_result,
            Opcode.MUL: mul_result,
            Opcode.CMP: cmp_result['equal']
        }

        result = results.get(op, 0)

        # Reset flags
        self.flags = {f: 0 for f in self.flags}

        # Update flags
        self.flags[Flag.ZERO] = 1 if result == 0 else 0
        self.flags[Flag.CARRY] = add_carry if op == Opcode.ADD else (
            sub_borrow if op == Opcode.SUB else 0
        )
        self.flags[Flag.OVERFLOW] = 1 if op == Opcode.MUL and mul_overflow != 0 else 0
        self.flags[Flag.LESS] = cmp_result['less_than']
        self.flags[Flag.GREATER] = cmp_result['greater_than']

        return result


# CPU

class CPU16:
    """
    16-bit CPU with dispatch-table instruction execution.
    """

    def __init__(self, bus):
        self.bus = bus
        self.alu = ALU16()
        self.regs = [0] * 16
        self.pc = 0x0000
        self.halted = False

        # Build dispatch table
        self.dispatch = {
            Opcode.ADD:  self._op_add,
            Opcode.SUB:  self._op_sub,
            Opcode.AND:  self._op_and,
            Opcode.OR:   self._op_or,
            Opcode.XOR:  self._op_xor,
            Opcode.MUL:  self._op_mul,
            Opcode.CMP:  self._op_cmp,
            Opcode.LDI:  self._op_ldi,
            Opcode.LDI16: self._op_ldi16,
            Opcode.LD:   self._op_ld,
            Opcode.ST:   self._op_st,
            Opcode.JMP:  self._op_jmp,
            Opcode.JZ:   self._op_jz,
            Opcode.JNZ:  self._op_jnz,
            Opcode.HALT: self._op_halt,
        }

    # --- Bus Interface ---

    def read_memory(self, addr):
        """Read 16-bit value from memory via bus."""
        self.bus.addr = addr & 0xFFFF
        self.bus.rd = 1
        self.bus.wr = 0
        result = self.bus.tick()
        self.bus.rd = 0  # Reset to idle
        return result

    def write_memory(self, addr, data):
        """Write 16-bit value to memory via bus."""
        self.bus.addr = addr & 0xFFFF
        self.bus.data_out = data & 0xFFFF
        self.bus.wr = 1
        self.bus.rd = 0
        self.bus.tick()
        self.bus.wr = 0  # Reset to idle

    # --- Fetch/Execute ---

    def fetch(self):
        """Fetch instruction from memory."""
        if self.halted:
            return 0
        instruction = self.read_memory(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return instruction

    def decode(self, instruction):
        """Decode instruction into fields."""
        op = (instruction >> 12) & 0xF
        dest = (instruction >> 8) & 0xF
        src1 = (instruction >> 4) & 0xF
        src2 = instruction & 0xF
        return op, dest, src1, src2

    def execute(self, instruction):
        """Execute decoded instruction. Returns False if halted."""
        op, dest, src1, src2 = self.decode(instruction)
        handler = self.dispatch.get(op)

        if handler is None:
            print(f"  WARNING: Unknown opcode 0x{op:X}")
            return True

        return handler(dest, src1, src2)

    # --- Instruction Handlers ---

    def _op_alu(self, dest, src1, src2, opcode):
        """Generic ALU operation handler."""
        result = self.alu.forward(self.regs[src1], self.regs[src2], opcode)
        self.regs[dest] = result
        return True

    def _op_add(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.ADD)

    def _op_sub(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.SUB)

    def _op_and(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.AND)

    def _op_or(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.OR)

    def _op_xor(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.XOR)

    def _op_mul(self, dest, src1, src2):
        return self._op_alu(dest, src1, src2, Opcode.MUL)

    def _op_cmp(self, dest, src1, src2):
        """Compare - updates flags only, no result stored."""
        self.alu.forward(self.regs[src1], self.regs[src2], Opcode.CMP)
        return True

    def _op_ldi(self, dest, src1, src2):
        """Load 4-bit immediate."""
        self.regs[dest] = src2
        return True

    def _op_ldi16(self, dest, src1, src2):
        """Load 16-bit immediate (next word in memory)."""
        self.regs[dest] = self.read_memory(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return True

    def _op_ld(self, dest, src1, src2):
        """Load from memory address in register."""
        addr = self.regs[src1]
        self.regs[dest] = self.read_memory(addr)
        return True

    def _op_st(self, dest, src1, src2):
        """Store register to memory address in register."""
        addr = self.regs[dest]
        value = self.regs[src1]
        self.write_memory(addr, value)
        return True

    def _op_jmp(self, dest, src1, src2):
        """Unconditional jump."""
        self.pc = self.regs[src1]
        return True

    def _op_jz(self, dest, src1, src2):
        """Jump if zero flag set."""
        if self.alu.flags[Flag.ZERO] == 1:
            self.pc = self.regs[src1]
        return True

    def _op_jnz(self, dest, src1, src2):
        """Jump if zero flag not set."""
        if self.alu.flags[Flag.ZERO] == 0:
            self.pc = self.regs[src1]
        return True

    def _op_halt(self, dest, src1, src2):
        """Halt CPU."""
        self.halted = True
        return False

    # --- Main Loop ---

    def run(self, max_cycles=255, verbose=False):
        """Run CPU until halt or max_cycles reached."""
        cycles = 0
        running = True

        while running and cycles < max_cycles:
            instruction = self.fetch()

            if verbose:
                op, dest, src1, src2 = self.decode(instruction)
                print(f"  [{cycles:3d}] PC={self.pc-1:04X} IR={instruction:04X} "
                      f"OP={op:X} R{dest},R{src1},R{src2}  "
                      f"flags={self.alu.flags}")

            running = self.execute(instruction)
            cycles += 1

        return cycles

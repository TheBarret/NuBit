import numpy as np

from storage import UnifiedBus, Memory
from nubit2 import Adder, Subtractor, BitWiseLogic, SAMultiplier, Comparator, Mux

# Opcode Table
ALU_ADD  = 0 # ADD Rdest, Rsrc1, Rsrc2
ALU_SUB  = 1 # SUB Rdest, Rsrc1, Rsrc2
ALU_AND  = 2  # AND Rdest, Rsrc1, Rsrc2
ALU_OR   = 3 # OR  Rdest, Rsrc1, Rsrc2
ALU_XOR  = 4 # XOR Rdest, Rsrc1, Rsrc2
ALU_MUL  = 5 # MUL Rdest, Rsrc1, Rsrc2
ALU_CMP  = 6 # CMP Rsrc1, Rsrc2
ALU_LDI  = 7 # LDI Rdest, Immediate (4-bit)
ALU_LD   = 8 # LD  Rdest, [Rsrc1]
ALU_ST   = 9 # ST  [Rdest], Rsrc1
ALU_JMP  = 10 # JMP Rsrc1
ALU_JZ   = 11 # JZ  Rsrc1
ALU_JNZ  = 12 # JNZ Rsrc1
ALU_HALT = 15 # HALT

class ALU16:
    """
    16-bit ALU with 7 operations.
    """

    def __init__(self):
        # All components
        self.adder = Adder(16)
        self.subtractor = Subtractor(16)
        self.and_logic = BitWiseLogic(16, 'AND')
        self.or_logic = BitWiseLogic(16, 'OR')
        self.xor_logic = BitWiseLogic(16, 'XOR')
        self.multiplier = SAMultiplier(16) # handles overflow
        self.comparator = Comparator(16)
        self.mux = Mux(16, num_inputs=7)

        # global table
        self.OP_ADD = ALU_ADD
        self.OP_SUB = ALU_SUB
        self.OP_AND = ALU_AND
        self.OP_OR = ALU_OR
        self.OP_XOR = ALU_XOR
        self.OP_MUL = ALU_MUL
        self.OP_CMP = ALU_CMP

        # Flags
        self.flags = {'zero': 0, 'carry': 0, 'less': 0, 'greater': 0}

    def forward(self, A, B, op):
        # Compute all operations in parallel
        add_result, add_carry = self.adder.forward(A, B)
        sub_result, sub_borrow = self.subtractor.forward(A, B)
        and_result = self.and_logic.forward(A, B)
        or_result = self.or_logic.forward(A, B)
        xor_result = self.xor_logic.forward(A, B)

        # Multiplication: get full 32-bit result
        mul_result_full = self.multiplier.forward(A, B)
        mul_result = mul_result_full & 0xFFFF  # Lower 16 bits
        mul_overflow = (mul_result_full >> 16) & 0xFFFF  # Upper 16 bits

        cmp_result = self.comparator.forward(A, B)

        # Select the correct result
        results = [
            add_result,                    # 0: ADD
            sub_result,                    # 1: SUB
            and_result,                    # 2: AND
            or_result,                     # 3: OR
            xor_result,                    # 4: XOR
            mul_result,                    # 5: MUL (lower 16 bits)
            cmp_result['equal']            # 6: CMP
        ]

        result = self.mux.forward(results, op)

        # Update flags
        self.flags['zero'] = 1 if result == 0 else 0
        self.flags['carry'] = add_carry if op == self.OP_ADD else 0
        self.flags['overflow'] = 1 if op == self.OP_MUL and mul_overflow != 0 else 0
        self.flags['less'] = cmp_result['less_than']
        self.flags['greater'] = cmp_result['greater_than']

        return result

class CPU16:
    """16-bit CPU with bus and memory access."""

    def __init__(self, bus):
        self.bus = bus
        self.alu = ALU16()
        self.regs = [0] * 16
        self.pc = 0x0000
        self.ir = 0x0000
        self.state = 'FETCH'
        self.halted = False

        # For 16-bit mode, set bus to 16-bit
        self.bus.addr_width = 16
        self.bus.data_width = 16
        self.bus.addr_mask = 0xFFFF
        self.bus.data_mask = 0xFFFF

    def read_memory(self, addr):
        """Read 16-bit value from memory via bus."""
        self.bus.addr = addr & 0xFFFF
        self.bus.rd = 1
        self.bus.wr = 0
        return self.bus.tick()

    def write_memory(self, addr, data):
        """Write 16-bit value to memory via bus."""
        self.bus.addr = addr & 0xFFFF
        self.bus.data_out = data & 0xFFFF
        self.bus.wr = 1
        self.bus.rd = 0
        self.bus.tick()

    def fetch(self):
        """Fetch instruction from memory."""
        if self.halted:
            return 0
        instruction = self.read_memory(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return instruction

    def execute(self, instruction):
        op = (instruction >> 12) & 0xF
        dest = (instruction >> 8) & 0xF
        src1 = (instruction >> 4) & 0xF
        src2 = instruction & 0xF

        if op == ALU_ADD:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_ADD)
            self.regs[dest] = result

        elif op == ALU_SUB:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_SUB)
            self.regs[dest] = result

        elif op == ALU_AND:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_AND)
            self.regs[dest] = result

        elif op == ALU_OR:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_OR)
            self.regs[dest] = result

        elif op == ALU_XOR:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_XOR)
            self.regs[dest] = result

        elif op == ALU_MUL:
            result = self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_MUL)
            self.regs[dest] = result

        elif op == ALU_CMP:
            self.alu.forward(self.regs[src1], self.regs[src2], self.alu.OP_CMP)

        elif op == ALU_LDI:  # Load Immediate
            # Immediate value is in src2 (4 bits, 0-15)
            self.regs[dest] = src2

        elif op == ALU_LD:  # Load from Memory
            addr = self.regs[src1]
            value = self.read_memory(addr)
            self.regs[dest] = value

        elif op == ALU_ST:  # Store to Memory
            addr = self.regs[dest]
            value = self.regs[src1]
            self.write_memory(addr, value)

        elif op == ALU_JMP:
            self.pc = self.regs[src1]

        elif op == ALU_JZ:
            if self.alu.flags['zero'] == 1:
                self.pc = self.regs[src1]

        elif op == ALU_JNZ:
            if self.alu.flags['zero'] == 0:
                self.pc = self.regs[src1]

        elif op == ALU_HALT:
            self.halted = True
            return False

        return True

    def run(self, max_cycles=255):
        """Run program."""
        instruction = 0
        cycles = 0
        running = True
        while running and cycles < max_cycles:
            instruction = self.fetch()
            running = self.execute(instruction)
            cycles += 1
            print(f"fetch: {instruction}, running: {running}, cycles: {cycles}")

        return cycles

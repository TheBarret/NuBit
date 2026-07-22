import numpy as np

from storage import UnifiedBus
from nubit2 import Adder, Subtractor, BitWiseLogic, SAMultiplier, Comparator, Mux

### 16bit ALU
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

        # Opcode Table
        self.OP_ADD = 0
        self.OP_SUB = 1
        self.OP_AND = 2
        self.OP_OR = 3
        self.OP_XOR = 4
        self.OP_MUL = 5
        self.OP_CMP = 6

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

### 16bit CPU

class CPU16:
    """CPU16 with bus and memory access."""

    def __init__(self, bus: UnifiedBus):
        self.bus = bus
        self.alu = ALU16()
        self.regs = [0] * 16  # 16 registers
        self.pc = 0x0000      # Program counter
        self.ir = 0x0000      # Instruction register
        self.state = 'FETCH'

        # Memory-mapped I/O addresses
        self.IO_CONSOLE = 0xFFFF
        self.IO_KEYBOARD = 0xFFFE

    def read_memory(self, addr):
        """Read 16-bit value from memory via bus."""
        self.bus.addr = addr
        self.bus.rd = 1
        self.bus.wr = 0
        self.bus.tick()
        return self.bus.data_in

    def write_memory(self, addr, data):
        """Write 16-bit value to memory via bus."""
        self.bus.addr = addr
        self.bus.data_out = data & 0xFFFF
        self.bus.wr = 1
        self.bus.rd = 0
        self.bus.tick()

    def fetch(self):
        """Fetch instruction from memory using bus."""
        instruction = self.read_memory(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return instruction

    def execute(self, instruction):
        """Decode and execute instruction."""
        op = (instruction >> 12) & 0xF
        dest = (instruction >> 8) & 0xF
        src1 = (instruction >> 4) & 0xF
        src2 = instruction & 0xF

        # Instruction set
        if op == 0:  # ADD Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_ADD
            )
            self.regs[dest] = result

        elif op == 1:  # SUB Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_SUB
            )
            self.regs[dest] = result

        elif op == 2:  # AND Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_AND
            )
            self.regs[dest] = result

        elif op == 3:  # OR Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_OR
            )
            self.regs[dest] = result

        elif op == 4:  # XOR Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_XOR
            )
            self.regs[dest] = result

        elif op == 5:  # MUL Rdest, Rsrc1, Rsrc2
            result = self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_MUL
            )
            self.regs[dest] = result

        elif op == 6:  # CMP Rsrc1, Rsrc2 (sets flags only)
            self.alu.forward(
                self.regs[src1],
                self.regs[src2],
                self.alu.OP_CMP
            )

        elif op == 7:  # LOAD Rdest, [Rsrc1]  (load from memory)
            addr = self.regs[src1]
            value = self.read_memory(addr)
            self.regs[dest] = value

        elif op == 8:  # STORE [Rdest], Rsrc1  (store to memory)
            addr = self.regs[dest]
            value = self.regs[src1]
            self.write_memory(addr, value)

        elif op == 9:  # JMP Rsrc1  (jump to address in register)
            self.pc = self.regs[src1]

        elif op == 10:  # JZ Rsrc1  (jump if zero flag is set)
            if self.alu.flags['zero'] == 1:
                self.pc = self.regs[src1]

        elif op == 11:  # JNZ Rsrc1  (jump if zero flag is not set)
            if self.alu.flags['zero'] == 0:
                self.pc = self.regs[src1]

        elif op == 12:  # HALT
            return False

        return True

    def run(self, max_cycles=10000):
        """Run the CPU for max_cycles instructions."""
        cycles = 0
        running = True

        while running and cycles < max_cycles:
            instruction = self.fetch()
            running = self.execute(instruction)
            cycles += 1

        return cycles

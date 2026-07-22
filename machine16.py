import numpy as np

from nubit2 import Adder, Subtractor, BitWiseLogic, SAMultiplier, Comparator, Mux

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

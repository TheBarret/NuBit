# NuBit 1.0

import numpy as np

# ==================== ATOM ====================

class Gate:
    def __init__(self, gate_type='AND'):
        self.gate_type = gate_type

        # truth tables
        if gate_type == 'AND':
            self.w1, self.w2, self.bias = 1.0, 1.0, -1.5
        elif gate_type == 'OR':
            self.w1, self.w2, self.bias = 1.0, 1.0, -0.5
        elif gate_type == 'NAND':
            self.w1, self.w2, self.bias = -1.0, -1.0, 1.5
        elif gate_type == 'NOR':
            self.w1, self.w2, self.bias = -1.0, -1.0, 0.5
        elif gate_type == 'NOT':
            self.w1, self.w2, self.bias = -1.0, 0.0, 0.5
        else:
            self.w1, self.w2, self.bias = 1.0, 1.0, -1.5
            
    def sigmoid(self, x, steepness=10):
        return 1.0 / (1.0 + np.exp(-steepness * x))
    
    def forward(self, x1, x2=0.0):
        if self.gate_type == 'NOT':
            linear = self.w1 * x1 + self.bias
        else:
            linear = self.w1 * x1 + self.w2 * x2 + self.bias
        return self.sigmoid(linear)
    
    def predict_binary(self, x1, x2=0.0):
        return 1.0 if self.forward(x1, x2) > 0.5 else 0.0
    
    def discretize(self, inputs, targets):
        # Preserve sign of weights
        self.w1 = 1.0 if self.w1 > 0.5 else (-1.0 if self.w1 < -0.5 else 0.0)
        self.w2 = 1.0 if self.w2 > 0.5 else (-1.0 if self.w2 < -0.5 else 0.0)
        
        # For gates that need negative weights
        if self.gate_type in ['NAND', 'NOR']:
            self.w1 = -1.0
            self.w2 = -1.0
        elif self.gate_type == 'NOT':
            self.w1 = -1.0
            self.w2 = 0.0
        
        best_bias = None
        best_score = float('inf')
        for bias_candidate in np.arange(-3.0, 3.1, 0.1):
            self.bias = bias_candidate
            errors = 0
            for i in range(len(inputs)):
                if self.gate_type == 'NOT':
                    pred = self.predict_binary(inputs[i][0])
                else:
                    pred = self.predict_binary(inputs[i][0], inputs[i][1])
                errors += (pred - targets[i]) ** 2
            if errors < best_score:
                best_score = errors
                best_bias = bias_candidate
        if best_bias is not None:
            self.bias = best_bias
        return self

# ==================== MACROS ====================

# HALF ADDER

class HalfAdder:
    def __init__(self):
        self.xor = TwoLayerXOR()
        self.and_gate = Gate('AND')
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        targets = np.array([0, 0, 0, 1])
        self.and_gate.discretize(inputs, targets)
    
    def forward(self, a, b):
        return self.xor.forward(a, b), self.and_gate.predict_binary(a, b)

# TL-XOR

class TwoLayerXOR:
    def __init__(self):
        self.nand = Gate('NAND')
        self.or_gate = Gate('OR')
        self.and_gate = Gate('AND')
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        
        self.nand.discretize(inputs, np.array([1, 1, 1, 0]))
        self.or_gate.discretize(inputs, np.array([0, 1, 1, 1]))
        self.and_gate.discretize(inputs, np.array([0, 0, 0, 1]))
    
    def forward(self, a, b):
        return self.and_gate.predict_binary(
            self.nand.predict_binary(a, b),
            self.or_gate.predict_binary(a, b)
        )

# FULL ADDER

class FullAdder:
    def __init__(self):
        self.ha1 = HalfAdder()
        self.ha2 = HalfAdder()
        self.or_gate = Gate('OR')
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        targets = np.array([0, 1, 1, 1])
        self.or_gate.discretize(inputs, targets)
    
    def forward(self, a, b, cin):
        s1, c1 = self.ha1.forward(a, b)
        s2, c2 = self.ha2.forward(s1, cin)
        cout = self.or_gate.predict_binary(c1, c2)
        return s2, cout


# 4-BIT ADDER

class FourBitAdder:
    def __init__(self):
        self.fa0 = FullAdder()
        self.fa1 = FullAdder()
        self.fa2 = FullAdder()
        self.fa3 = FullAdder()
    
    def forward(self, a, b):
        """Add two 4-bit integers (0-15). Returns 5-bit result (sum + carry)."""
        # Extract bits
        a_bits = [(a >> i) & 1 for i in range(4)]
        b_bits = [(b >> i) & 1 for i in range(4)]
        
        # Chain full-adders
        s0, c0 = self.fa0.forward(a_bits[0], b_bits[0], 0)
        s1, c1 = self.fa1.forward(a_bits[1], b_bits[1], c0)
        s2, c2 = self.fa2.forward(a_bits[2], b_bits[2], c1)
        s3, c3 = self.fa3.forward(a_bits[3], b_bits[3], c2)
        
        # Reconstruct result - cast to int to handle float returns
        result = int(s0) + (int(s1) << 1) + (int(s2) << 2) + (int(s3) << 3) + (int(c3) << 4)
        return result

# N-BIT ADDER

class NBitAdder:
    """N-bit ripple-carry adder."""
    def __init__(self, bits=8):
        self.bits = bits
        self.adders = [FullAdder() for _ in range(bits)]
    
    def forward(self, a, b):
        a_bits = [(a >> i) & 1 for i in range(self.bits)]
        b_bits = [(b >> i) & 1 for i in range(self.bits)]
        
        result = 0
        carry = 0
        
        for i in range(self.bits):
            s, carry = self.adders[i].forward(a_bits[i], b_bits[i], carry)
            result |= (int(s) << i)
        
        result |= (int(carry) << self.bits)
        return result


# N-BIT SUBTRACTOR

class NBitSubtractor:
    """N-bit subtractor using two's complement: A - B = A + (~B + 1)."""
    def __init__(self, bits=8):
        self.bits = bits
        self.adder = NBitAdder(bits)
        self.not_gates = [Gate('NOT') for _ in range(bits)]
        
        # Discretize NOT gates
        inputs = np.array([[0], [1]])
        targets = np.array([1, 0])
        for gate in self.not_gates:
            gate.discretize(inputs, targets)
    
    def forward(self, a, b):
        # Step 1: Invert B bit-by-bit using NOT gates
        b_inv = 0
        for i in range(self.bits):
            bit = (b >> i) & 1
            inv_bit = int(self.not_gates[i].predict_binary(bit))
            b_inv |= (inv_bit << i)
        
        # Step 2: Add 1 to inverted B (two's complement)
        # Use a simple ripple-carry increment
        b_twos_comp = 0
        carry = 1
        for i in range(self.bits):
            bit = (b_inv >> i) & 1
            sum_bit = bit ^ carry
            carry = bit & carry
            b_twos_comp |= (sum_bit << i)
        
        # Step 3: Add A + (~B + 1)
        result = self.adder.forward(a, b_twos_comp)
        
        # Mask to N bits (ignore overflow carry)
        mask = (1 << self.bits) - 1
        return result & mask


# N-BIT COMPARATOR 

class NBitComparator:
    """N-bit comparator: equality, less-than, greater-than."""
    def __init__(self, bits=8):
        self.bits = bits
        self.xor_gates = [TwoLayerXOR() for _ in range(bits)]
        self.and_gate = Gate('AND')
        self.or_gate = Gate('OR')
        self.not_gate = Gate('NOT')
        
        # Discretize gates
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        self.and_gate.discretize(inputs, np.array([0, 0, 0, 1]))
        self.or_gate.discretize(inputs, np.array([0, 1, 1, 1]))
        inputs_not = np.array([[0], [1]])
        self.not_gate.discretize(inputs_not, np.array([1, 0]))
    
    def forward(self, a, b):
        """Returns (equal, less_than, greater_than)."""
        # Check equality: all bits equal
        equal = 1
        for i in range(self.bits):
            a_bit = (a >> i) & 1
            b_bit = (b >> i) & 1
            xor_out = self.xor_gates[i].forward(a_bit, b_bit)
            if xor_out == 1:
                equal = 0
        
        # Find most significant differing bit
        less_than = 0
        greater_than = 0
        
        for i in range(self.bits - 1, -1, -1):
            a_bit = (a >> i) & 1
            b_bit = (b >> i) & 1
            
            if a_bit != b_bit:
                if a_bit == 0 and b_bit == 1:
                    less_than = 1
                else:
                    greater_than = 1
                break
        
        return {
            'equal': equal,
            'less_than': less_than,
            'greater_than': greater_than
        }


# N-BIT MULTIPLIER 

class NBitMultiplier:
    """N-bit multiplier using shift-and-add. Result is 2×bits bits."""
    def __init__(self, bits=8):
        self.bits = bits
        self.adder = NBitAdder(bits * 2)  # Need double width for result
        self.and_gate = Gate('AND')
        
        # Discretize AND gate
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        targets = np.array([0, 0, 0, 1])
        self.and_gate.discretize(inputs, targets)
    
    def forward(self, a, b):
        result = 0
        for i in range(self.bits):
            if (b >> i) & 1:
                shifted = a << i
                result = self.adder.forward(result, shifted)
        return result


# N-BIT ALU 
class NBitALU:
    """N-bit ALU: ADD, SUB, AND, OR, XOR, MUL, CMP."""
    def __init__(self, bits=8):
        self.bits = bits
        self.adder = NBitAdder(bits)
        self.subtractor = NBitSubtractor(bits)
        self.comparator = NBitComparator(bits)
        self.multiplier = NBitMultiplier(bits)
        self.and_logic = NBitLogic(bits, 'AND')
        self.or_logic = NBitLogic(bits, 'OR')
        self.xor_logic = NBitLogic(bits, 'XOR')
        self.mux = NBitMux(bits, num_inputs=7)  # 7 operations
    
    def forward(self, a, b, op):
        """
        op: 0=ADD, 1=SUB, 2=AND, 3=OR, 4=XOR, 5=MUL, 6=CMP
        """
        results = [
            self.adder.forward(a, b),
            self.subtractor.forward(a, b),
            self.and_logic.forward(a, b),
            self.or_logic.forward(a, b),
            self.xor_logic.forward(a, b),
            self.multiplier.forward(a, b),
            self.comparator.forward(a, b)['equal']  # Return equal flag for simplicity
        ]
        return self.mux.forward(results, op)


# HELPERS 

class NBitLogic:
    """N-bit bitwise logic gate."""
    def __init__(self, bits=8, gate_type='AND'):
        self.bits = bits
        self.gate_type = gate_type
        
        # XOR needs 2 layers, others need 1
        if gate_type == 'XOR':
            self.gates = [TwoLayerXOR() for _ in range(bits)]
        else:
            self.gates = [Gate(gate_type) for _ in range(bits)]
            
            # Discretize each gate
            inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
            if gate_type == 'AND':
                targets = np.array([0, 0, 0, 1])
            elif gate_type == 'OR':
                targets = np.array([0, 1, 1, 1])
            else:
                targets = np.array([0, 0, 0, 1])
            
            for gate in self.gates:
                gate.discretize(inputs, targets)
    
    def forward(self, a, b):
        result = 0
        for i in range(self.bits):
            a_bit = (a >> i) & 1
            b_bit = (b >> i) & 1
            
            if self.gate_type == 'XOR':
                out = self.gates[i].forward(a_bit, b_bit)
            else:
                out = self.gates[i].predict_binary(a_bit, b_bit)
            
            result |= (int(out) << i)
        return result


class NBitMux:
    """N-bit multiplexer: selects one of 2^sel inputs."""
    def __init__(self, bits=8, num_inputs=4):
        self.bits = bits
        self.num_inputs = num_inputs
        self.and_gates = [[Gate('AND') for _ in range(bits)] for _ in range(num_inputs)]
        self.or_gates = [Gate('OR') for _ in range(bits)]
        
        # Discretize gates
        inputs = np.array([[0,0], [0,1], [1,0], [1,1]])
        self.and_gate_template = Gate('AND')
        self.and_gate_template.discretize(inputs, np.array([0, 0, 0, 1]))
        self.or_gate_template = Gate('OR')
        self.or_gate_template.discretize(inputs, np.array([0, 1, 1, 1]))
        
        # Copy weights to all gates
        for i in range(num_inputs):
            for j in range(bits):
                self.and_gates[i][j].w1 = self.and_gate_template.w1
                self.and_gates[i][j].w2 = self.and_gate_template.w2
                self.and_gates[i][j].bias = self.and_gate_template.bias
        for j in range(bits):
            self.or_gates[j].w1 = self.or_gate_template.w1
            self.or_gates[j].w2 = self.or_gate_template.w2
            self.or_gates[j].bias = self.or_gate_template.bias
    
    def forward(self, inputs, select):
        """
        inputs: list of N-bit numbers (length = num_inputs)
        select: integer (0 to num_inputs-1)
        """
        # For each bit position, OR together all selected inputs
        result = 0
        for bit in range(self.bits):
            # Collect all AND outputs for this bit
            and_outputs = []
            for i in range(self.num_inputs):
                input_bit = (inputs[i] >> bit) & 1
                # AND with select line (only one select line is 1)
                select_bit = 1 if i == select else 0
                and_out = self.and_gates[i][bit].predict_binary(input_bit, select_bit)
                and_outputs.append(and_out)
            
            # OR all AND outputs together
            # For simplicity, cascade OR gates
            if self.num_inputs == 1:
                result_bit = and_outputs[0]
            else:
                result_bit = and_outputs[0]
                for i in range(1, self.num_inputs):
                    result_bit = self.or_gates[bit].predict_binary(result_bit, and_outputs[i])
            
            result |= (int(result_bit) << bit)
        
        return result


# TESTER

if __name__ == "__main__":
    print("N-BIT ALU TEST")

    bits = 4
    alu = NBitALU(bits)

    test_cases = [
        (5, 3, 0, 8),   # ADD
        (5, 3, 1, 2),   # SUB (5-3=2)
        (5, 3, 2, 1),   # AND (5&3=1)
        (5, 3, 3, 7),   # OR  (5|3=7)
        (5, 3, 4, 6),   # XOR (5^3=6)
        (3, 4, 5, 12),  # MUL (3*4=12)
        (5, 5, 6, 1),   # CMP (5==5 => equal=1)
        (5, 6, 6, 0),   # CMP (5==6 => equal=0)
    ]

    print("\nALU Output:")
    for a, b, op, expected in test_cases:
        result = alu.forward(a, b, op)
        status = "✓" if result == expected else "✗"
        print(f"  op={op}: {a} {['+','-','&','|','^','*','=='][op]} {b} = {result} (expected {expected}) {status}")
        print("-" * 50)

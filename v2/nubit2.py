# nubit2.py

### Gates (Vectorized AND/OR/AND/XOR)

import numpy as np

class Gate:
    """
    Vectorized logic gate using NumPy.
    Supports batch operations for speed.
    """

    def __init__(self, w1=1.0, w2=1.0, bias=-1.5):
        self.W = np.array([[w1, w2]])
        self.bias = np.array([bias])

    def forward(self, x1, x2):
        x1 = np.asarray(x1).reshape(-1, 1)
        x2 = np.asarray(x2).reshape(-1, 1)

        # DEBUG
        assert x1.shape == x2.shape, f"shape mismatch: x1={x1.shape} x2={x2.shape}"

        inputs = np.hstack([x1, x2])
        linear = np.dot(inputs, self.W.T) + self.bias
        return np.where(linear > 0, 1, 0).flatten()

    def forward_single(self, x1, x2):
        """Forward pass for single scalar inputs (convenience)."""
        return int(self.forward(np.array([x1]), np.array([x2]))[0])

class AND(Gate):
    """AND gate: output = A & B"""
    def __init__(self):
        super().__init__(w1=1.0, w2=1.0, bias=-1.5)


class OR(Gate):
    """OR gate: output = A | B"""
    def __init__(self):
        super().__init__(w1=1.0, w2=1.0, bias=-0.5)


class NAND(Gate):
    """NAND gate: output = ~(A & B)"""
    def __init__(self):
        super().__init__(w1=-1.0, w2=-1.0, bias=1.5)


class NOR(Gate):
    """NOR gate: output = ~(A | B)"""
    def __init__(self):
        super().__init__(w1=-1.0, w2=-1.0, bias=0.5)


class NOT(Gate):
    """NOT gate: output = ~A"""
    def __init__(self):
        super().__init__(w1=-1.0, w2=0.0, bias=0.5)

    def forward(self, x):
        """Override for single input."""
        x = np.asarray(x).reshape(-1, 1)
        linear = np.dot(x, self.W[:, 0].reshape(1, -1)) + self.bias
        return np.where(linear > 0, 1, 0).flatten()

    def forward_single(self, x):
        return int(self.forward(np.array([x]))[0])

class XOR(Gate):
    """XOR gate: output = A ^ B (vectorized)."""

    def __init__(self):
        self.or_gate = OR()
        self.nand_gate = NAND()
        self.and_gate = AND()

    def forward(self, x1, x2):
        """
        Vectorized forward pass.
        XOR = (A OR B) AND (A NAND B)
        """
        # Ensure numpy arrays
        x1 = np.asarray(x1)
        x2 = np.asarray(x2)

        # If one is scalar, broadcast to match the other
        if x1.ndim == 0 and x2.ndim > 0:
            x1 = np.full_like(x2, x1.item())
        elif x2.ndim == 0 and x1.ndim > 0:
            x2 = np.full_like(x1, x2.item())

        # XOR = (A OR B) AND (A NAND B)
        or_out = self.or_gate.forward(x1, x2)
        nand_out = self.nand_gate.forward(x1, x2)
        return self.and_gate.forward(or_out, nand_out)

    def forward_single(self, x1, x2):
        """Forward pass for scalar inputs."""
        if hasattr(x1, 'item'):
            x1 = x1.item()
        if hasattr(x2, 'item'):
            x2 = x2.item()
        return int(self.forward(np.array([x1]), np.array([x2]))[0])

### Adder - Carry Look Ahead (Vectorized/Kogge-Stone parallel prefix)

class Adder:
    def __init__(self, bits=4):
        self.bits = bits
        self.and_gate = AND()
        self.or_gate = OR()
        self.xor_gate = XOR()
        self.expected_width = bits

    def _compute_generate_propagate(self, A, B):
        """Compute G and P for all bits in parallel."""
        G = self.and_gate.forward(A, B)
        P = self.xor_gate.forward(A, B)
        return G, P

    def _compute_carries_kogge_stone(self, G, P, cin=0):
        """
        O(log N) carry computation using Kogge-Stone parallel prefix.
        Pure NumPy—no gate object overhead.
        """
        N = len(G)

        G = np.asarray(G, dtype=int)
        P = np.asarray(P, dtype=int)

        G_out = G.copy()
        P_out = P.copy()

        # Inject carry-in
        G_out[0] = G[0] | (P[0] & cin)

        stride = 1
        while stride < N:
            idx = slice(stride, N)
            prev_idx = slice(0, N - stride)

            # Vectorized black cell (pure NumPy)
            G_out[idx] = G_out[idx] | (P_out[idx] & G_out[prev_idx])
            P_out[idx] = P_out[idx] & P_out[prev_idx]

            stride <<= 1

        carries = np.zeros(N + 1, dtype=int)
        carries[0] = cin
        carries[1:] = G_out

        return carries

    def forward(self, A, B, cin=0):
        # Convert inputs to bit arrays
        if isinstance(A, (int, np.integer)):
            A_bits = np.array([(A >> i) & 1 for i in range(self.bits)])
        else:
            A_bits = np.asarray(A)

        if isinstance(B, (int, np.integer)):
            B_bits = np.array([(B >> i) & 1 for i in range(self.bits)])
        else:
            B_bits = np.asarray(B)

        # Compute G and P in parallel
        G, P = self._compute_generate_propagate(A_bits, B_bits)

        # Assert expected width
        assert len(G) == self.bits, f"G length {len(G)} != {self.bits}"
        assert len(P) == self.bits, f"P length {len(P)} != {self.bits}"

        # Compute carries using Kogge-Stone (O(log N))
        carries = self._compute_carries_kogge_stone(G, P, cin)

        # Sum = P ^ C
        #S = np.zeros(self.bits, dtype=int)
        S = self.xor_gate.forward(P, carries[:-1])

        # Ensure integer type
        S = S.astype(int)

        # Construct result data
        result = 0
        for i in range(self.bits):
            result |= int(S[i]) << i
        result |= int(carries[self.bits]) << self.bits

        return result, int(carries[self.bits])

### Subtractor

class Subtractor:
    """N-bit subtractor using two's complement."""

    def __init__(self, bits=16):
        self.bits = bits
        self.not_gate = NOT()
        self.adder = Adder(bits)
        self.mask = (1 << bits) - 1
        self.expected_width = bits

    def forward(self, A, B):
        """
        A - B using two's complement.

        A, B: integers (0 to 2^bits - 1)
        Returns: (result, borrow_out)
        """
        # Ensure inputs are within bit width
        A = A & self.mask
        B = B & self.mask

        # Convert to bit arrays
        A_bits = np.array([(A >> i) & 1 for i in range(self.bits)])
        B_bits = np.array([(B >> i) & 1 for i in range(self.bits)])

        # Two's complement of B: ~B + 1
        B_inv = self.not_gate.forward(B_bits)
        B_neg, _ = self.adder.forward(B_inv, 1)

        # A - B = A + (-B)
        result, carry = self.adder.forward(A, B_neg)

        # Mask result to bit width
        result = result & self.mask

        # Borrow is inverse of carry (carry=1 means no borrow)
        borrow = 0 if carry else 1

        return result, borrow

### Multiplier

class Multiplier:
    """
    N-bit multiplier using shift-and-add.
    Output is 2×bits bits (product can be up to 2N bits).
    """

    def __init__(self, bits=16):
        self.bits = bits
        self.and_gate = AND()
        # Need 2×bits adder for full product
        self.adder = Adder(bits * 2)
        self.expected_width = bits
        self.mask = (1 << bits) - 1

    def forward(self, A, B):
        """
        A × B using shift-and-add.

        A, B: integers (0 to 2^bits - 1)
        Returns: integer (0 to 2^(2*bits) - 1)
        """
        # Mask inputs to bit width
        A = A & self.mask
        B = B & self.mask

        result = 0

        for i in range(self.bits):
            # Check if bit i of B is set
            if (B >> i) & 1:
                # Add shifted A to result
                shifted = A << i
                result = self.adder.forward(result, shifted)[0]

        return result

class SAMultiplier:
    """
    N-bit multiplier using shift-and-add.
    Returns full 2×bits product.
    """

    def __init__(self, bits=16):
        self.bits = bits
        self.and_gate = AND()
        # Need 2×bits adder for full product
        self.adder = Adder(bits * 2)
        self.expected_width = bits
        self.mask = (1 << bits) - 1
        self.full_mask = (1 << (bits * 2)) - 1

    def forward(self, A, B):
        """
        A × B using shift-and-add.

        A, B: integers (0 to 2^bits - 1)
        Returns: integer (0 to 2^(2*bits) - 1)
        """
        # Mask inputs to bit width
        A = A & self.mask
        B = B & self.mask

        result = 0

        # Perform shift-and-add multiplication
        for i in range(self.bits):
            # Check if bit i of B is set
            if (B >> i) & 1:
                # Add shifted A to result
                shifted = A << i
                result = self.adder.forward(result, shifted)[0]

        # Mask to full width (2×bits)
        result = result & self.full_mask

        return result

### Bitwise Logic

class BitWiseLogic:
    """
    N-bit bitwise logic operations.
    Uses the same vectorized pattern as CarryLookaheadAdder.
    """
    def __init__(self, bits=16, gate_type='AND'):
        self.bits = bits
        self.gate_type = gate_type

        if gate_type == 'AND':
            self.gate = AND()
        elif gate_type == 'OR':
            self.gate = OR()
        elif gate_type == 'XOR':
            self.gate = XOR()
        else:
            raise ValueError(f"Unknown gate type: {gate_type}")

        # Pre-compute powers of 2 for fast reconstruction
        self.powers = 1 << np.arange(bits)
        self.expected_width = bits

    def forward(self, A, B):
        # Convert inputs to bit arrays
        if isinstance(A, (int, np.integer)):
            A_bits = np.array([(A >> i) & 1 for i in range(self.bits)])
        else:
            A_bits = np.asarray(A)

        if isinstance(B, (int, np.integer)):
            B_bits = np.array([(B >> i) & 1 for i in range(self.bits)])
        else:
            B_bits = np.asarray(B)

        # Assert expected width
        assert len(A_bits) == self.bits, f"A length {len(A_bits)} != {self.bits}"
        assert len(B_bits) == self.bits, f"B length {len(B_bits)} != {self.bits}"

        # Vectorized gate operation
        result_bits = self.gate.forward(A_bits, B_bits)

        # Vectorized reconstruction (no loop)
        result = int(np.dot(result_bits.astype(int), self.powers))

        return result

### Comparator

class ComparatorBroken:
    """
    N-bit comparator.
    Returns: equal, less_than, greater_than flags.
    """

    def __init__(self, bits=16):
        self.bits = bits
        self.xor_gate = XOR()
        self.and_gate = AND()
        self.or_gate = OR()
        self.not_gate = NOT()
        self.expected_width = bits

    def forward(self, A, B):
        """
        Compare A and B.

        A, B: integers (0 to 2^bits - 1)
        Returns: dict with 'equal', 'less_than', 'greater_than'
        """
        # Convert inputs to bit arrays
        if isinstance(A, (int, np.integer)):
            A_bits = np.array([(A >> i) & 1 for i in range(self.bits)])
        else:
            A_bits = np.asarray(A)

        if isinstance(B, (int, np.integer)):
            B_bits = np.array([(B >> i) & 1 for i in range(self.bits)])
        else:
            B_bits = np.asarray(B)

        # Assert expected width
        assert len(A_bits) == self.bits, f"A length {len(A_bits)} != {self.bits}"
        assert len(B_bits) == self.bits, f"B length {len(B_bits)} != {self.bits}"

        # ---------- EQUALITY ----------
        # XOR all bits: if any bit differs, XOR = 1
        xor_results = self.xor_gate.forward(A_bits, B_bits)

        # OR all XOR results: if any 1, not equal
        # Build OR tree (vectorized)
        equal = 1
        for i in range(self.bits):
            if xor_results[i] == 1:
                equal = 0
                break

        # ---------- LESS-THAN ----------
        # Find most significant bit where A and B differ
        less_than = 0
        for i in range(self.bits - 1, -1, -1):
            a_bit = A_bits[i]
            b_bit = B_bits[i]

            if a_bit != b_bit:
                if a_bit == 0 and b_bit == 1:
                    less_than = 1
                break

        # ---------- GREATER-THAN ----------
        greater_than = 1 if not equal and not less_than else 0

        return {
            'equal': equal,
            'less_than': less_than,
            'greater_than': greater_than
        }


class Comparator:
    """
    N-bit comparator.
    Returns: equal, less_than, greater_than flags.
    """

    def __init__(self, bits=16):
        self.bits = bits
        self.xor_gate = XOR()
        self.and_gate = AND()
        self.or_gate = OR()
        self.not_gate = NOT()
        self.expected_width = bits

    def forward(self, A, B):
        """
        Compare A and B.

        A, B: integers (0 to 2^bits - 1)
        Returns: dict with 'equal', 'less_than', 'greater_than'
        """
        # Convert inputs to bit arrays
        if isinstance(A, (int, np.integer)):
            A_bits = np.array([(A >> i) & 1 for i in range(self.bits)])
        else:
            A_bits = np.asarray(A)

        if isinstance(B, (int, np.integer)):
            B_bits = np.array([(B >> i) & 1 for i in range(self.bits)])
        else:
            B_bits = np.asarray(B)

        # Assert expected width
        assert len(A_bits) == self.bits, f"A length {len(A_bits)} != {self.bits}"
        assert len(B_bits) == self.bits, f"B length {len(B_bits)} != {self.bits}"

        # ---------- EQUALITY ----------
        xor_results = self.xor_gate.forward(A_bits, B_bits)

        equal = 1
        for i in range(self.bits):
            if xor_results[i] == 1:
                equal = 0
                break

        # ---------- LESS-THAN & GREATER-THAN ----------
        # Find most significant bit where A and B differ
        less_than = 0
        greater_than = 0

        # Start from MSB to LSB
        for i in range(self.bits - 1, -1, -1):
            a_bit = A_bits[i]
            b_bit = B_bits[i]

            if a_bit != b_bit:
                if a_bit == 0 and b_bit == 1:
                    less_than = 1
                else:  # a_bit == 1 and b_bit == 0
                    greater_than = 1
                break  # Found MSB difference, stop

        # FIX: If equal, both should be 0
        if equal == 1:
            less_than = 0
            greater_than = 0

        return {
            'equal': equal,
            'less_than': less_than,
            'greater_than': greater_than
        }

### Multiplexer

class Mux:
    """
    N-bit multiplexer.
    Selects one of num_inputs inputs based on select signal.
    """

    def __init__(self, bits=16, num_inputs=4):
        self.bits = bits
        self.num_inputs = num_inputs
        self.and_gate = AND()
        self.or_gate = OR()

        # Pre-compute select lines (binary to one-hot)
        self.select_mask = (1 << bits) - 1

    def forward(self, inputs, select):
        """
        Select one of many inputs.

        inputs: list of N-bit integers
        select: integer (0 to num_inputs - 1)
        Returns: selected N-bit integer
        """
        # For each bit position, select the correct input
        result = 0

        for bit in range(self.bits):
            # Collect all AND outputs for this bit
            and_outputs = []
            for i in range(self.num_inputs):
                input_bit = (inputs[i] >> bit) & 1
                select_bit = 1 if i == select else 0

                # AND the input bit with the select line
                and_out = self.and_gate.forward_single(input_bit, select_bit)
                and_outputs.append(and_out)

            # OR all AND outputs together
            if self.num_inputs == 1:
                result_bit = and_outputs[0]
            else:
                result_bit = and_outputs[0]
                for i in range(1, self.num_inputs):
                    result_bit = self.or_gate.forward_single(result_bit, and_outputs[i])

            result |= (int(result_bit) << bit)

        return result

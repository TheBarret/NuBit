# adder.py - Carry Lookahead Adder

import numpy as np
from gates import AND, OR, XOR, NOT, NOR, NAND

# Performance table:
# Performance test (4-bit):
#  10000 additions in 2815.61 ms
#  Speed: 3552 ops/sec
#
# Performance test (8-bit):
#  10000 additions in 2931.46 ms
#  Speed: 3411 ops/sec
#
# Performance test (16-bit):
#  10000 additions in 3057.30 ms
#  Speed: 3271 ops/sec


# Optimized, Carry Look Ahead adder, Kogge-Stone parallel prefix
# revision 0.2
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

        # old, slow performance
        #for i in range(self.bits):
        #    S[i] = self.xor_gate.forward_single(int(P[i]), int(carries[i]))
        # Reconstruct result
        #result = 0
        #for i in range(self.bits):
        #    result |= int(S[i]) << i
        #result |= int(carries[self.bits]) << self.bits
        #return result, int(carries[self.bits])

        result = 0
        for i in range(self.bits):
            result |= int(S[i]) << i
        result |= int(carries[self.bits]) << self.bits

        return result, int(carries[self.bits])

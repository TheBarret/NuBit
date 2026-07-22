# gates.py - Vectorized Logic Gates

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

# ==================== MACROS ====================

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

# gates.py - XOR (vectorized)

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

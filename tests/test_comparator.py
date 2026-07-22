# test_comparator.py
import numpy as np
from nubit2 import Comparator, XOR, AND, OR, NOT

def test_comparator_debug():
    cmp = Comparator(16)

    # Test each case individually
    test_cases = [
        (5, 5, "equal"),
        (3, 5, "less"),
        (5, 3, "greater"),
        (0, 65535, "less (unsigned)"),
    ]

    for a, b, desc in test_cases:
        # Convert to bit arrays manually for debugging
        A_bits = np.array([(a >> i) & 1 for i in range(16)])
        B_bits = np.array([(b >> i) & 1 for i in range(16)])

        print(f"\n--- {a} cmp {b} ({desc}) ---")
        print(f"A_bits (LSB first): {A_bits}")
        print(f"B_bits (LSB first): {B_bits}")

        # Test XOR gate directly
        xor_gate = XOR()
        xor_results = xor_gate.forward(A_bits, B_bits)
        print(f"XOR results: {xor_results}")
        print(f"Any XOR=1? {np.any(xor_results)}")

        # Manual equality check
        equal = 1 if not np.any(xor_results) else 0
        print(f"Equal: {equal}")

        # Manual MSB difference
        less_than = 0
        greater_than = 0
        for i in range(15, -1, -1):
            if A_bits[i] != B_bits[i]:
                print(f"MSB diff at bit {i}: A={A_bits[i]}, B={B_bits[i]}")
                if A_bits[i] == 0 and B_bits[i] == 1:
                    less_than = 1
                else:
                    greater_than = 1
                break

        # Call comparator
        result = cmp.forward(a, b)
        print(f"Comparator result: {result}")
        print(f"Manual result: equal={equal}, less={less_than}, greater={greater_than}")

if __name__ == "__main__":
    test_comparator_debug()

# test_alu.py
import time
import numpy as np
from machine16 import ALU16, Opcode, Flag

def test_alu():
    """Test ALU16 against expected operations."""
    alu = ALU16()
    failures = 0
    num_tests = 100

    # Test each operation
    for op in range(6):  # 0-5 only (ADD, SUB, AND, OR, XOR, MUL)
        op_name = ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'MUL'][op]
        print(f"\nTesting {op_name}:")

        for _ in range(num_tests):
            a = np.random.randint(0, 65536)
            b = np.random.randint(0, 65536)

            result = alu.forward(a, b, op)

            if op == 0:  # ADD
                expected = (a + b) & 0xFFFF
            elif op == 1:  # SUB
                expected = (a - b) & 0xFFFF
            elif op == 2:  # AND
                expected = a & b
            elif op == 3:  # OR
                expected = a | b
            elif op == 4:  # XOR
                expected = a ^ b
            elif op == 5:  # MUL
                expected = (a * b) & 0xFFFF

            if result != expected:
                failures += 1
                if failures <= 10:
                    print(f"  FAIL: {op_name} {a} {b} = {result} (expected {expected})")

        print(f"  ✅ {op_name} tests passed")

    # Test CMP separately (flags only)
    print(f"\nTesting CMP:")
    cmp_tests = [
        (5, 5, (1, 0, 0), "equal"),
        (3, 5, (0, 1, 0), "less"),
        (5, 3, (0, 0, 1), "greater"),
        (0, 0xFFFF, (0, 1, 0), "less unsigned"),
        (0xFFFF, 0, (0, 0, 1), "greater unsigned"),
    ]

    for a, b, expected_flags, desc in cmp_tests:
        alu.forward(a, b, Opcode.CMP)
        got = (alu.flags[Flag.ZERO], alu.flags[Flag.LESS], alu.flags[Flag.GREATER])
        if got == expected_flags:
            print(f"  ✓ CMP {a} {b}: {desc}")
        else:
            print(f"  ✗ CMP {a} {b}: got {got} expected {expected_flags}")
            failures += 1

    # Performance test
    print("Performance Test:")

    a_batch = np.random.randint(0, 65536, 1000)
    b_batch = np.random.randint(0, 65536, 1000)

    start = time.time()
    for a, b in zip(a_batch, b_batch):
        alu.forward(a, b, Opcode.ADD)
    elapsed = time.time() - start

    print(f"  1000 ADD operations in {elapsed*1000:.2f} ms")
    print(f"  Speed: {1000/elapsed:.0f} ops/sec")

    if failures == 0:
        print("PASSED")
    else:
        print(f"FAILED")

if __name__ == "__main__":
    test_alu()

# test_perf.py
import time
import numpy as np
from storage import UnifiedBus, Memory
from machine16 import CPU16, Opcode

def setup_cpu():
    bus = UnifiedBus(addr_width=16, data_width=16)
    mem = Memory(size=65536, data_width=16, backend='numpy')
    bus.connect("RAM", mem, (0x0000, 0xFFFF))
    cpu = CPU16(bus)
    cpu.pc = 0x0100
    return cpu, mem

def run_program(cpu, mem, program):
    for i, inst in enumerate(program):
        mem.write(0x0100 + i, inst)
    cpu.pc = 0x0100
    return cpu.run(max_cycles=10000, verbose=False)

def test_performance():
    # Now use LDI16 for large constants
    program = [
        (Opcode.LDI16 << 12) | (0 << 8), 0x0064,     # R0 = 100 (counter)
        (Opcode.LDI << 12) | (1 << 8) | 0x0,         # R1 = 0
        (Opcode.LDI << 12) | (5 << 8) | 0x1,         # R5 = 1
        (Opcode.LDI16 << 12) | (2 << 8), 0x0107,     # R2 = loop target (after LDI16)
        # Loop at 0x0107
        (Opcode.ADD << 12) | (1 << 8) | (1 << 4) | 5,  # R1 = R1 + 1
        (Opcode.SUB << 12) | (0 << 8) | (0 << 4) | 5,  # R0 = R0 - 1
        (Opcode.JNZ << 12) | (2 << 4),               # JNZ R2
        (Opcode.HALT << 12),
    ]

    # Run 10 times and average
    times = []
    cycles_list = []

    print("\nRunning performance test (100 iterations)...")

    for i in range(10):
        cpu, mem = setup_cpu()
        start = time.perf_counter()
        cycles = run_program(cpu, mem, program)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        cycles_list.append(cycles)
        print(f"  Run {i+1:2d}: {elapsed*1000:.2f} ms, {cycles} cycles")

    avg_time = np.mean(times)
    avg_cycles = np.mean(cycles_list)
    ops_per_sec = avg_cycles / avg_time

    print("-" * 50)
    print(f"\nAverage: {avg_time*1000:.2f} ms for {avg_cycles:.0f} cycles")
    print(f"Speed: {ops_per_sec:.0f} ops/sec")
    print(f"Time per op: {avg_time/avg_cycles*1000:.3f} ms")

    # Compare to expected performance
    print("\n" + "=" * 60)
    print("Performance Comparison:")
    print("-" * 50)
    print(f"  NuBit V2 16-bit: ~3,271 ops/sec")
    print(f"  Machine16:        ~{ops_per_sec:.0f} ops/sec")
    print(f"  Ratio:            {ops_per_sec/3271:.2f}x")

    # Estimate expected cycles per loop iteration
    # Each loop iteration = ADD + SUB + JNZ = 3 cycles
    # Setup = ~6 cycles
    expected_cycles = 6 + 100 * 3  # ~306 cycles
    print(f"\n  Expected cycles for 100 iterations: ~{expected_cycles}")
    print(f"  Actual cycles: {avg_cycles:.0f}")

    if ops_per_sec > 3000:
        print("\nPerformance meets expectations ( > 3000 ops/sec )")
        return True
    else:
        print(f"\nPerformance is lower than expected")
        return False

if __name__ == "__main__":
    test_performance()

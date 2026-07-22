# test_storage.py

import numpy as np
from storage import UnifiedBus, Memory

def test_bus_memory():
    """Test the bus and memory independently."""
    print("=" * 60)
    print("UNIFIED BUS + MEMORY TEST")
    print("=" * 60)

    # === Test 1: 8-bit mode ===
    print("\n[TEST 1] 8-bit mode")
    print("-" * 40)

    bus8 = UnifiedBus(addr_width=8, data_width=8)
    mem8 = Memory(size=256, data_width=8, backend='python')
    bus8.connect("RAM", mem8, (0x00, 0xFF))

    # Write and read
    bus8.addr = 0x10
    bus8.data_out = 0x42
    bus8.wr = 1
    bus8.rd = 0
    result = bus8.tick()
    print(f"  Write: {bus8.last_op}")

    bus8.addr = 0x10
    bus8.wr = 0
    bus8.rd = 1
    result = bus8.tick()
    print(f"  Read:  {bus8.last_op}")
    print(f"  Data read: 0x{result:02X} (expected 0x42)")

    # Check memory directly
    stored = mem8.read(0x10)
    print(f"  Memory[0x10] = 0x{stored:02X}")

    # === Test 2: 16-bit mode ===
    print("\n[TEST 2] 16-bit mode")
    print("-" * 40)

    bus16 = UnifiedBus(addr_width=16, data_width=16)
    mem16 = Memory(size=65536, data_width=16, backend='numpy')
    bus16.connect("RAM", mem16, (0x0000, 0xFFFF))

    # Write and read
    bus16.addr = 0x1234
    bus16.data_out = 0xDEAD
    bus16.wr = 1
    bus16.rd = 0
    result = bus16.tick()
    print(f"  Write: {bus16.last_op}")

    bus16.addr = 0x1234
    bus16.wr = 0
    bus16.rd = 1
    result = bus16.tick()
    print(f"  Read:  {bus16.last_op}")
    print(f"  Data read: 0x{result:04X} (expected 0xDEAD)")

    # Check memory directly
    stored = mem16.read(0x1234)
    print(f"  Memory[0x1234] = 0x{stored:04X}")

    # === Test 3: Multiple devices ===
    print("\n[TEST 3] Multiple devices")
    print("-" * 40)

    # Create two memory banks
    mem_a = Memory(size=256, data_width=8, backend='python')
    mem_b = Memory(size=256, data_width=8, backend='python')

    bus = UnifiedBus(addr_width=8, data_width=8)
    bus.connect("BANK_A", mem_a, (0x00, 0x7F))
    bus.connect("BANK_B", mem_b, (0x80, 0xFF))

    # Write to BANK_A
    bus.addr = 0x10
    bus.data_out = 0xAA
    bus.wr = 1
    bus.rd = 0
    bus.tick()
    print(f"  Write to BANK_A: {bus.last_op}")

    # Write to BANK_B
    bus.addr = 0x90
    bus.data_out = 0xBB
    bus.wr = 1
    bus.rd = 0
    bus.tick()
    print(f"  Write to BANK_B: {bus.last_op}")

    # Read from BANK_A
    bus.addr = 0x10
    bus.wr = 0
    bus.rd = 1
    result = bus.tick()
    print(f"  Read from BANK_A: {bus.last_op}")
    print(f"  Data: 0x{result:02X} (expected 0xAA)")

    # Read from BANK_B
    bus.addr = 0x90
    bus.wr = 0
    bus.rd = 1
    result = bus.tick()
    print(f"  Read from BANK_B: {bus.last_op}")
    print(f"  Data: 0x{result:02X} (expected 0xBB)")

    # === Test 4: Error handling ===
    print("\n[TEST 4] Error handling (no device)")
    print("-" * 40)

    bus = UnifiedBus(addr_width=8, data_width=8)
    # No devices connected

    bus.addr = 0xFF
    bus.wr = 0
    bus.rd = 1
    result = bus.tick()
    print(f"  Read from nowhere: {bus.last_op}")
    print(f"  Data: 0x{result:02X} (expected 0xFF - bus float)")

    # === Test 5: Memory stats ===
    print("\n[TEST 5] Memory stats")
    print("-" * 40)

    stats = mem16.get_stats()
    print(f"  Reads: {stats['reads']}")
    print(f"  Writes: {stats['writes']}")
    print(f"  Total ops: {stats['total_ops']}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_bus_memory()

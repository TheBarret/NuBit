# Threshold Logic Unit (NuBit)

A neural-network-based CPU architecture where logic gates are implemented using McCulloch-Pitts (MCP) neurons.  
Version 2 introduces vectorized operations, Kogge-Stone parallel prefix, and pure NumPy acceleration,  
transforming it from a conceptual prototype to a high-performance simulation.  

## Machine16

| Component | Specification |
|--------|---------------|
| **Architecture** | 16-bit |
| **Registers** | 16 × 16-bit |
| **Address space** | 64KB |
| **ALU operations** | ADD, SUB, AND, OR, XOR, MUL, CMP |
| **Instructions** | LDI, LD, ST, ADD, SUB, AND, OR, XOR, MUL, CMP, JMP, JZ, JNZ, HALT |
| **Flags** | Zero (Z), Carry (C), Overflow (V), Less (L), Greater (G) |
| **Performance** | ~97 ops/sec (software simulation) |
| **Memory** | virtual memory |
| **Bus** | virtual 16-bit unified, device discovery bus|


### Instruction Set

| Opcode | Mnemonic | Operation |
|--------|----------|-----------|
| 0 | ADD | Rdest = Rsrc1 + Rsrc2 |
| 1 | SUB | Rdest = Rsrc1 - Rsrc2 |
| 2 | AND | Rdest = Rsrc1 & Rsrc2 |
| 3 | OR | Rdest = Rsrc1 \| Rsrc2 |
| 4 | XOR | Rdest = Rsrc1 ^ Rsrc2 |
| 5 | MUL | Rdest = Rsrc1 * Rsrc2 |
| 6 | CMP | Compare Rsrc1, Rsrc2 (sets flags) |
| 7 | LDI | Rdest = Immediate (4-bit) |
| 8 | LD | Rdest = [Rsrc1] |
| 9 | ST | [Rdest] = Rsrc1 |
| 10 | JMP | PC = Rsrc1 |
| 11 | JZ | if Z: PC = Rsrc1 |
| 12 | JNZ | if !Z: PC = Rsrc1 |
| 15 | HALT | Stop execution |

# Versions

| Aspect | NuBit V1 | NuBit V2 | Improvement |
|--------|----------|----------|-------------|
| **Gate activation** | Sigmoid (`exp()`) | Step (`> 0`) | 10-100× |
| **Data representation** | Object per gate | NumPy arrays | 100-1000× |
| **Gate operations** | Python loops | Vectorized batch | 100-1000× |
| **Adder architecture** | Ripple carry (O(N)) | Kogge-Stone (O(log N)) | Performance |
| **Sum computation** | Per-bit Python loop | Vectorized XOR | 5-10× |
| **Code structure** | OOP per gate | NumPy matrix ops | Performance |

# Components

| Component | Bit Width | Tests | Status |
|-----------|-----------|-------|--------|
| AND gate | 1-bit | Truth table | functional |
| OR gate | 1-bit | Truth table | functional |
| NAND gate | 1-bit | Truth table | functional |
| NOR gate | 1-bit | Truth table | functional |
| NOT gate | 1-bit | Truth table | functional |
| XOR gate | 1-bit | Truth table | functional |
| Carry Lookahead Adder | 4-bit | 256/256 | functional |
| Carry Lookahead Adder | 8-bit | 10,000 random | functional |
| Carry Lookahead Adder | 16-bit | 10,000 random | functional |

# Scaling Tables

| Bit Width | V1 (Ripple) | V2 (Kogge-Stone + Vectorized Sum) | Improvement |
|-----------|-------------|-----------------------------------|-------------|
| **4-bit** | ~2,000 ops/sec | **3,552 ops/sec** | **1.8×** |
| **8-bit** | ~1,000 ops/sec | **3,411 ops/sec** | **3.4×** |
| **16-bit** | ~357 ops/sec | **3,271 ops/sec** | **9.2×** |

### NuBit-Adder Performance

| 4Bit Version | Speed (ops/sec) | Improvement (vs previous) | Total Improvement |
|---------|-----------------|---------------------------|-------------------|
| **V1 (ripple carry)** | ~2,000 | 1× | 1× |
| **V2 (Kogge-Stone)** | 1,803 | ~0.9× | ~0.9× |
| **V2 (vectorized sum)** | **3,552** | **~2×** | **~1.8×** |

| 8Bit Version | Speed (ops/sec) | Improvement (vs previous) | Total Improvement |
|---------|-----------------|---------------------------|-------------------|
| **V1 (ripple carry)** | ~1,000 | 1× | 1× |
| **V2 (Kogge-Stone)** | 1,061 | ~1.1× | ~1.1× |
| **V2 (vectorized sum)** | **3,411** | **~3.2×** | **~3.4×** |

| 16Bit Version | Speed (ops/sec) | Improvement (vs previous) | Total Improvement |
|---------|-----------------|---------------------------|-------------------|
| **V1 (ripple carry)** | ~357 | 1× | 1× |
| **V2 (Kogge-Stone)** | 588 | ~1.6× | ~1.6× |
| **V2 (vectorized sum)** | **3,271** | **~5.6×** | **~9.2×** |

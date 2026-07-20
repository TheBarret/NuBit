
A 8/16-bit neural CPU with 7 ALU operations.  


| Task | Works |
|------|--------|
| Add two numbers | ✅ |
| Subtract two numbers | ✅ |
| Bitwise AND/OR/XOR | ✅ |
| Multiply two numbers | ✅ |
| Compare two numbers | ✅ |
| Read from memory | ✅ |
| Write to memory | ✅ |
| Run a loop | To do |
| Output to console | To do |

### 1. Logic Gates (Atom)

| Gate | Implementation | Status |
|------|----------------|--------|
| AND | 1 neuron | ✅ Tested |
| OR | 1 neuron | ✅ Tested |
| NAND | 1 neuron | ✅ Tested |
| NOR | 1 neuron | ✅ Tested |
| NOT | 1 neuron | ✅ Tested |
| XOR | 2-layer network | ✅ Tested |

---

### 2. Arithmetic Units

| Unit | Built From | Status |
|------|------------|--------|
| Half-Adder | XOR + AND | ✅ Tested |
| Full-Adder | 2 × Half-Adder + OR | ✅ Tested |
| 4-bit Adder | 4 × Full-Adder (chained) | ✅ Tested (256/256 tests) |
| N-bit Adder | N × Full-Adder (chained) | ✅ Designed |

---

### 3. ALU Operations (7 Instructions)

| Opcode | Mnemonic | Operation | Tested |
|--------|----------|-----------|----------|
| 0 | **ADD** | `dest = src1 + src2` | ✅ |
| 1 | **SUB** | `dest = src1 - src2` | ✅ |
| 2 | **AND** | `dest = src1 & src2` | ✅ |
| 3 | **OR** | `dest = src1 \| src2` | ✅ |
| 4 | **XOR** | `dest = src1 ^ src2` | ✅ |
| 5 | **MUL** | `dest = src1 * src2` | ✅ |
| 6 | **CMP** | `compare src1, src2` | ✅ |

**Flags affected:** Carry (C), Zero (Z), Less (L), Greater (G)

---

### 4. Memory

| Component | Size | Status |
|-----------|------|--------|
| SRAM Cell | 1-bit | ✅ Designed |
| SRAM Byte | 8-bit | ✅ Designed |
| SRAM Array | N×M | ✅ Designed |
| FastSRAM (NumPy) | 64KB | ✅ Implemented |
| BooleanSRAM (gates) | 256 bytes | ✅ Tested |
| MemristorSRAM (model) | 256 bytes | ✅ Designed |

---

### 5. Bus

| Bus Line | Width | Direction | Status |
|----------|-------|-----------|--------|
| Address | 8-bit | ALU → Bus → Devices | ✅ |
| Data Out | 8-bit | ALU → Bus → Devices | ✅ |
| Data In | 8-bit | Devices → Bus → ALU | ✅ |
| Control | 4-bit | ALU → Bus → Devices | ✅ |

**Control signals:** RD, WR, SEL, CLK

---

### 6. I/O

| Device | Address | Status |
|--------|---------|--------|
| Console Output | 0xFE (write-only) | ✅ Planned |
| Keyboard Input | 0xFD (read-only) | ✅ Planned |

---

## Instruction Set

```
┌─────────────────────────────────────────────────────────────┐
│  NUBIT INSTRUCTION SET (7 OPS)                              │
│                                                             │
│  OP  MNEMONIC  OPERATION              FLAGS                 │
│  ────────────────────────────────────────────────────────── │
│  0   ADD       dest = src1 + src2     C, Z                  │
│  1   SUB       dest = src1 - src2     C, Z, L, G            │
│  2   AND       dest = src1 & src2     Z                     │
│  3   OR        dest = src1 | src2     Z                     │
│  4   XOR       dest = src1 ^ src2     Z                     │
│  5   MUL       dest = src1 * src2     C, Z                  │
│  6   CMP       compare src1, src2     C, Z, L, G            │
└─────────────────────────────────────────────────────────────┘
```


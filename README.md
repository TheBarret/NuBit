# Threshold Logic Unit (NuBit)
Formally described as McCulloch-Pitts neurons, from Warren McCulloch and Walter Pitts' 1943 paper.  
A 8/16-bit neural CPU with 7 ALU operations.  

## Atom

```py
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
```

## ALU Design
```py
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
            self.comparator.forward(a, b)['equal']
        ]
        return self.mux.forward(results, op)
```

| Task | Works |
|------|--------|
| Add two numbers | Tested |
| Subtract two numbers | Tested |
| Bitwise AND/OR/XOR | Tested |
| Multiply two numbers | Tested |
| Compare two numbers | Tested |
| Read from memory | Tested |
| Write to memory | Tested |
| Run a loop | To do |
| Output to console | To do |

### 1. Logic Gates (Atom)

| Gate | Implementation | Status |
|------|----------------|--------|
| AND | 1 neuron | Tested |
| OR | 1 neuron | Tested |
| NAND | 1 neuron | Tested |
| NOR | 1 neuron | Tested |
| NOT | 1 neuron | Tested |
| XOR | 2-layer network | Tested |

---

### 2. Arithmetic Units

| Unit | Built From | Status |
|------|------------|--------|
| Half-Adder | XOR + AND | Tested |
| Full-Adder | 2 × Half-Adder + OR | Tested |
| 4-bit Adder | 4 × Full-Adder (chained) | Tested (256/256 tests) |
| N-bit Adder | N × Full-Adder (chained) | Tested Designed |

---

### 3. ALU Operations (7 Instructions)

| Opcode | Mnemonic | Operation | Tested |
|--------|----------|-----------|----------|
| 0 | **ADD** | `dest = src1 + src2` | Tested |
| 1 | **SUB** | `dest = src1 - src2` | Tested |
| 2 | **AND** | `dest = src1 & src2` | Tested |
| 3 | **OR** | `dest = src1 \| src2` | Tested |
| 4 | **XOR** | `dest = src1 ^ src2` | Tested |
| 5 | **MUL** | `dest = src1 * src2` | Tested |
| 6 | **CMP** | `compare src1, src2` | Tested |

**Flags affected:** Carry (C), Zero (Z), Less (L), Greater (G)

---

### 4. Memory

| Component | Size | Status |
|-----------|------|--------|
| SRAM Cell | 1-bit | Implemented |
| SRAM Byte | 8-bit | Implemented |
| SRAM Array | N×M | Implemented |
| FastSRAM (NumPy) | 64KB | Implemented |
| BooleanSRAM (gates) | 256 bytes | Implemented |
| MemristorSRAM (model) | 256 bytes | Designed |

---

### 5. Bus

| Bus Line | Width | Direction | Status |
|----------|-------|-----------|--------|
| Address | 8-bit | ALU → Bus → Devices | Planned |
| Data Out | 8-bit | ALU → Bus → Devices | Planned |
| Data In | 8-bit | Devices → Bus → ALU | Planned |
| Control | 4-bit | ALU → Bus → Devices | Planned |

**Control signals:** RD, WR, SEL, CLK

---

### 6. I/O

| Device | Address | Status |
|--------|---------|--------|
| Console Output | 0xFE (write-only) | Planned |
| Keyboard Input | 0xFD (read-only) | Planned |

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




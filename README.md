# Threshold Logic Unit (NuBit)
Formally described as McCulloch-Pitts neurons, from Warren McCulloch and Walter Pitts' 1943 paper.  
A 8/16-bit neural CPU with 7 ALU operations.  
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
### ALU Operations (7 Instructions)

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




<img width="1132" height="589" alt="image" src="https://github.com/user-attachments/assets/79c132c5-22ba-4624-ae4b-283eb739316a" />

## Porting to C

The Python prototype proved the concept, the C port performance is ~228,000 ops/sec for 16-bit operations,  
roughly 70× faster than Python, while preserving the neural architecture.  

Perf results (on a AMD-8Core):
```
1000000 ops each, 4000000 ops total:
  ADD       98102 ops/sec  (10193.424 ms total, 10.193 µs/op)
  SUB       97956 ops/sec  (10208.638 ms total, 10.209 µs/op)
  MUL      185006 ops/sec  (5405.216 ms total, 5.405 µs/op)
  CMP       98347 ops/sec  (10168.064 ms total, 10.168 µs/op)

============================================================
ALU Performance Summary:
  Total time:  35975.34 ms
  Total ops:   4000000
  Average:     ~111187 ops/sec (total ops / total time)
```

## Files

| File | Role |
|------|------|
| **gates.c** | McCulloch-Pitts neurons: AND, OR, NAND, NOR, NOT, XOR. All logic is computed via weighted sums + threshold, not emulated gates. |
| **adder.c** | Kogge-Stone parallel prefix adder. O(log N) carry propagation. The heart of the ALU's speed. |
| **alu16.c** | ALU operations: ADD, SUB, MUL, AND, OR, XOR, CMP. All 80+ tests pass. Flags: Z, C, OV, L, G. |
| **cpu16.c** | 16-register, 16-bit CPU. Fetch-decode-execute with function-pointer dispatch. 16 instructions including SYS. |
| **bus.c** | Virtual 64KB memory. Handles reads/writes and I/O port trapping. |
| **nb-asm.c** | Two-stage assembler. Pass 1 collects symbols; Pass 2 generates bytecode. Outputs hex for the runtime. |

## Pipeline

```
.asm → nb-asm → .hex → nubit → output
```

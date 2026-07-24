## Porting Python to C Challenge

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
| **bus.c/neuristor.c** | Virtual 64 MiB Neuristor-based memory (16-Bit). Handles reads/writes and I/O port trapping. |
| **nb-asm.c** | Two-stage assembler. Pass 1 collects symbols; Pass 2 generates bytecode. Outputs hex for the runtime. |
| **main.c** | Runs NuBit runtime with hexcode (`nubit program.hex`) |

## Neuristor Memory

A hardware-level simulation of a neuromorphic memory bus (16-bit), rather than using traditional static RAM (SRAM),  
memory is stored across a 3D fields of virtual neuristor cells, analog switches activated by coincident voltage signals.  

The bus maps a 16-bit address space (`65,536` locations) across 16 parallel bitplanes.  
Each bitplane contains a `256x256` grid of physical `Neuristor` cells.  

```
          Plane 15 (Bit 15 Grid)  [256 x 256]  ──► Bit 15
                   ⋮
          Plane  1 (Bit  1 Grid)  [256 x 256]  ──► Bit 1
          Plane  0 (Bit  0 Grid)  [256 x 256]  ──► Bit 0
                                                    │
 Address (16-bit) ──► [ Row (8-bit) | Col (8-bit) ]─┴─► 16-bit CPU Data Word
```

Every bus operation takes place during a single clock tick (`bus_tick`) and relies on coincident voltage signals, 
`(w_row + w_col + bias > 0)` to activate targeted cells.  

#### Read Cycle (`bus_read`)
1. **Address Decode:** Decodes the requested address into `(Row, Col)` coordinates.  
2. **Coincident Activation:** Drives row/col activation signals to all 16 planes.  
3. **Destructive Read:** Each selected cell's analog state (`NEURISTOR_POSITIVE` vs. `NEURISTOR_NEGATIVE`) is sampled into a 16-bit word.
   *Reading wipes the cell state to neutral.*
4. **Auto-Refresh:** The bus immediately rewrites the sampled bits back into the cell, hiding the destructive read from the CPU.  

#### Write Cycle (`bus_write`)
1. **Address Decode:** Decodes address into `(Row, Col)` coordinates.
2. **Coincident Activation:** Drives row/col activation signals to all 16 planes.
3. **State Latency:** Translates each bit of the CPU `data_out` word into positive (`+`) or negative (`-`) state biases and updates the neuristor cells.  

## Pipeline

```
.asm → nb-asm → .hex → nubit → output
```
<img width="1044" height="640" alt="image" src="https://github.com/user-attachments/assets/3a588215-8b01-4a1d-9a50-36d23fe566a1" />
*(sorry for the little typo)*



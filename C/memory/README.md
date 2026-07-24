

## Neural CAM	4KB Memory *Concept*

Each CAM entry has:
- Pattern bits (16-bit)
- Data bits (16-bit)
- Valid bit
- age/priority bits

`SYS` calls for CAM operations:
- `SYS` 4, addr, data → Store pattern at addr
- `SYS` 5, addr → Find pattern matching addr
- `SYS` 6 → Invalidate CAM

Interface (memory-mapped I/O):  
- `0xFFF4`: NAM_CTRL   - Control register
- `0xFFF5`: NAM_ADDR   - Address/Pattern register
- `0xFFF6`: NAM_DATA   - Data register
- `0xFFF7`: NAM_STATUS - Status register

Pattern Memory (SRAM + Comparator):
- 256 entries × 16-bit pattern + data
- Parallel comparator using XOR/AND gates

Associative Search Engine
- Parallel pattern matching
- Hamming distance calculation
- Best match selection

Learning Engine:  
- Hebbian learning (weights)
- Pattern storage/update


```asm
; Neural Associative Memory Test

start:
    ; Store pattern: 0x1234 → data: 0xABCD
    LDI R0, 0x34
    LDI R1, 0x12
    ST 0xFFF5, R0       ; Write pattern low byte
    ST 0xFFF5, R1       ; Write pattern high byte
    LDI R0, 0xCD
    LDI R1, 0xAB
    ST 0xFFF6, R0       ; Write data low byte
    ST 0xFFF6, R1       ; Write data high byte
    LDI R0, 2           ; STORE operation
    ST 0xFFF4, R0       ; Trigger store

    ; Search for pattern 0x1234
    LDI R0, 0x34
    LDI R1, 0x12
    ST 0xFFF5, R0       ; Write pattern low byte
    ST 0xFFF5, R1       ; Write pattern high byte
    LDI R0, 1           ; SEARCH operation
    ST 0xFFF4, R0       ; Trigger search

    ; Read result from NAM_DATA
    LD R0, 0xFFF6       ; R0 = data (should be 0xABCD)
    ; ... use result ...

    HALT
```

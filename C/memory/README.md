# NuBit Memory Subsystem

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/24dae04d-c70e-4777-ae4b-1e8cef6342bf" />


## Tier 1, Register File (fast, small, gate-native)

Existing `Gate` primitive (specifically `NAND_GATE`), composed into cross-coupled SR latches,  
then master-slave D flip-flops for edge-triggered (clocked) behavior consistent with the fetch/decode/execute loop.  

Small enough (256 bits) that full gate-level simulation costs nothing meaningful.  
High read/write frequency makes edge-triggered discipline (not level-sensitive) the correct choice,  
avoids race conditions across a single "tick."  

Reuses existing `Gate`. New composite types: `SRLatch`, `DFlipFlop`, `RegisterFile`.  

## Tier 2, Neuristor Core

A "Neuristor Core" is a mapping of a ternary magnetic coincident-current selection onto a McCulloch-Pitts-style neuron.  


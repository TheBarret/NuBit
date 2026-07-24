# NuBit Memory Subsystem

## Tier 1, Register File (fast, small, gate-native)

Existing `Gate` primitive (specifically `NAND_GATE`), composed into cross-coupled SR latches,  
then master-slave D flip-flops for edge-triggered (clocked) behavior consistent with the fetch/decode/execute loop.  

Small enough (256 bits) that full gate-level simulation costs nothing meaningful.  
High read/write frequency makes edge-triggered discipline (not level-sensitive) the correct choice,  
avoids race conditions across a single "tick."  

Reuses existing `Gate`. New composite types: `SRLatch`, `DFlipFlop`, `RegisterFile`.  

## Tier 2, Neuristor Concept

To do...


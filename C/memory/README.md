# NuBit Memory Subsystem

## Tier 1, Register File (fast, small, gate-native)

Existing `Gate` primitive (specifically `NAND_GATE`), composed into cross-coupled SR latches,  
then master-slave D flip-flops for edge-triggered (clocked) behavior consistent with the fetch/decode/execute loop.  

Small enough (256 bits) that full gate-level simulation costs nothing meaningful.  
High read/write frequency makes edge-triggered discipline (not level-sensitive) the correct choice,  
avoids race conditions across a single "tick."  

Reuses existing `Gate`. New composite types: `SRLatch`, `DFlipFlop`, `RegisterFile`.  

## Tier 2, Core Memory (bulk, neuron-addressed, untested, concept)

A stand-in for magnetic core memory, the interesting part being *how a cell is selected*,  
not the physical storage mechanism (which no gate composition can honestly represent, see Open Questions).  

A new primitive, distinct from V2 NuBit `Gate`, a `SelectorNeuron`, ternary threshold unit (excite / neutral / inhibit),  
modeling coincident-current X/Y drive signals.  

Same linear-threshold essence as `Gate`, different activation:
  ```
  output = -1   if linear < -ε
             0   if -ε <= linear <= ε
            +1   if linear > ε
  ```
A cell is selected only when its X-axis and Y-axis `SelectorNeuron` outputs coincide,
(both +1, or magnitudes sum past a cell-level threshold), 
this is the actual coincident-current mechanism, expressed as neurons.  

Stored value itself, bit per cell, no gate/neuron composition produces bistable magnetism,  
this is a deliberate, acknowledged simplification, not an oversight).  

Distinguishing behavior worth simulating (this is the point of this tier, not just "slower RAM"),
Destructive read, reading a cell always clears it; every read must be immediately followed by a rewrite to restore state.  
Real cost, not free like array access.  
Non-volatility, state modeled as surviving a simulated power-cycle, unlike Tier 1 (flip-flops need continuous "power" to hold state).  

Fills the one real gap, *neuron-driven addressing*, that neither `Gate`-built flip-flops nor a plain array touch.  
Justified as "for science" / architectural completeness, not raw performance.  


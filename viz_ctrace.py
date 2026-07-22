# viz_ctrace.py - Visualize CPU execution trace

import matplotlib.pyplot as plt
import numpy as np

class CPUTraceVisualizer:
    """Visualize CPU execution trace as a logic analyzer."""

    def __init__(self, trace_data):
        """
        trace_data: list of dicts from verbose CPU output
        """
        self.trace = trace_data

    def draw(self):
        """Draw cycle-accurate trace."""
        if not self.trace:
            print("No trace data")
            return

        cycles = len(self.trace)
        fig, axes = plt.subplots(6, 1, figsize=(15, 8), sharex=True)

        # Row 1: PC
        axes[0].plot([t['pc'] for t in self.trace], 'bo-', markersize=8)
        axes[0].set_ylabel('PC')
        axes[0].set_ylim(0, 0x100)
        axes[0].grid(True, alpha=0.3)

        # Row 2: IR (Instruction)
        axes[1].plot([t['ir'] for t in self.trace], 'ro-', markersize=8)
        axes[1].set_ylabel('IR')
        axes[1].set_ylim(0, 0xFFFF)
        axes[1].grid(True, alpha=0.3)

        # Row 3: Opcode
        axes[2].plot([t['op'] for t in self.trace], 'go-', markersize=8)
        axes[2].set_ylabel('Opcode')
        axes[2].set_ylim(-1, 16)
        axes[2].set_yticks(range(16))
        axes[2].grid(True, alpha=0.3)

        # Row 4: Registers (R0, R1, R2)
        for reg, color in [(0, 'b'), (1, 'g'), (2, 'r')]:
            axes[3].plot([t['regs'][reg] for t in self.trace],
                        f'{color}o-', markersize=6, label=f'R{reg}')
        axes[3].set_ylabel('Regs')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)

        # Row 5: Flags
        flags = ['zero', 'carry', 'overflow', 'less', 'greater']
        for f, color in zip(flags, ['b', 'g', 'r', 'c', 'm']):
            axes[4].plot([t['flags'][f] for t in self.trace],
                        f'{color}o-', markersize=6, label=f)
        axes[4].set_ylabel('Flags')
        axes[4].legend()
        axes[4].set_ylim(-0.1, 1.1)
        axes[4].grid(True, alpha=0.3)

        # Row 6: Cycle counter
        axes[5].plot(range(cycles), 'k-', linewidth=2)
        axes[5].set_ylabel('Cycle')
        axes[5].set_xlabel('Cycle Number')
        axes[5].set_xticks(range(cycles))
        axes[5].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

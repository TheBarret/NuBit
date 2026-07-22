# viz_ks.py - Interactive Kogge-Stone stage stepper

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.widgets import Button

class KoggeStoneVisualizer:
    """Interactive Kogge-Stone parallel prefix visualizer."""

    def __init__(self, bits=8):
        self.bits = bits
        self.stage = 0
        self.max_stages = int(np.ceil(np.log2(bits))) + 1

        # Generate random G/P values for demonstration
        self.G = np.random.randint(0, 2, bits)
        self.P = np.random.randint(0, 2, bits)
        self.G_out = self.G.copy()
        self.P_out = self.P.copy()

        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 6))
        plt.subplots_adjust(bottom=0.15)

        # Add stage buttons
        ax_prev = plt.axes([0.3, 0.05, 0.15, 0.05])
        ax_next = plt.axes([0.55, 0.05, 0.15, 0.05])
        self.btn_prev = Button(ax_prev, '◀ Previous')
        self.btn_next = Button(ax_next, 'Next ▶')
        self.btn_prev.on_clicked(self.prev_stage)
        self.btn_next.on_clicked(self.next_stage)

        self.draw()

    def compute_carries(self, stage):
        """Compute carries up to given stage."""
        G_out = self.G.copy()
        P_out = self.P.copy()

        stride = 1
        for s in range(stage + 1):
            if stride >= self.bits:
                break
            idx = slice(stride, self.bits)
            prev_idx = slice(0, self.bits - stride)
            G_out[idx] = G_out[idx] | (P_out[idx] & G_out[prev_idx])
            P_out[idx] = P_out[idx] & P_out[prev_idx]
            stride <<= 1

        return G_out, P_out

    def draw(self):
        """Draw the Kogge-Stone network for current stage."""
        self.ax.clear()
        self.ax.set_xlim(-0.5, self.bits + 0.5)
        self.ax.set_ylim(-0.5, 2.5)
        self.ax.axis('off')
        self.ax.set_title(f"Kogge-Stone Stage {self.stage}/{self.max_stages-1}")

        # Compute carries for current stage
        G_out, P_out = self.compute_carries(self.stage)

        # Draw bits
        for i in range(self.bits):
            # Input row (G/P)
            g_color = 'red' if self.G[i] else 'lightgray'
            p_color = 'blue' if self.P[i] else 'lightgray'

            g_rect = patches.Rectangle((i, 1.5), 0.6, 0.4, facecolor=g_color, edgecolor='black')
            p_rect = patches.Rectangle((i, 1.0), 0.6, 0.4, facecolor=p_color, edgecolor='black')
            self.ax.add_patch(g_rect)
            self.ax.add_patch(p_rect)
            self.ax.text(i + 0.3, 1.7, f'G{i}', ha='center', fontsize=8)
            self.ax.text(i + 0.3, 1.2, f'P{i}', ha='center', fontsize=8)

            # Output row
            out_color = 'gold' if G_out[i] else 'lightgray'
            out_rect = patches.Rectangle((i, 0.2), 0.6, 0.4, facecolor=out_color, edgecolor='black')
            self.ax.add_patch(out_rect)
            self.ax.text(i + 0.3, 0.4, f'C{i+1}', ha='center', fontsize=8)

        # Draw connections based on stage
        if self.stage > 0:
            stride = 1 << (self.stage - 1)
            for i in range(stride, self.bits):
                # Draw diagonal connection
                self.ax.annotate('', xy=(i, 1.2), xytext=(i - stride, 1.8),
                               arrowprops=dict(arrowstyle='->', color='purple', lw=2, alpha=0.7))

        self.fig.canvas.draw()

    def next_stage(self, event):
        if self.stage < self.max_stages - 1:
            self.stage += 1
            self.draw()

    def prev_stage(self, event):
        if self.stage > 0:
            self.stage -= 1
            self.draw()

    def show(self):
        plt.show()

# Usage
viz = KoggeStoneVisualizer(8)
viz.show()

# viz_neuron.py - Single MCP neuron visualization

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

def draw_neuron(weights, bias, title="AND Gate"):
    """Draw a single MCP neuron with weights and bias."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 4)
    ax.axis('off')

    # Inputs
    ax.text(0.2, 3.0, "x₁", fontsize=14, fontweight='bold')
    ax.text(0.2, 1.0, "x₂", fontsize=14, fontweight='bold')

    # Weight lines
    ax.annotate(f"w₁={weights[0]:.1f}", xy=(2.0, 2.5), xytext=(0.5, 2.8),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate(f"w₂={weights[1]:.1f}", xy=(2.0, 1.5), xytext=(0.5, 1.2),
                arrowprops=dict(arrowstyle='->', lw=2))

    # Summation node
    circle = Circle((2.5, 2.0), 0.6, fill=True, facecolor='lightblue', edgecolor='black', lw=2)
    ax.add_patch(circle)
    ax.text(2.5, 2.0, "Σ", fontsize=16, ha='center', va='center', fontweight='bold')

    # Bias
    ax.text(2.5, 0.2, f"bias = {bias:.1f}", fontsize=10, ha='center')

    # Threshold
    ax.text(3.5, 2.0, f"Σ(wx) + bias > 0", fontsize=11, ha='center')

    # Output
    rect = FancyBboxPatch((4.0, 1.5), 0.8, 1.0, boxstyle="round,pad=0.1",
                          facecolor='lightgreen', edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(4.4, 2.0, "y", fontsize=14, fontweight='bold', ha='center', va='center')

    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# Example: AND gate
draw_neuron([1.0, 1.0], -1.5, "AND Gate (MCP Neuron)")

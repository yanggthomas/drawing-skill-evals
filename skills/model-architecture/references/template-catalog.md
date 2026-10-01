# Bundled template catalog

Use the smallest template that matches the model mechanism. Copy its `.tex` into the task output directory before editing it, and inspect the adjacent metadata for parameters, semantic node names, and invariants.

| Template | Use when | Source |
|---|---|---|
| `assets/self-attention-template.tex` | Self-attention with shared Q/K/V source, score formation, softmax, value mixing, output projection, and residual path | Local validated template designed for this skill |
| `assets/encoder-decoder-cross-attention-template.tex` | Canonical encoder-decoder cross-attention: decoder query/residual stream and encoder K/V memory | Local validated template designed for this skill |
| `assets/open-tikz/templates/neural-net/template.tex` | A conventional feed-forward network with parametric layer sizes | OpenTikZ CC0 |
| `assets/open-tikz/templates/encoder-decoder/template.tex` | Encoder-decoder, bottleneck, latent representation, or hourglass layouts | OpenTikZ CC0 |
| `assets/open-tikz/templates/resnet-block/template.tex` | Residual blocks, skip connections, and repeated transformation stacks | OpenTikZ CC0 |
| `assets/open-tikz/examples/flash-attention/figure.tex` | Attention data movement, tiled operators, memory hierarchy, or multi-panel attention explanations | OpenTikZ CC0; use as a visual grammar rather than a universal template |
| `assets/open-tikz/examples/lora/figure.tex` | Low-rank branches, parallel projections, merge paths, and equation-centred comparisons | OpenTikZ CC0; use as a visual grammar rather than a universal template |

The imported assets were selectively copied from [OpenTikZ](https://github.com/opentikz/opentikz). Their figure content is released under CC0 1.0; the bundled license text is at `assets/open-tikz/CC0-1.0.txt`. The full OpenTikZ skill is intentionally not bundled because its system-diagram and flowchart scope would overlap Graphviz and Mermaid routing.

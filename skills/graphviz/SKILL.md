---
name: graphviz
description: Draw consistent Graphviz (.dot) diagrams for software and system architecture, dependencies, infrastructure or runtime data flow, mind maps, concept hierarchies, and other topology-first graphs that benefit from automatic layout. Do not use for UML diagrams, or for publication-style ML model figures containing tensor stacks, equations, attention internals, layer operators, or paper-figure reconstruction.
---

## When to use

- Software/system architecture, dependency graphs, infrastructure or runtime data flow, concept graphs, and tree/hierarchy diagrams
- Mind maps where colored semantic branches and automatic layout matter
- Anything where node *role* (top-level system, supporting concept, external tool, etc.) should be visually distinguishable at a glance
- **Not** for UML diagrams (sequence, class, state, activity) — use Mermaid for those; Mermaid's UML semantics add value that Graphviz doesn't replicate
- **Not** for publication-style neural-network or mathematical model architecture: tensor shapes/stacks, attention or transformer internals, equations, operator-level blocks, precise residual paths, and reconstruction of figures from papers or screenshots belong to the `$model-architecture` TikZ skill

## Template selection

- Use `references/style-template.dot` for software/system architecture, dependencies, infrastructure, and runtime data flow.
- Use `references/xmind-cluster-style-template.dot` for mind maps and concept trees. Preserve one hue per semantic branch and use lighter variants toward the leaves.
- Do not choose a Graphviz template solely because the request contains the word "architecture". Determine whether the subject is system topology (Graphviz) or mathematical/model internals (`$model-architecture`).

## Workflow

1. Select and copy the appropriate template above (or apply its conventions to an existing `.dot` file)
2. Assign each node one of the 7 semantic classes below based on its role — do not invent new colors/shapes ad hoc
3. Render: `dot -Tpng <name>.dot -o <name>.png`
4. Reference the rendered `.png` from markdown — never embed raw dot source inline in prose

## Semantic color palette (node classes)

| Class       | Shape       | Use case                          | Fill                      | Border                   |
| ----------- | ----------- | ---------------------------------- | -------------------------- | -------------------------- |
| `primary`   | hexagon     | Top-level system, main anchor      | `#F4A261` (warm orange)    | `#E76F51` (coral)          |
| `secondary` | ellipse     | Default node, supporting concept   | `#E8F4FD` (light blue)     | `#2E86AB` (medium blue)    |
| `accent`    | hexagon     | Key branching point, supervisor    | `#F4D35E` (yellow)         | `#D68A1A` (gold)           |
| `workflow`  | rounded box | Process, pipeline, fixed sequence  | `#E1BEE7` (light purple)   | `#6A1B9A` (purple)         |
| `swarm`     | folder      | Peer mesh, collaborative group     | `#FFCDD2` (light pink)     | `#B71C1C` (dark red)       |
| `tool`      | cylinder    | External resource, service         | `#FFF2B2` (light yellow)   | `#B8860B` (dark gold)      |
| `muted`     | ellipse     | External dependency, out-of-scope  | `#F5F5F5` (light grey)     | `#CCCCCC` (dashed)         |

## Edge styling

- Default: `color="#555555"` (neutral grey)
- Prefer `splines=curved` for smooth Bézier connections; it is especially important for mind maps and concept trees
- Use straight or orthogonal routing only when it materially clarifies dense system topology or ordered data flow
- Highlighted connection: use the source node's border color
- External/loose dependency: `style=dashed`

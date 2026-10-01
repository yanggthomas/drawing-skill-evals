---
type: llm
focus: { source: file, path: out/mixed-batch-attn.png }
---

You are grading the visual quality of a technical diagram (the attached PNG). Ignore whether its content is technically correct; grade only how readable it is.

Check each criterion:
1. Every label is legible at 100% zoom: no text is truncated, clipped, or too small to read.
2. No nodes overlap, and no labels overlap nodes, edges, or each other.
3. There is one clear reading direction (top-to-bottom or left-to-right) that a reader can follow from start to end.
4. Edges are distinguishable: a reader can trace each edge from its source to its target, and edges that mean different things (e.g. control flow vs. data handed off) are visually different or labeled.
5. The visual grammar is consistent: shape and/or colour encode the role of a node (e.g. decision, action, data structure, queue), and the same role always looks the same.
6. There are no orphan nodes (unconnected, without an obvious reason) and no purely decorative elements.

PASS if criteria 1, 2 and 3 all hold and at most one of criteria 4–6 fails.
FAIL otherwise. Begin your explanation by giving a pass/fail for each criterion number.

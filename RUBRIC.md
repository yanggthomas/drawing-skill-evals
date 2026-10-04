# Baseline Rubric

Score every image on five dimensions, each an integer from 1 to 5. This is a starting point: refine it as described in `CLAUDE.md`, and record the final version in `results/RUBRIC-FINAL.md` before scoring.

| Dimension | What it measures |
|---|---|
| Fidelity | Whether arrows, labels, shapes, ownership, ordering, and examples match the grounded source behavior |
| Coverage | Whether the diagram includes the relationships and concepts requested by the case prompt |
| Flow | Whether a reader can follow the intended path and hierarchy without reconstructing the layout |
| Legibility | Whether text, spacing, crossings, and aspect ratio remain usable at a normal viewing size |
| Visual encoding | Whether color, grouping, symbols, and polish communicate meaning consistently |

## Anchors

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Fidelity | Several material errors, or one error that inverts the core mechanism | One material error, or several minor inaccuracies | Every checked claim matches the source; at most cosmetic slips |
| Coverage | Most requested relationships are missing | The core is present; some requested elements are missing or only implied | Everything the prompt asks for is shown explicitly |
| Flow | The reader must reconstruct the path; the reading order is unclear | The main path is followable with effort; some backtracking or ambiguity | The intended path and hierarchy read at a glance |
| Legibility | Text is unreadable at normal size, or overlaps and crossings obscure content | Readable with zooming; some crowding, crossings, or an awkward aspect ratio | Comfortable to read at normal size; clean spacing |
| Visual encoding | Color and shape are arbitrary or misleading | Mostly consistent, with some unexplained or decorative encoding | Color, grouping, and symbols carry consistent meaning, with a legend where needed |

A **material error** misstates something the diagram exists to explain: a wrong connector or direction, wrong ownership or process placement, a wrong tensor shape, a wrong ordering, or an invented component. A **minor inaccuracy** is a loose label, an imprecise name, or a simplification that a reader would not act on wrongly.

## Totals

- `total_25` = sum of the five dimensions.
- `technical_30` = `total_25` + Fidelity. These diagrams explain code and system behavior, so fidelity counts twice.
- Polish cannot compensate for a material error: a persuasive diagram that is wrong is worse than a plain one that is right.

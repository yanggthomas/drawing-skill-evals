# Final Rubric (applied uniformly to all 54 images)

This is `RUBRIC.md` with sharpened anchors, explicit caps, and a few case-driven
clarifications. It was written after reading all nine prompts, answer keys, and
the key-cited source lines, and **before viewing any image**. Every image is
scored against this document only; no image is scored relative to the other
five in its case.

## Dimensions (each an integer 1–5)

| Dimension | What it measures |
|---|---|
| Fidelity | Whether arrows, labels, shapes, ownership, ordering, shapes/counts and examples match the pinned source |
| Coverage | Whether the diagram explicitly shows the relationships and concepts the **case prompt** asks for |
| Flow | Whether a reader can follow the intended path / hierarchy without reconstructing the layout |
| Legibility | Whether text, spacing, crossings, and aspect ratio are usable at a normal viewing size |
| Visual encoding | Whether color, grouping, symbols, and polish carry consistent meaning |

## Definitions

**Material error** — a claim the diagram exists to make that would lead a reader
to a wrong model of the system. Concretely, for these nine cases:

- wrong process / thread / node / pool placement of a component (A1, A2, A3, G2, G3, G4);
- wrong transport, socket type, or direction on a link (A1, A2);
- wrong group membership, rank formula, or group count (A3);
- wrong tensor or weight shape, or a collective placed on the wrong side of a
  layer or in the wrong direction (M1), wrong index arithmetic (M2);
- wrong ordering of stages in a step diagram, or a stage placed on the wrong side
  of a driver/worker boundary (G1, G2, G4);
- a queue, thread, or component that does not exist in the source, or a real
  component drawn as something it is not (all cases);
- a mechanism inverted (e.g. "I/O thread executes commands", "waiting is
  scheduled before running", "preemption victim goes to the back of the queue").

**Minor inaccuracy** — a loose or imprecise label, a slightly wrong default
number, a simplification that collapses detail without changing what a reader
would do, or a stale/alternate name for a real component. An unverifiable but
plausible embellishment that does not contradict the source is minor.

**Not a defect** — omitting something the prompt did not ask for; simplifying a
rarely-used branch (e.g. DP, LoRA, non-colocated sync) when the main path is
right; using a different but equivalent concrete example than the key.

**Garbled text** — glyph-shaped marks that do not form words. Garbled labels are a
Legibility defect, not a Fidelity defect, unless the fragments readable in them
assert something false. A box whose label cannot be read earns no Coverage
credit for whatever it was meant to show.

## Anchors

### Fidelity (capped by material errors — the cap is absolute)

| Score | Anchor |
|---|---|
| 5 | Every checked claim matches the source; at most one or two cosmetic slips (e.g. a method name slightly off) |
| 4 | No material error; a few (≤3) minor inaccuracies |
| 3 | **Exactly one** material error, or many (≥4) minor inaccuracies that together blur the mechanism |
| 2 | **Two** material errors, or one material error plus several minor ones |
| 1 | **Three or more** material errors, **or** one error that inverts the core mechanism the prompt asks about |

Caps: one material error → Fidelity ≤ 3; two → ≤ 2; three or an inverted core mechanism → 1.
Polish never lifts the cap.

### Coverage (judged against the prompt's enumerated asks, with the key as the reference for what "shown" means)

| Score | Anchor |
|---|---|
| 5 | Every item the prompt enumerates is shown explicitly and labelled, including the "how" (e.g. the rule, the transport, the shapes), not only the "what" |
| 4 | All items present; one is only implied or shown without its mechanism |
| 3 | The core is present; two items missing or only implied |
| 2 | Roughly half of the asks are missing |
| 1 | Most requested relationships are missing, or the diagram answers a different question |

Items a diagram gets *wrong* still count as "present" for Coverage; they are
penalised under Fidelity. Items that are illegible count as absent.

### Flow

| Score | Anchor |
|---|---|
| 5 | Reading order and hierarchy are obvious at a glance; step diagrams have a clear start, numbered or ordered stages, and loops/branches are drawn as such; architecture diagrams nest containment correctly |
| 4 | Main path clear; one place needs a second look (a back-edge, an unlabelled branch) |
| 3 | Main path followable with effort; some backtracking, ambiguous arrow direction, or mixed reading directions |
| 2 | Several paths compete; the reader has to guess what comes first or what contains what |
| 1 | No discernible path; the reader must reconstruct the mechanism from scattered labels |

### Legibility (at "normal size" = the whole image fitted to a ~1600 px wide screen; zooming is allowed but costs points)

| Score | Anchor |
|---|---|
| 5 | Comfortable at normal size; clean spacing; no overlapping text; aspect ratio between ~1:1 and ~2:1 |
| 4 | Readable at normal size with minor crowding or a few small labels; or a mildly awkward aspect ratio (2:1–2.5:1, or 1:1.5) |
| 3 | Readable only with zooming; crowding, crossings, or an aspect ratio beyond 2.5:1 or taller than 1:2 that forces scrolling |
| 2 | Significant overlaps / truncated labels / clipped content, or a meaningful fraction (≈10–30 %) of labels garbled |
| 1 | Most text unreadable or garbled; content clipped off the canvas; or overlaps obscure the structure |

### Visual encoding

| Score | Anchor |
|---|---|
| 5 | Colour/shape/line-style map one-to-one to meaning (process, thread, GPU, data type, direction); a legend exists where the mapping is not self-evident; grouping boxes match real boundaries |
| 4 | Mostly consistent; one unexplained or decorative encoding, or a legend that is incomplete |
| 3 | Some meaning carried by colour/shape, but with inconsistencies (same colour for different kinds, same kind in different colours) or no legend where one was needed |
| 2 | Encoding mostly decorative; grouping boxes do not correspond to real boundaries |
| 1 | Colour and shape are arbitrary or actively misleading |

## Totals

- `total_25` = Fidelity + Coverage + Flow + Legibility + Visual encoding.
- `technical_30` = `total_25` + Fidelity (fidelity counts twice).

## Changes from `RUBRIC.md`, with reasons

1. **Numeric caps on Fidelity** (1 material → ≤3, 2 → ≤2, 3+ or inverted core → 1).
   The baseline said "capped" but gave no number; without one, two scorers could
   put the same two-error diagram at 2 or 3. The cap is stated as absolute so
   polish cannot leak into Fidelity.
2. **Case-specific list of what counts as material.** The baseline's list
   (connector, ownership, shape, ordering, invented component) is kept and
   mapped to the nine cases so the same kind of error is treated the same way
   in every case — e.g. a wrong socket type in A1 and a wrong collective
   direction in M1 are both material.
3. **Garbled text rule.** Several image sizes (1536×1024, 1672×941) suggest some
   images may be rasterised with imperfect text. The baseline did not say where
   garbled text is penalised; it is now Legibility (and Coverage, since an
   unreadable box shows nothing), not Fidelity, unless the readable fragments
   assert something false. This keeps Fidelity about correctness, not rendering.
4. **Coverage is against the prompt, not the key.** The key is explicitly "a
   reference, not an exhaustive list". Coverage counts the prompt's enumerated
   asks; the key only tells us what a complete answer to each ask looks like.
   Wrong-but-present items count for Coverage and are penalised in Fidelity, so
   the same fact is not double-counted.
5. **Aspect-ratio thresholds for Legibility.** Several images are extreme
   (0.30, 0.54, 2.49). The baseline said "awkward aspect ratio" without a
   threshold; thresholds are now explicit so tall scroll-diagrams and wide
   banners are treated consistently.
6. **"How, not only what" clause in Coverage 5.** Prompts ask for *rules* (A3),
   *transports* (A1), *shapes* (M1), *index arithmetic* (M2). A box labelled
   "ZMQ" without socket types, or "all-gather" without a shape, is Coverage 4
   territory, not 5. This separates diagrams that name things from diagrams
   that explain them.
7. **Flow 5 requires drawn loops/branches for step diagrams.** G1/G2/G3/G4 are
   loop-shaped mechanisms; a linear list of boxes that hides the loop is
   followable but does not show the mechanism's shape.
8. **Explicit "not a defect" list.** Prevents penalising a diagram for leaving
   out DP/LoRA/elastic-EP branches or for using a different concrete example
   than the key.

## Procedure notes (binding on the scorer)

- Read prompt, key, and cited source lines before viewing any image in a case.
- View all six images of a case (tiling large ones at native resolution) before
  writing any score for that case.
- Every recorded defect cites `key#N` or `src/<path>:<line>` and states
  material / minor.
- Score each image against the anchors above; do not adjust a score because of
  how the other five in the case look.
- If any anchor is changed after scoring begins, rescore every image already scored.

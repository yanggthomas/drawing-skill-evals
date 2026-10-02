# Visual QA

Generated using exactly one built-in image_gen call, no reference images and no editing or regeneration. Inspected the returned image directly at full rendered size.

## Verified

- All 16 ranks occur exactly once in the lattice, in the correct four-by-four arrangement.
- Node 0 contains 0–7; Node 1 contains 8–15. The contiguous launcher placement assumption is explicitly stated.
- TP brackets and TP directory sets are correct.
- PP vertical columns and directory sets are correct.
- All eight DP directory sets are correct.
- Both MP shaded bands and directory sets are correct; each MP group spans both nodes.
- All four embedding directory sets are correct. The text correctly excludes ranks 4–11.
- Formula r=t+2d+4p, default effective ordering, axis ranges, and DP=2 calculation are correct.
- Source footer is present; main text is readable with no clipping.

## Errors and limitations

- The gold embedding endpoint rings appear only on ranks 0, 3, 12, and 15. They are missing on ranks 1, 2, 13, and 14. Therefore the lattice's embedding highlighting is incomplete, even though the complete embedding group directory is correct.
- DP memberships are communicated by the group directory, not by connecting lines in the lattice.
- The source footer is small at the generated 1536×1024 resolution, although readable when enlarged.

## Artifact

`out/parallel-groups.png` is the unmodified image returned by the single generation call.

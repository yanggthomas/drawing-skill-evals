# Evaluation Methodology

Each case is grounded in pinned source and asks for one PNG. Skill ablations use fresh Claude sessions with and without the plugin. The Codex + ImageGen arm used one fresh subagent and one image-generation call per case, without reference images or best-of-N selection.

Automated Claude grader scores remain distinct from the later 27-image Codex review. The manual-style review scores factual fidelity, requested coverage, reading flow, legibility, and visual encoding from 1–5. Its technical score counts fidelity twice.

Production cost excludes graders. Claude costs are observed values from run traces. Codex reasoning cost is reconstructed from recorded uncached input, cached input, and output tokens. Image output cost is an estimate because the built-in tool does not expose its backend quality setting.

Color consistency combines human assessment with mean pairwise intersection of 12-bin hue histograms after excluding neutral and low-value pixels. The histogram metric measures palette similarity, not whether colors retain the same semantic meaning.

Every conclusion must link to immutable run artifacts. Comparisons may interpret runs but may not rewrite their raw evidence.

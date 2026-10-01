---
type: regex
target: { source: file, path: out/schedule-step.dot }
flags: i
pattern: '^(?=[\s\S]*running)(?=[\s\S]*waiting)'
---

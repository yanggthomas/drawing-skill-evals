# 评测运行归档

每次评测一个目录，skill 评测命名为 `<日期>-skill-v<插件版本>`，其他生成路线使用 `<日期>-<agent>-<renderer>-v<运行版本>`。目录里放这次运行的结果、报告、产物和评价；case 定义统一放在 `evals/`。

| 运行 | 被测 skill | case | 状态 |
|---|---|---|---|
| [2026-10-01-skill-v0.1.0](2026-10-01-skill-v0.1.0/README.md) | drawing-skills 0.1.0 | G1–G4、M1–M2、A1–A3（真正在 graphviz 主场的只有 A1、A2） | ⚠ 评测设计有问题，分数不能用来判断 skill，见 [LIMITATIONS](2026-10-01-skill-v0.1.0/LIMITATIONS.md) |
| [2026-10-01-codex-imagegen-v1](2026-10-01-codex-imagegen-v1/README.md) | Codex + image generation（独立生成路线） | G1–G4、M1–M2、A1–A3 | 9 张首次生成图；每题独立上下文；27 张三路线复核、成本与风格一致性见 [MANUAL-SCORES](2026-10-01-codex-imagegen-v1/MANUAL-SCORES.md)，图片见 [Gallery](2026-10-01-codex-imagegen-v1/GALLERY.md) |

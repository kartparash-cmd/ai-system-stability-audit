# Shared review contract — ai-system-stability-audit skill

Target: /Users/kartikeyaparashar/.claude/skills/ai-system-stability-audit/ (SKILL.md, rubric.yaml, scoring.md, EVOLUTION.md, CHANGELOG.md, PROPOSALS.md, history/). It audits AI/agent/RAG codebases against 8 weighted pillars (50 checks, 0/1/2 evidence-cited scoring, all with scoring anchors), writes timestamped audit-history JSONs for longitudinal deltas, and has an approval-gated self-evolution loop (models file proposals; the owner applies them in evolve mode). Review the CURRENT files fresh — multiple hardening passes have already run; do not assume previously-reported defects still exist.

Score these 7 dimensions 0–10, one line of evidence each:

- D1 Mathematical correctness — recompute the formulas and worked examples by hand (pillar %, weighted overall, N/A renormalization Rules A/B, gap impact, half_up rounding incl. negatives, band assignment, gap-sum aggregation).
- D2 Internal consistency — cross-file agreement: check IDs, semver policy, bands, mode lists, proposal-ID format, cross-references. Count contradictions.
- D3 Fresh-model executability — could a model with zero prior context run every mode end-to-end with no guessing? Count remaining ambiguities.
- D4 Determinism — two different models, same repo: identical numbers, slugs, filenames, orderings, anchor-guided scores?
- D5 Trigger precision — frontmatter description fires on right asks, silent on wrong ones (collisions with /cso, /absence-detector, code-review skills); char count vs the 1024 hard cap.
- D6 Evolution-loop integrity — any path where rubric/scoring/engine changes without explicit owner approval? ID collisions under concurrent audits? Ledger gaps? Post-evolve verification coverage?
- D7 Measurability coverage — fraction of mandated output elements carrying a number and/or check ID/path. The owner's requirement is 100%: no prose-only element.

Overall = ((D1+D2+D3+D4)×2 + D5+D6+D7) / 11, one decimal.

Scoring calibration — be strict but honest: award a 10 when you cannot name one concrete, actionable finding for that dimension; do NOT withhold points reflexively or invent style nits to justify a 9. Every finding must include: file + section/line, severity (critical | major | minor), one-sentence defect, QUANTIFIED impact (points of swing, % of runs affected, counts — a real number, never "significant"), and a concrete fix. A finding without a quantified impact is invalid — drop it. Do not report anything you have not verified against the current file content. Do not modify any files.

## Versioning

This contract is the judge rubric for tri-model panel reviews of this skill. Changes to it are versioned in git — any edit to the dimensions, weights, or calibration rules is a rubric change and must land as a tracked commit, so every score in the log is traceable to the exact contract text it was scored against. Each panel run records its scores as one line in `reviews/log.jsonl`.

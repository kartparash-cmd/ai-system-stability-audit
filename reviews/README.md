# Recurring judged evals — panel review policy

This directory is the skill's own LLM-as-judge eval loop (rubric check P3): a versioned
judge rubric plus a per-run score log.

## Panel

Three independent reviewers, each given the same `review-contract.md` and a fresh
context (no prior findings, no shared state):

1. A **Fable-class Claude agent** (claude-fable-5)
2. An **Opus-class Claude agent** (claude-opus-4-x)
3. **OpenAI Codex CLI** (cross-vendor check)

Each reviewer scores 0–10 on the 7 dimensions defined in `review-contract.md` (D1–D7)
and computes the weighted overall `((D1+D2+D3+D4)×2 + D5+D6+D7) / 11`, one decimal.
Every finding must carry file+line, severity, and a quantified impact — unquantified
findings are dropped per the contract.

## Judge rubric versioning

The judge rubric IS `review-contract.md`, checked into git. Any change to its
dimensions, weights, or calibration rules is made by commit, so each `log.jsonl` line
is traceable to the exact contract text in effect at that commit. Scores are recorded
per run (see below) — the two P3 anchor-2 requirements.

## Cadence

- **Before every MINOR or MAJOR rubric release** — the panel runs against the release
  candidate; release proceeds only after the run is logged.
- **At least monthly** while the skill is actively developed, even with no release
  pending.

## Recording

Each panel run appends exactly one line to `log.jsonl`:

```json
{"date", "round", "trigger", "reviewers": {"fable": {"overall"}, "opus": {"overall"}, "codex": {"overall"}}, "avg", "findings": {"critical", "major", "minor"}, "notes"}
```

`round` is monotonic. A reviewer absent from a run records `"overall": null` (round 0
predates the Fable reviewer). `avg` is the mean of the non-null overalls, 2 decimals.

## Regression gate

A drop **>0.5** in any single reviewer's overall vs. the previous round must be
investigated before release — read that reviewer's findings, classify the drop as
(a) real regression, (b) contract change, or (c) instance variance, and note the
verdict in the run's `notes`.

## Known variance

Fresh instances of the same reviewer on identical content vary by about **±0.7**
overall. Single-round moves inside that band are noise; **trends across rounds matter
more than any single round**. The regression gate above exists to force the
investigation, not to auto-fail a release on one noisy number.

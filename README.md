# ai-system-stability-audit

A Claude Code skill that scores an AI, agent, LLM, or RAG codebase for production stability. It produces a weighted, evidence-cited scorecard across **8 pillars** and **50 anchored checks**, with every gap ranked by its exact point impact on the overall score.

## How it works

- **8 pillars, weighted to 100:** Govern (20), Prove (20), Decision Engine (14), Context & Data (12), Orchestration & Humans (10), Shared Platform (10), Rollout Maturity (8), NFR Foundations (6). Pillars and checks live in `rubric.yaml`, a versioned data file separate from the audit engine (`SKILL.md`).
- **50 anchored checks**, each scored 0 (absent), 1 (partial), or 2 (present and enforced), with per-check scoring anchors and evidence hints. Coverage includes prompt-injection defense, tool/MCP security, agent sandboxing, supply-chain pinning, and memory hygiene.
- **Evidence or zero:** every 1 or 2 must cite a concrete file path, function, config key, or infrastructure definition. README claims earn nothing. An uncited score is downgraded to 0. N/A requires a one-sentence argument and is excluded from denominators.
- **Weighted % + maturity bands:** pillar percentages roll up into a weighted overall percentage mapped to a band — Fragile (<40.0), Developing (40.0–<60.0), Production-Capable (60.0–<80.0), Production-Grade (≥80.0). All formulas, rounding rules, and the audit-history JSON schema are in `scoring.md`; two models given the same per-check scores produce bit-identical derived numbers.
- Every full/gaps/compare audit writes a history JSON to `history/`, enabling deltas across audits of the same repo.

## Install

```bash
git clone https://github.com/kartparash-cmd/ai-system-stability-audit.git ~/.claude/skills/ai-system-stability-audit
```

Then, in Claude Code, ask for an audit (e.g. "audit my AI system") or invoke the skill directly.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| **full** (default) | "audit", "score this repo" | Complete scorecard: pillar table, detailed findings, top-10 gaps, top 5 risks, prioritized fixes |
| **gaps** | "gaps", "what's missing" | Ranked misses only — every non-2 check with its point impact, plus risks and fixes |
| **compare** | "compare", "re-audit", "delta" | Full audit plus per-pillar and per-check deltas vs. the most recent prior audit of the same repo |
| **partial** | "partial: <pillar names>" | Audits only the named pillars; no overall %, no history write |
| **evolve** | "evolve", "review proposals", "apply proposals" | Reviews pending rubric proposals with impact analysis; the skill owner accepts/rejects/defers each |
| **trend** | "trend", "trajectory" | Per-check score trajectories, never-moved checks, N/A frequency across ≥3 history entries; reporting only; same-day entries collapse to the day's latest |
| **dry-run** prefix | "dry-run audit", etc. | Any audit mode (full, gaps, compare, partial), skipping the history write and proposal filing; evolve has no dry-run |

## Example scorecard fragment

> Illustrative — from scoring.md's 43-check 1.0.0 worked example; live rubric is 3.0.0 with 50 checks.

```
# AI System Stability Scorecard: helpdesk-bot

Rubric v1.0.0 | 2026-07-29 | target: ~/dev/helpdesk-bot | 47 of 312 tracked files examined (15.1%), 11 configs | model: claude-fable-5

Overall adherence: 38.3% (Fragile)
Evidence density: 58.5% (24 of 41 applicable checks citable) | distinct evidence paths: 23

| Pillar | Score | Strongest evidence | Biggest gap |
|---|---|---|---|
| Govern | 42.9% | G1: require_role() on every route (src/auth/middleware.py) | G3: no approval gate (+2.9 pts) |
| Prove  | 28.6% | P2: tests/test_output_schema.py | P3: no LLM-as-judge evals (+2.9 pts) |

## If you implement only 3 things
1. G3 — approval gates on risky actions — +2.9 pts — gate side-effecting tools behind confirm step
2. G4 — immutable audit trail — +2.9 pts — append-only log of every tool call
3. G5 — human override mechanism — +2.9 pts — documented way to supersede any agent decision
```

## Self-evolution loop

- Every audit must file 1–3 rubric improvement proposals to `PROPOSALS.md`, grounded in audit friction, tech development, or history signal — never "would be nice".
- Proposals are never auto-applied; every audit is scored against the current `rubric.yaml` only.
- Guardrails reject proposals that weaken evidence requirements, inflate scores, or remove checks without deprecation rationale.
- In evolve mode, each proposal gets a review card with a guardrail check and a rescore of past `history/` entries under the proposed rubric; the skill owner decides each one.
- Accepted changes bump `rubric_version` by semver, get a `CHANGELOG.md` entry, and move the proposal to an Accepted/Rejected ledger so future models do not re-propose settled ideas.

## Metrics glossary

| Metric | Definition |
|---|---|
| Overall % | Weighted average of pillar percentages (pillar % = score_sum / (2 × applicable checks)); N/A pillars trigger weight renormalization. Mapped to a maturity band. |
| Evidence density | Applicable checks scored 1–2 with a concrete citation, divided by all applicable checks. What fraction of the rubric the codebase can prove. |
| distinct_evidence_paths | Count of distinct concrete file paths cited in the evidence of checks scored 1 or 2; directories, glob patterns, and score-0 search targets are excluded (worked example: 23). Falsifiable companion to evidence density. |
| Gap impact | Exact overall-percentage points gained by raising one check to 2: headroom / (2 × pillar applicable checks) × normalized pillar weight. All gap impacts sum to 100 − overall %. |
| Coverage | Files examined / tracked files (`git ls-files`), plus config count. Context for the audit's depth, never a grade. |

## Files

- `SKILL.md` — the audit engine: procedure, modes, output template
- `rubric.yaml` — versioned rubric: pillars, checks, weights, anchors, evidence hints
- `scoring.md` — all formulas, rounding rules, history JSON schema, worked examples
- `EVOLUTION.md` — the self-improvement protocol and evolve-mode procedure
- `PROPOSALS.md` — pending/accepted/rejected rubric proposals
- `CHANGELOG.md` — rubric version history
- `README.md` — this overview
- `LICENSE` — MIT license text
- `history/` — one JSON per audit (gitignored by default except the committed worked example — see Privacy below)

Mechanical integrity tooling:

- `scripts/validate.py` — validates rubric.yaml structure and cross-file consistency
- `.github/workflows/validate.yml` — CI: runs the validator on every push/PR
- `.githooks/pre-commit` — local pre-commit gate running the same validation
- `tests/golden/` — golden fixture the validator checks scoring math against

## Privacy and the history/ directory

Audit history JSONs contain evidence strings and file manifests **from the repos you audit** — file paths, function names, and config keys of potentially private codebases. To keep those details from ever reaching a public remote, `history/*.json` is gitignored by default. The one committed entry, `history/ai-system-stability-audit-2026-07-30-064451.json`, is a deliberately kept worked example whose audit target is this same public repo — zero leak by construction. If you want durable audit history, back up `history/` privately (it is not covered by pushes of this repo). Deleting a history file is the supported purge path.

## Repo integrity gate

After cloning, run once:

```bash
git config core.hooksPath .githooks
```

This activates the pre-commit gate (`.githooks/pre-commit`), which validates the rubric and cross-file consistency before every commit. CI (`.github/workflows/validate.yml`) enforces the same rules on push and PR.

## Model calibration and pinning

The model that executes an audit is chosen by the Claude Code harness, not by this repo — there is no model config to pin. The repo pins by **policy** instead:

- Every audit records the exact lowercased model id in its history JSON (`model` field, scoring.md §4.1), so every score is permanently attributable to the model that produced it.
- The golden fixture (`tests/golden/`) was calibrated on `claude-fable-5` (46/50 first-run check-level agreement, 2026-07-30).
- Before trusting scores produced by any other model, run the golden audit under that model and record its agreement rate here.
- Score comparisons across history entries with different `model` values are trend signal, not regression proof — only same-model, same-rubric deltas are directly comparable.

| Model | Golden agreement | Calibrated |
|---|---|---|
| `claude-fable-5` | 46/50 | 2026-07-30 |

### Supply chain

Zero runtime dependencies by design: the skill itself is markdown + YAML read by the harness, and `scripts/validate.py` uses only the Python stdlib plus `pyyaml` — which is installed in CI only, pinned to an exact version. CI actions in `.github/workflows/validate.yml` are pinned to full commit SHAs. Repo integrity is enforced by the pre-commit gate (`.githooks/pre-commit`), the CI rubric gate (rule G2), and git history.

## License

MIT — see [LICENSE](LICENSE).

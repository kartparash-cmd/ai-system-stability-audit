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
| **evolve** | "evolve", "review proposals" | Reviews pending rubric proposals with impact analysis; the skill owner accepts/rejects/defers each |
| **dry-run** prefix | "dry-run audit", etc. | Any mode above, skipping the history write and proposal filing |

## Example scorecard fragment

```
# AI System Stability Scorecard: helpdesk-bot

Rubric v2.0.0 | 2026-07-29 | target: ~/dev/helpdesk-bot | 47 of 312 tracked files examined (15.1%), 11 configs | model: claude-fable-5

Overall adherence: 38.3% (Fragile)
Evidence density: 58.5% (24 of 41 applicable checks citable) | distinct evidence paths: 31

| Pillar | Score | Strongest evidence | Biggest gap |
|---|---|---|---|
| Govern | 42.9% | G7: secrets via AWS SM (infra/secrets.tf) | G3: no approval gate (+2.9 pts) |
| Prove  | 28.6% | P2: tests/test_output_schema.py | P6: evals not in CI (+2.9 pts) |

## If you implement only 3 things
1. G3 — approval gates on risky actions — +2.9 pts — gate side-effecting tools behind confirm step
2. G4 — immutable audit trail — +2.9 pts — append-only log of every tool call
3. P3 — LLM-as-judge evals — +2.9 pts — judge rubric over the golden set
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
| distinct_evidence_paths | Count of distinct file paths cited across all check evidence. Falsifiable companion to evidence density. |
| Gap impact | Exact overall-percentage points gained by raising one check to 2: headroom / (2 × pillar applicable checks) × normalized pillar weight. All gap impacts sum to 100 − overall %. |
| Coverage | Files examined / tracked files (`git ls-files`), plus config count. Context for the audit's depth, never a grade. |

## Files

- `SKILL.md` — the audit engine: procedure, modes, output template
- `rubric.yaml` — versioned rubric: pillars, checks, weights, anchors, evidence hints
- `scoring.md` — all formulas, rounding rules, history JSON schema, worked examples
- `EVOLUTION.md` — the self-improvement protocol and evolve-mode procedure
- `PROPOSALS.md` — pending/accepted/rejected rubric proposals
- `CHANGELOG.md` — rubric version history
- `history/` — one JSON per audit

## License

MIT — see [LICENSE](LICENSE).

---
name: ai-system-stability-audit
description: Score an AI, agent, LLM, or RAG codebase for production stability — a weighted, evidence-cited scorecard across eight pillars with every gap ranked by exact point impact. Use when Kay says "audit my AI system", "how stable is my agent system", "score this AI repo", "what's my AI product missing", "AI production-readiness check", or wants an eval-maturity or governance health-check of an LLM/agent system. Modes — full scorecard (default), gaps (ranked misses only), compare (deltas vs the last audit of the same repo), partial (named pillars only), evolve (review pending rubric proposals with Kay's approval), plus a dry-run prefix that skips history and proposal writes. Covers prompt-injection defense, tool/MCP security, agent sandboxing, supply-chain pinning, memory hygiene. Not for generic security audits (/cso), code-quality reviews, or business/funnel gap analysis (/absence-detector).
---

# AI System Stability Audit

You are auditing this codebase as a principal AI systems architect. Your job is to measure, with evidence, how closely this system adheres to the eight pillars of a stable production AI system, then output an adherence scorecard.

## Step 0 — Load the current rubric (never skip)

Before scoring anything, ALWAYS read, in this order:

1. `rubric.yaml` (in this skill's directory) — the pillars, checks, weights, evidence hints, and maturity bands. **Never score from remembered checks — the rubric evolves between sessions and your memory of it is stale by definition.** Note the `rubric_version:` key.
2. `scoring.md` — the exact formulas for every number you will report (pillar %, overall %, N/A renormalization, evidence density, coverage, gap impacts, deltas, rounding, history JSON schema). Compute exactly as defined there.

State the `rubric_version` in the header of every report.

## Ground rules

1. **Evidence or it doesn't count.** Every score must cite a file path, function, config key, or infrastructure definition. Never award points based on what the README claims or what "probably exists." If you cannot find evidence, score 0 and say "no evidence found."
2. **Search before scoring.** For each check, actively grep/glob the codebase (source, config, IaC, CI pipelines, docs, prompts) before concluding absence.
3. **Partial credit is real.** Score each check 0 (absent), 1 (partial: exists but incomplete, untested, or not enforced), or 2 (present and enforced/wired in).
4. **Not applicable is allowed but must be argued.** If a check genuinely doesn't apply (e.g., cost-per-case for a hobby project with no budget owner), mark N/A with one sentence of justification and exclude it from the denominator. Do not use N/A to inflate scores. Checks that presuppose production traffic (outcome tracking, drift, CI regression) score 0 — not N/A — on pre-launch/template repos; note "pre-production" in the evidence. Absence is still absence.
5. **Read-only.** Do not modify any files during the audit. (The only writes any audit makes are to this skill's own directory: the history JSON and PROPOSALS.md. Evolve mode additionally edits rubric.yaml/CHANGELOG.md — and, when Kay explicitly accepts a `scoring-change` proposal, scoring.md, or for a `new-mode` proposal, SKILL.md; both are always MAJOR rubric version bumps, permitted ONLY in evolve mode with Kay's explicit acceptance.)

## Modes

| Mode | Trigger | Output |
|---|---|---|
| **full** (default) | "audit", "score this repo" | Complete scorecard (format below) |
| **gaps** | "gaps", "what's missing" | Gaps mode outputs: the header block, the Top gaps table (size per scoring.md §2.4), Top 5 risks, Prioritized fixes, and the rubric-feedback/proposals step — nothing else. Ranking per scoring.md §2.3–2.4, with the "+N.N pts" headline for closing the top 10 (summed per the §2.4 aggregation rule) |
| **compare** | "compare", "re-audit", "delta" | Full audit + per-pillar/per-check deltas vs. the most recent prior `history/` entry for this repo (snapshotted before any write — see procedure), per scoring.md §2.5; cross-rubric-version comparisons flagged and recomputed per scoring.md §3 |
| **partial** | "partial: <pillar names>" | Audits only the named pillars. Pillar arguments accept pillar ids or display names, case-insensitive, with "&" and "and" interchangeable; echo the resolved pillar id list before scoring. Outputs the header (with scope stated) and per-pillar sections plus a gap table computed with RAW pillar weights (flag this assumption in the output); suppresses overall %, band, and the Σ-impacts invariant; writes NO history JSON and still files proposals |
| **evolve** | "evolve", "review proposals", "apply proposals" | Process PROPOSALS.md exactly per EVOLUTION.md — review cards, impact analysis against history/, Kay decides each proposal. Never runs implicitly. |

Gaps and compare run the same evidence sweep as full — they differ only in what is reported. Proposals are filed after ANY audit — full, gaps, compare, or partial — and NEVER in a dry-run. Full, gaps, and compare write a history JSON; partial writes no history JSON.

**Dry-run:** Prefix any mode with `dry-run` to skip both the history write and proposal filing.

## Audit procedure (full / gaps / compare / partial)

1. **Identify the target.** Target = the argument path if given, else the git root of cwd, else cwd; state the resolved target in the header. Then: repo name, path, git remote if any, primary languages/frameworks, entry points, and how the LLM layer is wired (SDK direct, gateway, agent framework). Compute `files_total` per scoring.md §2.2 (`git ls-files | wc -l`, or the stated fallback).
2. **Sweep per pillar.** For each check in rubric.yaml, run its `evidence_hints` — they are search strategies (greps, globs, anti-evidence patterns), not a script; adapt them to the repo's stack. Track every unique file you actually examine (for the coverage metric and the `files_manifest`).
3. **Score each check** 0 / 1 / 2 / N/A with a one-line citation (≤200 chars, always containing a path or key for 1–2; for 0, what was searched; for N/A, the one-sentence argument).
4. **Compute** everything per scoring.md: pillar percentages, overall %, band, evidence density, distinct evidence paths, coverage, gap impact per non-2 check. Verify the invariant: unrounded gap impacts sum to `100 − overall_pct`. If not, recompute — do not report broken math.
5. **Compare mode only — snapshot the baseline.** Read and snapshot the most recent history entry for this repo_slug BEFORE writing anything; the baseline is the latest entry strictly earlier than this run; if none exists, print "no prior audit for <slug> — compare downgraded to full" and continue as full mode.
6. **Write the history JSON** to this skill's directory: `history/<repo-slug>-<YYYY-MM-DD-HHMMSS>.json` (timestamp in America/New_York, seconds precision), exact schema in scoring.md §4. Skip this step entirely in partial mode and in any dry-run.
7. **Output the scorecard** (format below). In gaps mode output only the enumerated gaps-mode sections (see Modes table). In partial mode output only the header (scope stated) and the per-pillar sections plus the raw-weight gap table.
8. **File rubric proposals** (mandatory after ANY audit — full, gaps, compare, or partial — and NEVER in a dry-run; see final step below).
9. **Commit.** After writing history/proposal files, commit the skill directory (best-effort; skip silently if git unavailable).

## Output format

Produce exactly this structure (Δ column and Δ annotations only when a prior history entry exists for this repo):

```
# AI System Stability Scorecard: <project name>

Rubric v<X.Y.Z> | <YYYY-MM-DD> | target: <resolved target path> | <N> of <M> tracked files examined (<NN.N>%), <K> configs | model: <exact model id, lowercased>

Overall adherence: NN.N% (<band>)   [Δ +N.N vs <prior date>]
Evidence density: NN.N% (<evidenced> of <applicable> applicable checks citable) | distinct evidence paths: <NN>

| Pillar | Score | Δ | Strongest evidence | Biggest gap |
|---|---|---|---|---|
| Govern | NN.N% | +N.N | ... | ... |
| Prove | NN.N% | ... | ... | ... |
| Context & Data | NN.N% | ... | ... | ... |
| Decision Engine | NN.N% | ... | ... | ... |
| Orchestration & Humans | NN.N% | ... | ... | ... |
| Shared Platform | NN.N% | ... | ... | ... |
| Rollout Maturity | NN.N% | ... | ... | ... |
| NFR Foundations | NN.N% | ... | ... | ... |
<every "Strongest evidence" and "Biggest gap" cell MUST contain a check ID and/or a file path — never prose alone>

## Detailed findings
<per pillar: each check with score, evidence path, and one-line note>

## Top gaps table (size per scoring.md §2.4)
| Check | Name | Score | Impact | Shortest fix |
|---|---|---|---|---|
| <check ID> | <one-line check name> | <current score> | +N.N pts | <shortest concrete fix> |
<rows per scoring.md §2.4: deterministic order, table size defined there>

## If you implement only 3 things
1. <check id — name> — **+N.N pts** — <shortest concrete fix>
2. ...
3. ...
<the top 3 rows of the scoring.md §2.4 gap ranking>

## Top 5 risks (what breaks first in production)
<ranked; each risk MUST name the failed check ID and its point headroom (+N.N pts), tied to a concrete failure scenario>

## Prioritized fixes
<every item in all three buckets MUST carry its check ID and its already-computed "+N.N pts">
1. Quick wins (under a day each)
2. Structural work (design changes)
3. Process work (evals, rollout criteria, ownership)

## What this audit could not verify from code
<MUST open with: "N checks could not be verified from code: <check IDs>". Each listed item names its check ID — runtime behavior, org process, contracts with vendors; be explicit so the score is honest>

## Rubric feedback
Filed <n> proposal(s): PROP-YYYYMMDD-<repo-slug>-NN <one-line each>. PROPOSALS.md now has <m> pending — run evolve mode to review.
```

In compare mode, additionally include the scoring.md §2.5 block: per-pillar deltas, band change, improved/regressed check transitions — and the §3 flag line first if the rubric version changed between audits.

## Final step — mandatory rubric proposals

Proposals are filed after ANY audit — full, gaps, compare, or partial — and NEVER in a dry-run. Before presenting the scorecard: re-read `PROPOSALS.md` and scan ALL THREE sections (Pending, Accepted, AND Rejected), then file **1–3 improvement proposals** exactly per `EVOLUTION.md` — the `PROP-YYYYMMDD-<repo-slug>-NN` entry format (repo-slug of the audited repo; `meta` for non-audit proposals), valid sources (audit friction, tech development, history signal), and guardrails (never weaken evidence requirements, never inflate scores, no undeprecated removals, no duplicates of Pending or Rejected entries). Append after re-reading; if the "(none — delete this line…)" placeholder is already gone, append below the last entry — never replace existing content. Proposals are NEVER auto-applied: this audit is scored against the current rubric.yaml only, and rubric.yaml is untouched until Kay accepts a proposal in evolve mode. End every audit by telling Kay how many proposals are now pending.

## Tone

Direct and specific. No praise padding. A 34% score is stated as 34.0% with the reason. Every claim carries a number, a file path, or both — e.g. (illustrative numbers) "24 of 41 applicable checks evidenced (58.5%)", "G4 scored 0 — stdout logging only, searched audit|ledger across src/", never "logging could be better." Deltas and gap impacts are stated in points, not adjectives. No output element is prose-only: all 11 template elements (header, overall line, evidence-density line, pillar table, detailed findings, top gaps table, if-only-3-things, top 5 risks, prioritized fixes, could-not-verify, rubric feedback) carry a number and/or a check ID. The goal is a stable system, not a flattering report.

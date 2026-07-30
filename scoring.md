# scoring.md — Metrics, Math, and Audit History Schema

This file is the single source of truth for every number the audit produces. Any model
running this skill MUST compute scores exactly as defined here. If two models audit the
same repo with the same per-check scores, every derived number (pillar %, overall %,
gap impacts, deltas) must be bit-identical after rounding.

Pillar IDs, check IDs, and weights come from `rubric.yaml` (current version recorded in
that file's `rubric_version:` field). The formulas below change only via an accepted
scoring-change proposal (always a MAJOR rubric version bump); otherwise only the check
set and weights change between rubric versions.

---

## 1. Base scoring (v1 — preserved exactly)

### 1.1 Per-check score

Each check receives exactly one of:

| Score | Meaning |
|---|---|
| **0** | Absent. No evidence found after actively searching. |
| **1** | Partial. Exists but incomplete, untested, or not enforced. |
| **2** | Present and enforced/wired in. |
| **N/A** | Genuinely not applicable. Requires a one-sentence justification. Excluded from all denominators. |

Every 1 or 2 MUST cite at least one concrete file path, function, config key, or
infrastructure definition. A 0 records what was searched for and not found. N/A is never
used to inflate scores.

### 1.2 Pillar percentage

```
pillar_pct = score_sum / (2 × applicable_checks) × 100
```

where `applicable_checks` = number of checks in the pillar that are not N/A, and
`score_sum` = sum of the 0/1/2 scores over those applicable checks.

If **every** check in a pillar is N/A, the pillar itself is N/A (no percentage) and its
weight is redistributed per §1.4.

### 1.3 Overall adherence percentage

```
overall_pct = Σ over applicable pillars ( pillar_pct × weight_normalized_p ) / 100
```

where for each applicable pillar p:

```
weight_normalized_p = weight_p / Σ(weight_q over applicable pillars q) × 100
```

Weights: read `pillars[].weight` in rubric.yaml (authoritative — never use a remembered
or transcribed list; the weights sum to 100). When no pillar is entirely N/A,
`weight_normalized_p = weight_p` and the overall is a plain weighted average.

**Degenerate edge:** if every pillar is N/A, the audit is not scoreable — report
"not scoreable: no applicable checks" and write no history file.

### 1.4 N/A renormalization — the two rules, explicit

**Rule A — per-check N/A (within a pillar):** remove the check from the pillar's
denominator. The pillar is scored over what remains. Pillar weights are untouched.

**Rule B — whole-pillar N/A:** remove the pillar entirely and renormalize the remaining
weights so they again sum to 100.

**Worked example of Rule B.** *Illustrative only — raw weights shown are the 2.0.0
values; take weights from the current rubric.yaml.* Suppose Rollout Maturity (weight 8)
is entirely N/A (single-user internal script, no autonomy staging possible — justified
per check). The remaining weight mass is 100 − 8 = 92. Each surviving pillar's
normalized weight:

| Pillar | Raw weight | Normalized weight |
|---|---|---|
| Govern | 20 | 20/92 × 100 = 21.739 |
| Prove | 20 | 21.739 |
| Context & Data | 12 | 13.043 |
| Decision Engine | 14 | 15.217 |
| Orchestration & Humans | 10 | 10.870 |
| Shared Platform | 10 | 10.870 |
| NFR Foundations | 6 | 6.522 |
| **Sum** | **92** | **100.000** |

If those seven pillars scored 50, 40, 60, 50, 30, 70, 33.333 respectively:

```
overall = (50×21.739 + 40×21.739 + 60×13.043 + 50×15.217 + 30×10.870 + 70×10.870 + 33.333×6.522) / 100
        = (1086.96 + 869.57 + 782.61 + 760.87 + 326.09 + 760.87 + 217.39) / 100
        = 4804.35 / 100
        = 48.0%
```

**Worked example of Rule A.** *Illustrative only — v1 check counts; take counts from
the current rubric.yaml.* Shared Platform has 5 checks; S3 (cache scope control) is
N/A because the system has no caching layer at all. Scores on the remaining four:
S1=2, S2=1, S4=1, S5=0 → `pillar_pct = 4 / (2×4) × 100 = 50.0%`. The pillar still
carries its full weight of 10.

### 1.5 Maturity bands

Bands are half-open intervals on the 1-decimal rounded overall %:

- **Fragile**: overall < 40.0
- **Developing**: 40.0 ≤ overall < 60.0
- **Production-Capable**: 60.0 ≤ overall < 80.0
- **Production-Grade**: overall ≥ 80.0

Band names and boundaries come from rubric.yaml `maturity_bands` (authoritative).

### 1.6 Rounding rules (mandatory, for cross-model determinism)

- Carry full floating-point precision through all intermediate math. Round only at
  reporting time.
- All percentages (pillar, overall, evidence density, coverage) and deltas: round half
  up to **1 decimal place**.
- Gap impacts: round half up to **1 decimal place**.
- Half-up is defined exactly as: `half_up(x) = sign(x) × floor(|x|·10 + 0.5)/10` for
  1 decimal — round half away from zero: 0.05 → 0.1, and for negative values (deltas
  can be negative) −0.05 → −0.1.
- **Warning: do not use Python's bare `round()`** — it applies banker's rounding
  (`round(31.25, 1) = 31.2`, wrong).
- The maturity band is determined from the overall % **after** rounding to 1 decimal
  (so 39.95 unrounded → 40.0 → Developing; 39.94 → 39.9 → Fragile).
- If every pillar is N/A, the audit is not scoreable — report "not scoreable: no
  applicable checks" and write no history file (see §1.3).
- The JSON history file stores the 1-decimal rounded values.

---

## 2. v2 metrics — precise definitions

Each metric below is defined so that two different models, given the same per-check
scores and file lists, compute the identical number.

### 2.1 Evidence density

```
evidence_density_pct = evidenced_checks / applicable_checks × 100
```

- `applicable_checks` = total non-N/A checks across all applicable pillars.
- `evidenced_checks` = checks scored **1 or 2** that carry at least one concrete
  citation (file path, function name, config key, or infra definition). A score of 1 or 2
  without a citation is invalid — downgrade it to 0 rather than counting it. Checks
  scored 0 are absence findings and never count as evidenced. N/A checks count in
  neither numerator nor denominator.

Interpretation: the fraction of the applicable rubric this codebase can actually prove.
It is NOT the same as the adherence score (a repo full of partials can have high density
and a mediocre score).

Note: by construction, evidence density equals the fraction of applicable checks scoring
nonzero — the cite-or-downgrade rule (an uncited 1 or 2 is downgraded to 0) makes
"scored 1 or 2" and "evidenced" the same set. As a second, falsifiable companion metric,
also compute and report:

```
distinct_evidence_paths = count of distinct file paths cited across all check evidence
```

It appears in the report header (SKILL.md output format) and in the history JSON schema
(§4.1).

### 2.2 Coverage

Reported as raw counts plus one ratio — never as a vague adjective:

```
files_examined  = every distinct file path passed to a Read call, plus every
                  distinct grep-hit path cited in check evidence — nothing else
files_total     = count of tracked files in the repo: `git ls-files | wc -l`
                  (fallback for non-git dirs: all files excluding .git, node_modules,
                  venv/.venv, dist, build, __pycache__, vendor)
configs_examined = subset of files_examined matching config/infra extensions:
                  .yaml .yml .json .jsonl .toml .ini .sh .tf Dockerfile
                  docker-compose* .github/workflows/* Procfile Makefile
                  and dotfiles (e.g. .gitignore, .env.example)
coverage_pct    = files_examined / files_total × 100
```

Report all four. Example line: `Coverage: 47 of 312 tracked files examined (15.1%), 11 configs.`
Coverage is context, not a grade — a focused audit of a huge monorepo will be low and
that is fine, as long as the number is stated. The history JSON additionally records
`files_manifest`: the sorted array of exactly the `files_examined` paths — this is the
audit's reproducibility record (§4.1).

### 2.3 Weighted gap impact per check

For every applicable check scored 0 or 1, the exact overall-percentage points gained by
raising it to 2:

```
check_headroom      = 2 − current_score          (2 for a 0, 1 for a 1)
gap_impact_points   = check_headroom / (2 × pillar_applicable_checks) × weight_normalized_p
```

where `pillar_applicable_checks` is that check's pillar's non-N/A check count and
`weight_normalized_p` is the pillar's normalized weight from §1.3 (equal to the raw
weight when no whole pillar is N/A).

Sanity invariant (models MUST verify before reporting): the sum of gap impacts over all
non-2 applicable checks equals `100 − overall_pct` (before rounding). If it doesn't,
the math is wrong — recompute.

In partial scope, compute gap impacts with raw pillar weights, flag the assumption in
the output, and skip the Σ-impacts invariant check.

Example: G4 scored 0; Govern has 7 applicable checks and normalized weight 20.
`gap_impact = 2 / (2×7) × 20 = 2.857 → +2.9 points` (illustrative v1 counts; under the
live rubric Govern has more checks — always use current rubric.yaml counts). Reported as:
"Implementing G4 (immutable audit trail) gains **+2.9 points** overall."

### 2.4 Top-N gap ranking

The gaps table lists the top **N** gaps, where **N = 10 in full and compare modes;
N = all gaps in gaps mode** (fewer if fewer exist). This section is the single source
for the table size — other files reference it, never restate it. Rows are ordered by:

1. `gap_impact_points` descending (compare unrounded values);
2. tie-break: pillar raw weight descending;
3. tie-break: check ID ascending in rubric order (the order checks appear in
   rubric.yaml: G1 < G2 < … < G10 < P1 …).

This ordering is deterministic — two models with the same scores produce the same
ranked list. In `gaps` mode the table is the primary output; in `full` mode it appears
as a section. Each row: check ID, one-line check name, current score, impact
(`+N.N pts`), and the shortest concrete fix.

**Aggregation rule:** when summing gap impacts (e.g. the gaps-mode headline or a top-N
total), sum the UNROUNDED `gap_impact_points` and round the total once; table row
values are display-only and must never be re-summed.

### 2.5 Compare-mode deltas

Given the current audit and the most recent prior entry for the same `repo_slug`
(see SKILL.md procedure — snapshot before write; the baseline is the latest entry
strictly earlier than this run):

```
pillar_delta_p   = current_pillar_pct_p − previous_pillar_pct_p     (percentage points)
overall_delta    = current_overall_pct − previous_overall_pct
check_transition = previous_score → current_score, for every check whose score changed
```

Report per-pillar deltas (signed, 1 decimal, e.g. `Govern 42.9% (+14.3)`), the overall
delta, band change if any (`Fragile → Developing`), and two lists: **improved checks**
and **regressed checks** with their transitions (`P6: 0 → 2`). A pillar that is N/A in
one audit but not the other is reported as `n/a → NN.N%` with no numeric delta.

---

## 3. Comparing across rubric versions

`rubric_version` is recorded in every history file. The baseline for any comparison is
the most recent prior entry (see SKILL.md procedure — snapshot before write). Rules:

**Common check set.** All deltas — per-pillar and overall — are computed on the COMMON
check set between the two audits. The current audit's headline numbers still include
new checks and are reported separately, labeled "(headline, incl. N checks not in
baseline)". Worked sentence (illustrative numbers): "Overall 45.4% (headline, incl. 2
checks not in baseline); common-check delta: 37.6% → 44.1% (+6.5)" — the headline and
the delta are two different vectors and both must be shown.

1. **Flag always.** If the two audits being compared have different `rubric_version`
   values, the comparison output MUST begin with a flag line:
   `⚠ Rubric changed between audits (1.0.0 → 1.2.0) — deltas computed under rubric 1.2.0, see recompute notes.`
2. **Recompute the old audit under the current rubric** whenever the check sets or
   weights differ. Using the old audit's stored per-check scores:
   - Checks present in both versions keep their stored score.
   - Checks **added** since the old audit are marked **"not assessed"** in the
     recomputed old audit: excluded from the old audit's denominators, AND excluded
     from the current audit's denominators *for delta purposes only* (the current
     audit's headline numbers still include them). This way the delta measures change
     on the common check set, not rubric growth.
   - Checks **removed** from the rubric are dropped from both sides.
   - Current-rubric **weights** apply to both sides of the delta.
3. **Weights-only change** (same check set): recompute the old overall with the new
   weights; per-pillar percentages are unchanged, only the overall delta needs the
   recompute. Still flag.
4. Never overwrite the old history file — the recompute is done in-memory for the
   comparison and noted in the output ("old audit recomputed under rubric 1.2.0:
   old overall 38.3% → 37.6% on common checks").

---

## 4. Audit history JSON schema

Every full, gaps, or compare audit writes one file. Evolve mode never writes a history
file. Partial and dry-run audits never write a history file.

```
history/<repo-slug>-<YYYY-MM-DD-HHMMSS>.json
```

- `repo_slug` = basename of the origin remote URL with any trailing `.git` stripped,
  if an origin remote exists; otherwise the repo directory basename. Then lowercase,
  collapse every run of non-alphanumerics to one hyphen, strip leading/trailing
  hyphens. Example: `git@github.com:kay/WealthPilot-Core.git` → `wealthpilot-core`.
- Filename timestamp: the audit date and time in America/New_York, seconds precision,
  regardless of where the audit runs or whose repo it is. Format `YYYY-MM-DD-HHMMSS`.
  Every audit writes its own file; the baseline for compare is the most recent prior
  entry (see SKILL.md procedure — snapshot before write).
- The file lives in the skill's own directory, not in the audited repo (the audit is
  read-only with respect to the target).

### 4.1 Schema (flat, diff-friendly)

Design rules: no nesting deeper than two levels; object keys in the order given below;
`checks` keys in rubric order; arrays in deterministic order (§2.4 ordering for
`top_gaps`, rubric order for `na_checks`). One audit changes → small, readable diff.

```jsonc
{
  "schema_version": 1,                 // integer; bump only if this schema changes
  "repo": "string",                    // human name as reported in the scorecard
  "repo_slug": "string",               // slug used in the filename
  "date": "YYYY-MM-DD",
  "rubric_version": "1.0.0",           // semver, from rubric.yaml
  "model": "string",                   // e.g. "claude-fable-5"
  "mode": "full" | "gaps" | "compare",     // evolve never writes a history file;
                                           // partial and dry-run audits never write one
  "overall_pct": 38.3,                 // 1 decimal
  "band": "Fragile" | "Developing" | "Production-Capable" | "Production-Grade",
  "evidence_density_pct": 58.5,        // 1 decimal
  "distinct_evidence_paths": 31,       // §2.1 companion metric: distinct file paths cited across all check evidence
  "files_examined": 47,                // integer counts, per §2.2
  "files_total": 312,
  "configs_examined": 11,
  "coverage_pct": 15.1,                // context, not a grade (§2.2)
  "files_manifest": ["api/feedback.py", "src/main.py"],
                                       // sorted array of exactly the §2.2 files_examined
                                       // paths — the audit's reproducibility record

  "pillars": {                         // one entry per rubric pillar, rubric order,
                                       // keyed by the pillar `id` from rubric.yaml
    "govern":        { "weight": 20, "applicable": 7, "score_sum": 6,  "pct": 42.9 },
    "prove":         { "weight": 20, "applicable": 7, "score_sum": 4,  "pct": 28.6 }
    // ... all pillars; an entirely-N/A pillar: { "weight": 8, "applicable": 0, "score_sum": 0, "pct": null }
  },

  "checks": {                          // one entry per rubric check, rubric order
    "G1": { "score": 2, "evidence": "src/auth/middleware.py:require_role() gates every route" },
    "G3": { "score": 0, "evidence": "no approval gate found; searched approve|confirm|gate in src/" },
    "S3": { "score": null, "na": "no caching layer exists anywhere in the system" }
    // score is 0|1|2, or null with an "na" justification instead of "evidence"
  },

  "na_checks": ["S3", "N4"],           // convenience list, rubric order

  "top_gaps": [                        // §2.4 order, max 10
    { "check": "G3", "from": 0, "impact_pts": 2.9 },
    { "check": "G4", "from": 0, "impact_pts": 2.9 }
  ],

  "compared_to": null                  // or "history/<slug>-<YYYY-MM-DD-HHMMSS>.json" when mode=compare
}
```

Field notes:

- `checks.*.evidence` is one line, ≤ 200 chars, always containing at least one path or
  key for scores 1–2; for score 0 it states what was searched.
- `model` is the exact model id string, lowercased (e.g. `claude-fable-5`) — never a
  marketing name or an abbreviation.
- `pillars.*.pct` uses `null` (not 0) for an entirely-N/A pillar so that a 0% pillar
  and an N/A pillar are never confused.
- `top_gaps[].from` is the current score (0 or 1) so the gap list is self-describing.
- Everything a future compare or recompute needs is present: per-check scores rebuild
  every derived number under any rubric version.

### 4.2 Worked example file — `history/helpdesk-bot-2026-07-29-153000.json`

> **Illustrative only** — scored under a hypothetical 43-check rubric labeled 1.0.0
> (pre-release draft; the live rubric starts at 2.0.0 with more checks). Always take
> check counts, IDs, and denominators from the current rubric.yaml, never from this
> example. `files_manifest` is truncated here to 5 of its 47 entries for brevity —
> a real file lists every examined path.

(The full scoring behind these numbers is §5.)

```json
{
  "schema_version": 1,
  "repo": "helpdesk-bot",
  "repo_slug": "helpdesk-bot",
  "date": "2026-07-29",
  "rubric_version": "1.0.0",
  "model": "claude-fable-5",
  "mode": "full",
  "overall_pct": 38.3,
  "band": "Fragile",
  "evidence_density_pct": 58.5,
  "distinct_evidence_paths": 31,
  "files_examined": 47,
  "files_total": 312,
  "configs_examined": 11,
  "coverage_pct": 15.1,
  "files_manifest": ["api/feedback.py", "api/hooks.py", "api/upload.py", "config/rbac.yaml", "infra/secrets.tf"],
  "pillars": {
    "govern":               { "weight": 20, "applicable": 7, "score_sum": 6, "pct": 42.9 },
    "prove":                { "weight": 20, "applicable": 7, "score_sum": 4, "pct": 28.6 },
    "context_data":         { "weight": 12, "applicable": 5, "score_sum": 4, "pct": 40.0 },
    "decision_engine":      { "weight": 14, "applicable": 6, "score_sum": 7, "pct": 58.3 },
    "orchestration_humans": { "weight": 10, "applicable": 5, "score_sum": 3, "pct": 30.0 },
    "shared_platform":      { "weight": 10, "applicable": 4, "score_sum": 4, "pct": 50.0 },
    "rollout_maturity":     { "weight": 8,  "applicable": 4, "score_sum": 1, "pct": 12.5 },
    "nfr_foundations":      { "weight": 6,  "applicable": 3, "score_sum": 2, "pct": 33.3 }
  },
  "checks": {
    "G1": { "score": 2, "evidence": "src/auth/middleware.py:require_role() on every route; roles in config/rbac.yaml" },
    "G2": { "score": 1, "evidence": "src/policy/rules.py exists but only 2 rules, tool calls bypass it" },
    "G3": { "score": 0, "evidence": "no approval gate; searched approve|confirm|human_gate across src/" },
    "G4": { "score": 0, "evidence": "stdout logging only; no append-only store; searched audit|ledger" },
    "G5": { "score": 0, "evidence": "no override mechanism; searched override|supersede" },
    "G6": { "score": 1, "evidence": "DISABLE_BOT env flag in src/main.py:22 but no in-flight handling, untested" },
    "G7": { "score": 2, "evidence": ".env gitignored, secrets via AWS SM (infra/secrets.tf); no keys in prompts/" },
    "P1": { "score": 1, "evidence": "tests/golden/cases.json has 12 pairs, not versioned by prompt version" },
    "P2": { "score": 2, "evidence": "tests/test_output_schema.py enforces JSON schema + forbidden-phrase list" },
    "P3": { "score": 0, "evidence": "no judge evals; searched judge|rubric|llm_eval" },
    "P4": { "score": 0, "evidence": "no resolution tracking; searched resolved|deflection" },
    "P5": { "score": 0, "evidence": "no drift detection; searched drift|distribution" },
    "P6": { "score": 0, "evidence": "evals only via manual make eval; .github/workflows/ has lint+unit only" },
    "P7": { "score": 1, "evidence": "src/llm/client.py logs token counts; no dollar rollup or dashboard" },
    "C1": { "score": 2, "evidence": "ingest/pipeline.py is the only writer to the pgvector index" },
    "C2": { "score": 0, "evidence": "retriever ignores user identity; retrieve() in src/rag/search.py takes no user arg" },
    "C3": { "score": 1, "evidence": "nightly re-index cron (infra/cron.tf) but no staleness bound stated" },
    "C4": { "score": 0, "evidence": "no labeled retrieval set; searched recall|precision|ndcg" },
    "C5": { "score": 1, "evidence": "src/rag/answer.py:88 refuses on empty hits but threshold hardcoded 0" },
    "D1": { "score": 2, "evidence": "src/flow/: classify.py → retrieve.py → answer.py → act.py, each unit-tested" },
    "D2": { "score": 1, "evidence": "retrieval similarity stored (answer.py:41) but never surfaced downstream" },
    "D3": { "score": 0, "evidence": "no confidence routing; low-sim answers ship anyway" },
    "D4": { "score": 1, "evidence": "citations rendered (templates/answer.md) but groundedness never checked" },
    "D5": { "score": 2, "evidence": "MAX_STEPS=6, timeout=30s, token cap in src/flow/act.py:12-19" },
    "D6": { "score": 1, "evidence": "prompts in prompts/*.md but no versioning; git history only" },
    "O1": { "score": 0, "evidence": "no review queue; searched queue|worklist|review" },
    "O2": { "score": 1, "evidence": "escalate-to-email in src/flow/act.py:77; single level, no tracking" },
    "O3": { "score": 1, "evidence": "thumbs-down endpoint api/feedback.py stores rows; no lifecycle states" },
    "O4": { "score": 0, "evidence": "feedback rows never joined back to eval sets; no consumer found" },
    "O5": { "score": 1, "evidence": "Slack webhook on 5xx (src/alerts.py); nothing for SLA or flag resolution" },
    "S1": { "score": 2, "evidence": "src/llm/client.py sole call path; provider set by LLM_PROVIDER env" },
    "S2": { "score": 1, "evidence": "retry w/ backoff in client.py:60 but no secondary provider configured" },
    "S3": { "score": null, "na": "no response caching layer exists anywhere in the system" },
    "S4": { "score": 1, "evidence": "structlog JSON config in src/logging.py:14; no traces, no latency percentiles" },
    "S5": { "score": 0, "evidence": "ingestion runs in request thread (api/upload.py:31); no queue/worker" },
    "R1": { "score": 1, "evidence": "AUTO_SEND flag defaults false (config.py:9) — implicit approval mode, undocumented" },
    "R2": { "score": 0, "evidence": "no promotion criteria; searched docs/ for autonomy|promotion" },
    "R3": { "score": 0, "evidence": "no rollback procedure documented" },
    "R4": { "score": 0, "evidence": "no risk tiering; all actions treated equally" },
    "N1": { "score": 0, "evidence": "no latency target stated anywhere; no measurement" },
    "N2": { "score": 1, "evidence": "stateless: no session store imports; state lives in Postgres (src/db.py); scaling approach undocumented" },
    "N3": { "score": 1, "evidence": "retries present; webhook handler api/hooks.py not idempotent" },
    "N4": { "score": null, "na": "internal IT helpdesk, unregulated domain, no compliance regime applies" }
  },
  "na_checks": ["S3", "N4"],
  "top_gaps": [
    { "check": "G3", "from": 0, "impact_pts": 2.9 },
    { "check": "G4", "from": 0, "impact_pts": 2.9 },
    { "check": "G5", "from": 0, "impact_pts": 2.9 },
    { "check": "P3", "from": 0, "impact_pts": 2.9 },
    { "check": "P4", "from": 0, "impact_pts": 2.9 },
    { "check": "P5", "from": 0, "impact_pts": 2.9 },
    { "check": "P6", "from": 0, "impact_pts": 2.9 },
    { "check": "S5", "from": 0, "impact_pts": 2.5 },
    { "check": "C2", "from": 0, "impact_pts": 2.4 },
    { "check": "C4", "from": 0, "impact_pts": 2.4 }
  ],
  "compared_to": null
}
```

---

## 5. End-to-end worked example: `helpdesk-bot`

> **Illustrative only** — scored under a hypothetical 43-check rubric labeled 1.0.0
> (pre-release draft; the live rubric starts at 2.0.0 with more checks). Always take
> check counts, IDs, and denominators from the current rubric.yaml, never from this
> example.

A small fictional internal IT helpdesk RAG bot. Per-check scores are in §4.2's JSON;
here is every formula producing its concrete number.

### 5.1 Pillar percentages (§1.2)

| Pillar | Scores | N/A | score_sum | applicable | pillar_pct |
|---|---|---|---|---|---|
| Govern | G1=2 G2=1 G3=0 G4=0 G5=0 G6=1 G7=2 | — | 6 | 7 | 6/(2×7)×100 = **42.9%** |
| Prove | P1=1 P2=2 P3=0 P4=0 P5=0 P6=0 P7=1 | — | 4 | 7 | 4/14×100 = **28.6%** |
| Context & Data | C1=2 C2=0 C3=1 C4=0 C5=1 | — | 4 | 5 | 4/10×100 = **40.0%** |
| Decision Engine | D1=2 D2=1 D3=0 D4=1 D5=2 D6=1 | — | 7 | 6 | 7/12×100 = **58.3%** |
| Orchestration | O1=0 O2=1 O3=1 O4=0 O5=1 | — | 3 | 5 | 3/10×100 = **30.0%** |
| Shared Platform | S1=2 S2=1 S4=1 S5=0 | S3 | 4 | 4 | 4/8×100 = **50.0%** (Rule A) |
| Rollout Maturity | R1=1 R2=0 R3=0 R4=0 | — | 1 | 4 | 1/8×100 = **12.5%** |
| NFR Foundations | N1=0 N2=1 N3=1 | N4 | 2 | 3 | 2/6×100 = **33.3%** (Rule A) |

No pillar is entirely N/A, so Rule B does not fire: normalized weights = raw weights.

### 5.2 Overall (§1.3)

```
overall = (42.857×20 + 28.571×20 + 40.0×12 + 58.333×14 + 30.0×10 + 50.0×10 + 12.5×8 + 33.333×6) / 100
        = (857.14 + 571.43 + 480.00 + 816.67 + 300.00 + 500.00 + 100.00 + 200.00) / 100
        = 3825.24 / 100
        = 38.25 → 38.3%  → band: Fragile (< 40.0)
```

### 5.3 Evidence density (§2.1)

Applicable checks = 7+7+5+6+5+4+4+3 = **41**.
Checks scored 1 or 2 with citations: Govern 4 (G1,G2,G6,G7), Prove 3 (P1,P2,P7),
Context 3 (C1,C3,C5), Decision 5 (D1,D2,D4,D5,D6), Orchestration 3 (O2,O3,O5),
Platform 3 (S1,S2,S4), Rollout 1 (R1), NFR 2 (N2,N3) = **24**.

```
evidence_density = 24 / 41 × 100 = 58.54 → 58.5%
```

### 5.4 Coverage (§2.2)

`git ls-files | wc -l` → 312 tracked files. The audit opened 47 unique files, 11 of
which matched config patterns.

```
coverage = 47 / 312 × 100 = 15.06 → 15.1%
```

Reported: `Coverage: 47 of 312 tracked files examined (15.1%), 11 configs.`

### 5.5 Gap impacts (§2.3) — every non-2 check

Formula per check: `(2 − score) / (2 × pillar_applicable) × weight`.

| Check | From | Calculation | Impact |
|---|---|---|---|
| G3, G4, G5 | 0 | 2/(2×7)×20 = 2.857 | +2.9 each |
| P3, P4, P5, P6 | 0 | 2/(2×7)×20 = 2.857 | +2.9 each |
| S5 | 0 | 2/(2×4)×10 = 2.500 | +2.5 |
| C2, C4 | 0 | 2/(2×5)×12 = 2.400 | +2.4 each |
| D3 | 0 | 2/(2×6)×14 = 2.333 | +2.3 |
| O1, O4 | 0 | 2/(2×5)×10 = 2.000 | +2.0 each |
| R2, R3, R4 | 0 | 2/(2×4)×8 = 2.000 | +2.0 each |
| N1 | 0 | 2/(2×3)×6 = 2.000 | +2.0 |
| G2, G6 | 1 | 1/(2×7)×20 = 1.429 | +1.4 each |
| P1, P7 | 1 | 1/(2×7)×20 = 1.429 | +1.4 each |
| S2, S4 | 1 | 1/(2×4)×10 = 1.250 | +1.3 each |
| C3, C5 | 1 | 1/(2×5)×12 = 1.200 | +1.2 each |
| D2, D4, D6 | 1 | 1/(2×6)×14 = 1.167 | +1.2 each |
| O2, O3, O5 | 1 | 1/(2×5)×10 = 1.000 | +1.0 each |
| R1 | 1 | 1/(2×4)×8 = 1.000 | +1.0 |
| N2, N3 | 1 | 1/(2×3)×6 = 1.000 | +1.0 each |

**Invariant check:** sum of all unrounded impacts =
11.429 (Govern) + 14.286 (Prove) + 7.200 (Context) + 5.833 (Decision) + 7.000 (Orch)
+ 5.000 (Platform) + 7.000 (Rollout) + 4.000 (NFR) = **61.748** = 100 − 38.252 ✓

### 5.6 Top-10 gap ranking (§2.4)

Sorted by unrounded impact desc → pillar weight desc → check ID asc:

| # | Check | Gap | Impact |
|---|---|---|---|
| 1 | G3 | No approval gates on risky actions | +2.9 |
| 2 | G4 | No immutable audit trail | +2.9 |
| 3 | G5 | No human override mechanism | +2.9 |
| 4 | P3 | No LLM-as-judge evals | +2.9 |
| 5 | P4 | No outcome/resolution tracking | +2.9 |
| 6 | P5 | No drift monitoring | +2.9 |
| 7 | P6 | Evals not automated (manual only) | +2.9 |
| 8 | S5 | Ingestion blocks request threads, no queue | +2.5 |
| 9 | C2 | Retrieval ignores user permissions | +2.4 |
| 10 | C4 | Retrieval quality never measured | +2.4 |

(G3/G4/G5 sort before P3–P6 despite equal impact and equal pillar weight because
Govern checks precede Prove checks in rubric order. S5 at 2.500 outranks C2/C4 at
2.400 on impact alone.)

Headline in `gaps` mode: "Closing the top 10 gaps gains **+27.3 points**
(2.857×7 + 2.5 + 2.4×2 = 27.3), moving helpdesk-bot from 38.3% (Fragile) to 65.6%
(Production-Capable)."

### 5.7 Compare mode, six weeks later (§2.5)

Suppose `history/helpdesk-bot-2026-09-09-101500.json` shows the team implemented P6 (0→2),
G4 (0→2), and improved G6 (1→2), same rubric 1.0.0. New sums: Govern 9/14 = 64.3%,
Prove 6/14 = 42.9%, everything else unchanged.

```
new overall = (64.286×20 + 42.857×20 + 40.0×12 + 58.333×14 + 30.0×10 + 50.0×10 + 12.5×8 + 33.333×6) / 100
            = (1285.71 + 857.14 + 480.00 + 816.67 + 300.00 + 500.00 + 100.00 + 200.00) / 100
            = 4539.52 / 100 = 45.40 → 45.4%
```

Compare output:

```
helpdesk-bot: 38.3% → 45.4% (+7.1)   band: Fragile → Developing
  Govern         42.9% → 64.3%  (+21.4)
  Prove          28.6% → 42.9%  (+14.3)
  Context & Data 40.0% → 40.0%  (0.0)
  ... (unchanged pillars listed with 0.0)
Improved checks: G4: 0→2, G6: 1→2, P6: 0→2
Regressed checks: none
```

If the second audit had run under rubric 1.1.0 (which, say, added check P8), the output
would start with the §3 flag, P8 would be "not assessed" on the old side and excluded
from both denominators for the delta, and the recomputed common-check overall would be
stated alongside the headline numbers.

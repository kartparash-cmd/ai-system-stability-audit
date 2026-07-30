# Rubric Improvement Proposals

Improvement proposals for `rubric.yaml`, filed by auditing models per
`EVOLUTION.md`. **Nothing here is active** — entries change the rubric only
after the skill owner accepts them in evolve mode. Read EVOLUTION.md before adding an
entry; do not re-file anything in the Rejected section without new evidence
answering its rejection reason.

## Entry format

Id format: `PROP-YYYYMMDD-<repo-slug>-NN` — the slug of the audited repo
(scoring.md §4), or `meta` for non-audit proposals. Before numbering, re-read
this file and scan ALL THREE sections (Pending, Accepted, AND Rejected) for
today's ids with the same slug; continue the sequence. Append after
re-reading; if the "(none — delete this line…)" placeholder is already gone,
append below the last entry — never replace existing content. The pre-write
scan is not a lock: immediately after appending, re-read this file; if an id
you just wrote also appears in an entry you did not write (concurrent audit),
rename YOURS with your audit's HHMMSS suffix — `PROP-YYYYMMDD-<repo-slug>-NN-HHMMSS`
— and re-verify uniqueness (full rule: EVOLUTION.md, id format).

```markdown
### PROP-YYYYMMDD-<repo-slug>-NN
- **Date:** YYYY-MM-DD
- **Proposer:** <model id>
- **Rubric version:** <e.g. 2.0.0>
- **Type:** new-check | evidence-hint | weight-change | deprecate-check | scoring-change | new-mode
- **Affects:** <pillar/check id, or "scoring"/"modes">
- **Audit that prompted it:** <repo slug + date, or "tech-development"/"history-signal">
- **Rationale:** <what the audit revealed or what changed in the field>
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml
  - <current>
  + <proposed>
  ```
- **Expected semver bump if accepted:** patch | minor | major
- **Score impact estimate:** <one line>
```

Guardrails (see EVOLUTION.md for full text): no weakening of evidence
requirements, no score inflation, no check removal without deprecation
rationale, max 3 proposals per audit, no duplicates of Pending or Rejected
entries.

## Pending

<!-- Append new proposals below this line. Re-read this file and scan
Pending, Accepted, AND Rejected for today's PROP ids (same repo-slug) before
numbering a new one. If the placeholder is gone, append below the last
entry — never replace existing content. -->

*(none — delete this line when adding the first entry)*

## Accepted

<!-- Evolve mode moves accepted proposals here. Each entry keeps its original
text verbatim plus three mandated lines:
  - **Accepted:** YYYY-MM-DD by the skill owner
  - **Applied in:** vX.Y.Z
  - **As modified:** <amended diff summary, or "as filed">
Never delete entries from this section. -->

### PROP-20260729-meta-01
- **Date:** 2026-07-29
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** new-mode
- **Affects:** modes (SKILL.md)
- **Audit that prompted it:** history-signal
- **Rationale:** (Non-normative note: reviewed by panel — Codex, Opus 5 —
  2026-07-29.) History signal is 1 of 3 declared proposal sources
  (EVOLUTION.md), yet no mode computes it today — a model must eyeball raw
  history JSONs to spot the patterns the protocol asks for (checks that score
  2 in every audit, checks N/A in >80% of audits). With ≥3 history entries
  for a slug, a trend mode could compute per-check trajectories, never-moved
  checks, and N/A frequency per check, turning the declared source into a
  measurable input for deprecation and narrowing proposals.
- **Suggested change (diff-style):**
  ```diff
  # SKILL.md — Modes table
   | **evolve** | "evolve", "review proposals", "apply proposals" | Process PROPOSALS.md exactly per EVOLUTION.md — review cards, impact analysis against history/, the skill owner decides each proposal. Never runs implicitly. |
  +| **trend** | "trend", "trajectory" (requires ≥3 history entries for this repo_slug) | Per-check score trajectories across history entries, checks that never moved, N/A frequency per check; reporting only — no new scoring sweep, no history write, still files proposals |
  ```
- **Expected semver bump if accepted:** major
- **Score impact estimate:** no score change (reporting-only mode; new modes
  are always MAJOR per the semver policy)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed, plus mechanical mode-list sync required by checklist item 10: "trend" added to the SKILL.md frontmatter description and the README modes table

### PROP-20260729-meta-02
- **Date:** 2026-07-29
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** scoring-change
- **Affects:** scoring (scoring.md §4 history JSON schema)
- **Audit that prompted it:** history-signal
- **Rationale:** (Non-normative note: reviewed by panel — Codex, Opus 5 —
  2026-07-29.) Evolve mode's impact analysis is required to rescore
  history/ under a proposed rubric, but history JSONs store only a ≤200-char
  evidence line per check — when a check's meaning or anchors change, old
  audits cannot be rescored and must be marked "unknown — will apply from
  next audit". A richer audit trace (per-check searched patterns, evidence
  snippets beyond the 200-char cap) would make historical audits backtestable
  when checks change.
- **Suggested change (diff-style):**
  ```diff
  # scoring.md §4.1 — per-check entry in "checks"
  -  "G1": { "score": 2, "evidence": "src/auth/middleware.py:require_role() gates every route" },
  +  "G1": { "score": 2, "evidence": "src/auth/middleware.py:require_role() gates every route",
  +          "searched": ["requires_auth", "@login_required", "verifyToken"],
  +          "evidence_extended": "<full snippet(s) supporting the score, no 200-char cap>" },
  ```
- **Expected semver bump if accepted:** major
- **Score impact estimate:** no score change (trace enrichment only;
  scoring-change proposals are always MAJOR)
- **Refinement (2026-07-29):** if accepted, scoring.md `schema_version` must
  bump 1 → 2 alongside the schema edit (per EVOLUTION.md scoring-change scope;
  verified by evolve checklist item 9).
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** schema v2 additionally gains optional top-level duration_seconds, tokens_estimate, cost_estimate_usd fields (owner-directed in the same session, for P7 cost tracking and S4 observability)

### PROP-20260730-ai-system-stability-audit-01
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** evidence-hint
- **Affects:** rubric header note + per-check hints on G1, G6, G9, S1, S2, S5
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (self-audit)
- **Rationale:** Auditing a harness-hosted system (a Claude Code skill — no
  service code, the LLM runtime is the external harness) required 11 N/A calls
  out of 50 checks (22%), each argued from scratch because every evidence hint
  assumes a networked AI service. The N/A boundary between "harness provides
  it" (G9 tools, S1 gateway) and "system should still have it" (G8 injection
  defense, G10 write scoping — both scoreable and both non-2 here) was the
  hardest judgment of the audit; explicit guidance would make the same calls
  reproducible across models.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml (header comment, after the scoring-scale note)
  + # Harness-hosted systems (skills, plugins, CLI tools where the LLM runtime
  + # is an external harness): checks on infrastructure the harness owns
  + # (G1 authn, G6 kill switch, G9 tool registry, S1/S2 gateway/failover,
  + # S5 async) are legitimately N/A with a one-line argument. Checks on the
  + # system's OWN behavior (G8 injection defense of content it reads, G10
  + # scoping of writes it instructs, C6 hygiene of artifacts it persists)
  + # are never N/A on harness grounds.
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** no score change for service repos; removes
  ~6 judgment calls per harness-hosted audit (makes N/A sets reproducible)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-02
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** evidence-hint
- **Affects:** CONTEXT_DATA / C6
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (self-audit)
- **Rationale:** The audit's most severe finding (C6 = 0, +3.0 pts) — evidence
  strings and file manifests from audited repos persist into a PUBLICLY synced
  git repo — was reachable only by combining `git remote` inspection with the
  persistence path; none of C6's five existing hints points at where persisted
  artifacts SYNC to. Publication-boundary crossings (private source data →
  public store) are a distinct leak class the hints currently miss entirely.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml, C6 evidence_hints
  +          - "publication boundary: check where persisted memory/artifacts sync or publish to (git remotes, shared drives, artifact stores) — persistence into a store with BROADER visibility than the source data is a trust-boundary crossing (anti-evidence); run `git remote -v` on the store's repo"
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** stricter C6 scoring for systems that persist
  audit/memory artifacts into shared or public stores (this repo included)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-03
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** evidence-hint
- **Affects:** PROVE / P6 (and boundary with P2)
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (compare re-audit)
- **Rationale:** Scoring P6 required an unguided judgment call on whether a
  deterministic validation runner in CI (schema + math checks with
  exit-nonzero) counts as "evals run automatically". The P2/P6 boundary is
  undefined: P2 credits the assertions, but nothing states whether P6 requires
  the QUALITY eval suite (golden set, judge scores) to be the thing automated,
  or any automated check suffices. Two models can defensibly score this repo's
  CI as P6=1 or P6=2 — a 1.25-point swing on a Prove check.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml, P6 evidence_hints
  +          - "scope boundary with P2: P6 scores the automation of the EVAL suite (golden sets, judge scoring, adversarial cases) — CI that runs only deterministic schema/format validation earns P6 = 1 at most; the quality evals themselves must run on the schedule for 2"
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** removes a 1.25-pt ambiguity on any repo whose CI
  automates validation but not quality evals (this repo scored P6=1 under the
  proposed rule)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-04
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** evidence-hint
- **Affects:** DECISION_ENGINE / D2
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (first
  executed golden run — fixture-repo divergence D2: auditor 0 vs authored
  expected 1)
- **Rationale:** D2's hint says confidence must be "COMPUTED, not
  model-self-reported prose", but the scoring_anchors never repeat the word
  "computed" at level 0, so a self-reported confidence value that IS attached
  and consumed (the fixture's exact pattern — model rates itself, threshold
  gates on it) fits no anchor cleanly: not "no signal anywhere" (0), not
  "computed but discarded" (1). Two scorers split 0 vs 1 on the golden
  fixture — a 1.0-pt swing on a common real-world pattern.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml, D2 scoring_anchors
  -          0 = no computed confidence signal anywhere; 1 = a signal is computed
  +          0 = no computed confidence signal anywhere (a model-self-reported
  +          confidence value does not count as computed, even if attached and
  +          consumed downstream); 1 = a signal is computed
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** resolves a 1.0-pt two-scorer split observed on
  the golden fixture's self-reported-confidence pattern
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-05
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 2.0.0
- **Type:** evidence-hint
- **Affects:** CONTEXT_DATA / C5
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (first
  executed golden run — fixture-repo divergence C5: auditor 1 vs expected N/A;
  auditor conceded)
- **Rationale:** On a system with no retrieval layer, C5 has no
  empty-retrieval state and is N/A — but nothing in the hints says so, and an
  auditor can be tempted to credit a generic low-confidence fallback branch
  under C5, double-counting D3's scope (exactly what happened on the golden
  run: same app.py branch nearly earned both C5=1 and D3=1). A 1.2-pt
  score-inflation path on every non-RAG system audited.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml, C5 evidence_hints
  +          - "no retrieval layer in the system at all -> C5 is N/A (no empty-retrieval state exists); do NOT credit generic low-confidence fallback branches here - that behavior is D3's scope, and counting it twice inflates both pillars"
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** removes a 1.2-pt double-count path on every
  non-RAG audit (golden fixture C&D pillar: 50.0% under the double-count vs
  N/A-whole-pillar under the correct reading)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v3.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-06
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 3.0.0
- **Type:** evidence-hint
- **Affects:** SHARED_PLATFORM / S4
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (compare, rubric 3.0.0)
- **Rationale:** For harness-hosted systems, S4's anchor 2 (traces across the
  request flow + latency percentiles) is structurally unreachable from the
  repo alone — execution traces live in the harness, not the codebase. The
  3.0.0 harness-hosted header note covers N/A boundaries but S4 is scoreable
  (it stayed 1 across all four audits of this repo) with no guidance on what
  in-repo evidence could ever earn 2.
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml, S4 evidence_hints
  +          - "harness-hosted systems: per-run structured records (audit/history files) + duration fields + a script computing cross-run stats can substitute for logs+metrics; anchor 2 still requires referenced, retrievable execution traces (e.g. harness transcripts) — without them S4 caps at 1"
  ```
- **Expected semver bump if accepted:** patch
- **Score impact estimate:** no current score change (this repo stays S4=1);
  makes the S4 ceiling explicit instead of a repeated judgment call
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v4.0.0
- **As modified:** as filed

### PROP-20260730-ai-system-stability-audit-07
- **Date:** 2026-07-30
- **Proposer:** claude-fable-5
- **Rubric version:** 3.0.0
- **Type:** new-mode
- **Affects:** modes (SKILL.md — trend row, behavior clarification)
- **Audit that prompted it:** ai-system-stability-audit 2026-07-30 (first
  trend-eligible history: 4 entries, all same-day)
- **Rationale:** All 4 history entries for this slug are from one calendar
  day (a hardening sprint), so trend trajectories degenerate: days_between=0
  everywhere and per-check "trajectories" are really intra-day fix
  verification. Trend mode has no stated rule for same-day clusters, so two
  models could report different trajectory counts (4 points vs 1 collapsed
  point per check).
- **Suggested change (diff-style):**
  ```diff
  # SKILL.md — trend mode row, output column, append:
  + Same-day entries collapse to the day's LATEST entry for trajectory
  + purposes (intra-day runs are fix-verification, not trend signal); the
  + collapse count is stated in the output.
  ```
- **Expected semver bump if accepted:** major
- **Score impact estimate:** no score change (reporting-only determinism rule)
- **Accepted:** 2026-07-30 by Kartikeya Parashar
- **Applied in:** v4.0.0
- **As modified:** as filed

## Rejected

<!-- Evolve mode moves rejected proposals here verbatim, with rejection date
and reason appended. Never delete entries from this section — they exist so
future models do not re-propose the same idea. -->

*(none — delete this line when adding the first entry)*

# Rubric Improvement Proposals

Improvement proposals for `rubric.yaml`, filed by auditing models per
`EVOLUTION.md`. **Nothing here is active** — entries change the rubric only
after Kay accepts them in evolve mode. Read EVOLUTION.md before adding an
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

### PROP-20260729-meta-01
- **Date:** 2026-07-29
- **Proposer:** claude-fable-5 + review panel (Codex, Opus 5), 2026-07-29
- **Rubric version:** 2.0.0
- **Type:** new-mode
- **Affects:** modes (SKILL.md)
- **Audit that prompted it:** history-signal
- **Rationale:** History signal is 1 of 3 declared proposal sources
  (EVOLUTION.md), yet no mode computes it today — a model must eyeball raw
  history JSONs to spot the patterns the protocol asks for (checks that score
  2 in every audit, checks N/A in >80% of audits). With ≥3 history entries
  for a slug, a trend mode could compute per-check trajectories, never-moved
  checks, and N/A frequency per check, turning the declared source into a
  measurable input for deprecation and narrowing proposals.
- **Suggested change (diff-style):**
  ```diff
  # SKILL.md — Modes table
   | **evolve** | "evolve", "review proposals", "apply proposals" | Process PROPOSALS.md exactly per EVOLUTION.md — review cards, impact analysis against history/, Kay decides each proposal. Never runs implicitly. |
  +| **trend** | "trend", "trajectory" (requires ≥3 history entries for this repo_slug) | Per-check score trajectories across history entries, checks that never moved, N/A frequency per check; reporting only — no new scoring sweep, no history write, still files proposals |
  ```
- **Expected semver bump if accepted:** major
- **Score impact estimate:** no score change (reporting-only mode; new modes
  are always MAJOR per the semver policy)

### PROP-20260729-meta-02
- **Date:** 2026-07-29
- **Proposer:** claude-fable-5 + review panel (Codex, Opus 5), 2026-07-29
- **Rubric version:** 2.0.0
- **Type:** scoring-change
- **Affects:** scoring (scoring.md §4 history JSON schema)
- **Audit that prompted it:** history-signal
- **Rationale:** Evolve mode's impact analysis is required to rescore
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

## Accepted

<!-- Evolve mode moves accepted proposals here. Each entry keeps its original
text verbatim plus three mandated lines:
  - **Accepted:** YYYY-MM-DD by Kay
  - **Applied in:** vX.Y.Z
  - **As modified:** <amended diff summary, or "as filed">
Never delete entries from this section. -->

*(none — delete this line when adding the first entry)*

## Rejected

<!-- Evolve mode moves rejected proposals here verbatim, with rejection date
and reason appended. Never delete entries from this section — they exist so
future models do not re-propose the same idea. -->

*(none — delete this line when adding the first entry)*

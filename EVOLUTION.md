# EVOLUTION.md — Self-Improvement Protocol

This file defines how the audit rubric improves over time. It is written to be
executed by ANY model in a future session with zero memory of prior sessions.
Everything you need is in this file, `SKILL.md`, `rubric.yaml`, `PROPOSALS.md`,
`CHANGELOG.md`, and `history/`.

## The one rule that is never optional

**Proposals are filed after ANY audit — full, gaps, compare, or partial — and
NEVER in a dry-run. After completing any audit, you MUST file at least one
improvement proposal to PROPOSALS.md before presenting the final
scorecard.** No exceptions. If you believe the rubric is perfect, you have not
looked hard enough — every audit surfaces at least one check that was ambiguous
to score, one evidence hint that sent you to the wrong files, or one emerging
practice the rubric doesn't cover yet.

**Maximum 3 proposals per audit.** Quality over quantity. If you have more than
3 ideas, file the 3 with the strongest grounding in what this audit actually
revealed.

## Before proposing: mandatory reads

1. Read `PROPOSALS.md` in full — ALL THREE sections: Pending, Accepted, AND
   Rejected.
   - Never file a duplicate of a Pending proposal. If your idea refines a
     pending one, add a dated `Refinement:` line under the existing entry
     instead of a new entry.
   - Never re-file anything in the Rejected section unless you have *new*
     evidence that directly answers the recorded rejection reason. If you do,
     say so explicitly in the rationale: `Re-proposal of PROP-XXXX; rejection
     reason was "..."; new evidence: ...`
2. Read the `rubric_version:` key at the top of `rubric.yaml` so your proposal
   references the version it was written against.

## What counts as a valid proposal source

A proposal must be grounded in one of:
- **Audit friction** — something this audit just revealed: a check you couldn't
  score cleanly, evidence you found only by luck, a real weakness the rubric
  gave no credit for catching, a check that double-counts another.
- **Tech development** — a practice that has become standard since the rubric
  version was written (new eval tooling, new attack class, new compliance
  regime, new orchestration pattern). Name the development concretely.
- **History signal** — a pattern across `history/` results, e.g. a check that
  scores 2 in every audit ever run (candidate for deprecation or for raising
  the bar) or one that is N/A in >80% of audits (candidate for narrowing).

"I think it would be nice" is not a source. Cite what you saw.

## Proposal entry format (exact)

Append to the **Pending** section of `PROPOSALS.md`:

```markdown
### PROP-YYYYMMDD-<repo-slug>-NN
- **Date:** YYYY-MM-DD
- **Proposer:** <model id, e.g. claude-fable-5>
- **Rubric version:** <version proposal was written against, e.g. 2.0.0>
- **Type:** new-check | evidence-hint | weight-change | deprecate-check | scoring-change | new-mode
- **Affects:** <pillar id / check id, e.g. "PROVE / P5", or "scoring" or "modes">
- **Audit that prompted it:** <repo slug + date, e.g. "onclave-agent 2026-07-29", or "tech-development" / "history-signal">
- **Rationale:** <2-5 sentences. What did the audit reveal, or what changed in
  the field? Why does the current rubric handle it badly? Metrics-first where
  possible: "P5 was un-scoreable in 3 of 4 history entries", "evidence hint
  matched 0 files; actual evidence lived in ...">
- **Suggested change (diff-style):**
  ```diff
  # rubric.yaml
  - <exact current line(s)>
  + <exact proposed line(s)>
  ```
- **Expected semver bump if accepted:** patch | minor | major
- **Score impact estimate:** <one line: "no score change (hint only)" or
  "repos without X lose up to N.N weighted points" or "neutral: weight moved
  from A to B within pillar">
```

Id format: `PROP-YYYYMMDD-<repo-slug>-NN` — `<repo-slug>` is the slug of the
audited repo (per scoring.md §4); for non-audit proposals (tech-development,
history-signal, work on the skill itself) use `meta`. `NN` is a two-digit
sequence within the day for that slug (01, 02, 03). Before numbering, re-read
PROPOSALS.md and scan ALL THREE sections — Pending, Accepted, AND Rejected —
for today's ids with the same slug; if any exist, continue the sequence.

The pre-write scan is not a lock: two concurrent audits of the same repo on
the same day can both compute the same NN. Collision resolution is therefore
mandatory: **immediately after appending, re-read PROPOSALS.md once more.** If
any id you just wrote also appears in an entry you did not write — or NN would
exceed 99 — rename YOUR entry by suffixing your audit's start time:
`PROP-YYYYMMDD-<repo-slug>-NN-HHMMSS`. The HHMMSS suffix source is the audit's
start time in America/New_York, HHMMSS (identical to the history-filename time
whenever a history file is written — partial mode writes none but still has a
start time). If the suffixed id still collides, apply a monotonic -2/-3 suffix
until unique. Re-read once more to confirm the renamed id is unique before
presenting the scorecard.

Append only after re-reading: if the target section shows the placeholder
`*(none — delete this line when adding the first entry)*`, delete that
placeholder line when appending the first entry; if the placeholder is already
gone, append below the last entry — never replace existing content.

A `scoring-change` proposal may target scoring.md content (formulas or the §4
history-JSON schema) OR rubric.yaml's `maturity_bands` block; any of these
targets is always a MAJOR bump. A change to the §4.1 schema additionally
requires bumping scoring.md's `schema_version` integer (verified by evolve
checklist item 9).

The diff must be concrete and mechanically applicable. For a `new-check`, write
the full check entry as it would appear in rubric.yaml (id, name, description,
evidence_hints, scoring_anchors, added_in, rationale). For a `weight-change`, show both the
weight you raise and the weight you lower — total pillar weights must still
sum to 100.

## Guardrails — proposals that must NOT be filed

Reject your own idea before filing if it does any of the following:

1. **Weakens evidence requirements.** Nothing may make it easier to score
   points without cited file-level evidence. "Accept README claims for check
   X" is never valid.
2. **Inflates scores.** A change whose primary effect is that typical repos
   score higher without being better is invalid. Weight changes must be
   justified by risk reality, not by making numbers prettier. State the score
   impact honestly in the entry.
3. **Removes a check without deprecation rationale.** `deprecate-check`
   requires an argument for why the risk the check guarded against no longer
   exists, is fully covered by another named check, or is universally solved
   by the platform layer. "Nobody scores well on it" is a reason to keep it.
4. **Exceeds the cap.** Max 3 proposals per audit.
5. **Duplicates a Pending or Rejected entry** (see mandatory reads above).

A proposal violating these guardrails should be rejected in evolve mode even if
otherwise attractive — the reviewer applies the same list.

## Proposals are NEVER auto-applied

Filing a proposal changes only PROPOSALS.md. `rubric.yaml`, `SKILL.md`,
`scoring.md`, `CHANGELOG.md`, and all scoring behavior remain exactly as-is
until the skill owner runs **evolve mode** and explicitly accepts a proposal. Do not "helpfully" apply an
obvious fix directly to rubric.yaml during an audit. Do not score the audit you
just ran against your own proposed changes — score against the current
rubric.yaml only.

## Evolve mode

Trigger: the user says "evolve", "review proposals", "apply proposals", or invokes
the skill with the evolve argument. Evolve mode never runs implicitly.

### Procedure

1. **Load state.** Read `rubric.yaml` (note current version), `PROPOSALS.md`,
   `CHANGELOG.md`, and every JSON file in `history/`.
2. **If Pending is empty**, say so and stop.
3. **For each pending proposal, present a review card:**

   ```
   PROP-YYYYMMDD-<repo-slug>-NN — <type> — <affects>
   Proposed by <model> on <date> (rubric <version>), from audit <repo/date>
   Rationale: <verbatim from entry>
   Diff: <verbatim from entry>

   Guardrail check: PASS | FAIL <which guardrail and why>
   Impact analysis:
     - Semver bump if accepted: patch|minor|major (X.Y.Z -> X'.Y'.Z')
     - Rescore of history/ under the proposed rubric:
         <repo>@<date>: 61% -> 58% (-3, P5 now scores 0 with no evidence)
         <repo>@<date>: 74% -> 74% (no change)
       For a new-check, score it against each historical audit's recorded
       evidence; where the historical JSON lacks the evidence to score it,
       mark "unknown — will apply from next audit" instead of guessing.
     - Repos most affected and in which direction.

   Recommendation: ACCEPT | REJECT | MODIFY — <2-3 sentences of reasoning>
   ```

   Make a genuine recommendation for every proposal — never punt the analysis
   to the skill owner — but the recommendation decides nothing.
4. **The skill owner decides each proposal individually:** accept / reject / modify / defer
   (modify = the skill owner states the change, you restate the amended diff, the skill owner confirms,
   then it is treated as accepted-as-modified; defer = the entry STAYS in
   Pending — append to it `- **Deferred:** YYYY-MM-DD — <what evidence would
   decide it>` and take no other action on it this session).
5. **Apply accepted proposals:**
   a. Edit the target file exactly per the (possibly amended) diff. For most
      proposal types the target is `rubric.yaml`. When the skill owner accepts a
      `scoring-change` proposal, the target is `scoring.md` (formulas or the
      §4 history-JSON schema) OR rubric.yaml's `maturity_bands` block,
      whichever the proposal names; for
      a `new-mode` proposal, edit `SKILL.md`. These scoring/mode edits are
      always MAJOR bumps and are permitted ONLY in evolve mode with the skill owner's
      explicit acceptance.
   b. Bump `rubric_version:` in rubric.yaml by semver. **This step is the
      normative semver policy — every other file's summary defers to it:**
      - **MAJOR** (X.0.0) — pillar weight changes, pillar restructuring,
        check removal/renumbering/meaning changes, scoring-formula or
        maturity-band changes, new modes, scoring-engine edits (accepted
        scoring-change and new-mode proposals edit scoring.md / SKILL.md and
        are always MAJOR).
      - **MINOR** (x.Y.0) — new checks, check scope clarifications that
        change what earns points.
      - **PATCH** (x.y.Z) — evidence hints, wording, typos.
      Multiple proposals accepted in one evolve session = one combined bump at
      the highest level among them, one new version.
      Also in this step: set rubric.yaml `last_updated:` to today's date
      (America/New_York), and set each newly added check's `added_in:` to the
      version this session's bump produces.
   c. Add a `CHANGELOG.md` entry (format below), listing each applied PROP id.
   d. Move the applied entries from Pending to the "## Accepted" section of
      PROPOSALS.md. Each accepted entry keeps its original text verbatim plus
      three mandated lines:
      - **Accepted:** YYYY-MM-DD by the skill owner
      - **Applied in:** vX.Y.Z
      - **As modified:** <amended diff summary, or "as filed">
      (The changelog remains the permanent record of what changed.)
   e. If a check id is deprecated, never reuse its id; new checks get the next
      unused number in the pillar.
6. **Move rejected proposals** from Pending to the Rejected section verbatim,
   appending two lines:
   ```
   - **Rejected:** YYYY-MM-DD by the skill owner
   - **Reason:** <the skill owner's reason, or the guardrail violated — specific enough
     that a future model knows what evidence would be needed to re-open it>
   ```
   Never delete rejected entries. They are the institutional memory that stops
   future models from re-proposing the same idea.
7. **Verify and report** — run this 12-item checklist, every item mandatory:
   1. Pillar weights sum to 100.
   2. rubric.yaml parses as YAML.
   3. Check ids are unique and no deprecated id was reused.
   4. The CHANGELOG.md entry for the new version is written and matches the
      `rubric_version:` key.
   5. rubric.yaml `last_updated:` equals today's date (America/New_York).
   6. Every `added_in:` value matches a real released version (checks added
      this session carry the version this bump produced).
   7. No stale literal is left in ANY skill file — grep scoring.md,
      CHANGELOG.md, SKILL.md, and EVOLUTION.md for every weight, band,
      check-count, pillar display name, mode name, and template-element count
      the accepted diff invalidated (SKILL.md hardcodes the pillar names in
      its output template and the "all 11 template elements" count; EVOLUTION.md
      and PROPOSALS.md restate formats and mode-dependent rules). If a
      scoring-change was applied, recompute every worked-example number in
      scoring.md §§1.4, 4.2, 5 under the amended formula.
   8. PROPOSALS.md sections are consistent: every dispatched entry moved to
      Accepted or Rejected; deferred entries remain in Pending, each with its
      dated `- **Deferred:**` line; placeholders correct.
   9. scoring.md `schema_version` (§4.1) is bumped by 1 iff an accepted diff
      changed the §4.1 history JSON schema; if none did, it is unchanged.
   10. Mode consistency — every mode named in SKILL.md's modes table also
      appears in SKILL.md's frontmatter `description:`, and its history-write
      behavior is stated consistently in SKILL.md's history-write sentence,
      scoring.md §4's opening write rule, and (only if it writes a history
      file) scoring.md §4.1's `mode` enum.
   11. SKILL.md's frontmatter `description:` is ≤ 1024 characters after any
      edit (hard platform cap on skill descriptions).
   12. Every check in rubric.yaml has a non-empty scoring_anchors block
      (grep -c scoring_anchors equals the check count).
   Confirm every pending proposal was dispatched or explicitly deferred, then
   summarize: N accepted, M rejected, K deferred, new version.

### Comparability note

History JSONs record the rubric version they were scored under. Compare mode
(in SKILL.md) must flag any cross-version comparison and state the version
pair. Cross-version deltas are NOT guesswork: scoring.md §3 recomputes them
deterministically on the common check set from the stored per-check scores.
The only genuine unknowns are checks whose meaning changed when the stored
evidence is insufficient to rescore them — mark those "unknown — will apply
from next audit" (as in step 3's impact analysis), never estimate them.
Evolve mode never rewrites history/ files — the rescoring in impact analysis
is presented to the skill owner for the decision, not persisted.

# Rubric Changelog

All notable changes to `rubric.yaml`. Versioning is semver (normative source:
EVOLUTION.md step 5b):
**MAJOR** = pillar weight changes, pillar restructuring, check
removal/renumbering/meaning changes, scoring-formula or maturity-band changes,
new modes, scoring-engine edits (accepted scoring-change and new-mode
proposals edit scoring.md / SKILL.md and are always MAJOR);
**MINOR** = new checks, check scope clarifications that change what earns
points; **PATCH** = evidence hints, wording, typos.
Entries are added only by evolve mode with the skill owner's approval (except
this initial release). Each entry lists the PROP ids applied, or "initial".

## [2.0.0] — 2026-07-29

Initial versioned release. Restructures the v1 skill (monolithic SKILL.md,
2026) into the v2 architecture: the rubric is now a versioned data file
separate from the audit engine.

Hardened pre-release after adversarial verification and a live smoke test
(agent-starter): semver policy unified, bands made half-open, deterministic
repo_slug/date/rounding rules, partial + dry-run modes, scoring anchors on
all 50 checks.

Second hardening pass (dual-model review: Codex + Opus 5, 2026-07-29):
semver policy contradiction resolved (new modes and engine edits folded into
MAJOR everywhere); proposals filed after ANY audit including partial, never
in a dry-run; timestamped history filenames (`<slug>-<YYYY-MM-DD-HHMMSS>.json`)
with read-before-write compare baselining; compare deltas computed on the
common check set with the headline labeled separately; gaps-table cap
single-sourced in scoring.md §2.4 plus an unrounded gap-sum aggregation rule;
sign-correct half-away-from-zero rounding; weights/bands single-sourced to
rubric.yaml with worked examples marked illustrative; evolve-mode bookkeeping
(last_updated + added_in maintenance, 11-item verification checklist,
scoring-change proposals may target maturity_bands or the §4 history-JSON
schema, with schema_version bumped iff §4.1 changed); namespaced
concurrent-safe proposal ids (`PROP-YYYYMMDD-<repo-slug>-NN`) with
three-section scans, post-append collision re-read with HHMMSS suffix rename,
and an accepted-ledger format (Accepted/Applied in/As
modified); deterministic inputs (target resolution, pillar-name resolution,
lowercased exact model id); mechanical files_examined definition with a
files_manifest reproducibility record and a distinct_evidence_paths companion
metric; 100% measurable output template (no element is prose-only); scoring
anchors extended from 7 checks to all 50; skill directory git-tracked with
best-effort post-audit commits.

### Added
- `rubric.yaml`: 8 pillars, 50 checks. The 43 v1 checks and all pillar weights
  are extracted verbatim from v1 SKILL.md — Govern (20), Prove (20), Context &
  Data (12), Decision Engine (14), Orchestration & Humans (10), Shared
  Platform (10), Rollout Maturity (8), NFR Foundations (6). Scoring method
  (0/1/2 per check, weighted pillar average, N/A renormalization) and maturity
  band boundaries (Fragile <40.0, Developing 40.0-<60.0, Production-Capable
  60.0-<80.0, Production-Grade >=80.0; half-open intervals — rubric.yaml
  `maturity_bands` is authoritative) carried over from v1.
- 7 new 2026-era checks, each carrying a recorded `rationale`: G8 prompt
  injection defense, G9 tool and MCP security, G10 agent execution sandboxing
  (Govern now 10 checks), P8 adversarial and safety evals (Prove 8), C6 memory
  and context hygiene (Context & Data 6), D7 structured output validation
  (Decision Engine 7), S6 supply chain integrity (Shared Platform 6).
- `EVOLUTION.md`: self-improvement protocol — mandatory >=1 proposal per audit
  (max 3), guardrails, evolve mode with owner-only approval and semver bumps.
- `PROPOSALS.md` and this changelog.
- **gaps mode**: reports only missing/partial checks, ranked by weighted point
  gain ("adding X gains +N.N points").
- **compare mode** + `history/`: every full/gaps/compare audit writes a JSON
  result; compare reports per-pillar deltas vs. the previous audit of the same
  repo, flagging cross-rubric-version comparisons and recomputing their deltas
  deterministically on the common check set (scoring.md §3).
- **evolve mode**: reviews pending proposals with impact analysis against
  history/; the skill owner decides; accepted changes bump this version.
- Metrics-first output language: files scanned, checks evidenced vs. absent,
  evidence density, point deltas.

### Changed
- All v1 checks, weights, scoring, and maturity bands carry over unchanged.
  The 7 new checks mean v2.0.0 scores are approximately — not exactly —
  comparable to informal v1 audits: repos without 2026-era controls score
  lower under 2.0.0 because the new checks enter their pillar denominators.

### Proposals applied
- initial (pre-protocol release)

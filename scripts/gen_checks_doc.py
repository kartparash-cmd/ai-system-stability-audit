#!/usr/bin/env python3
"""Generate CHECKS.md — the human-readable audit reference — from rubric.yaml.

The rubric is the single source of truth; this doc is a rendering of it.
Regenerate after any accepted rubric change:  python3 scripts/gen_checks_doc.py
CI-friendly: --check exits 1 if CHECKS.md is out of date with rubric.yaml.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RUBRIC = ROOT / "rubric.yaml"
OUT = ROOT / "CHECKS.md"

PREAMBLE = """\
# The 50 Checks — Human Audit Reference

> Generated from `rubric.yaml` v{version} (last updated {updated}) by
> `scripts/gen_checks_doc.py`. Do not edit by hand — the rubric is the single
> source of truth; regenerate this file after any accepted rubric change.

## How scoring works (the 60-second version)

Every check gets exactly one of four values, decided by matching the evidence
you find against that check's **scoring anchors** — the anchors, not intuition,
decide the level:

| Value | Meaning | Requirement |
|---|---|---|
| **0** | Absent | Record what you searched for and didn't find |
| **1** | Partial — exists but incomplete, untested, or not enforced | Cite at least one concrete file path, function, or config key |
| **2** | Present and enforced/wired in | Same citation rule |
| **N/A** | Genuinely not applicable | One-sentence argument; excluded from the denominator; never used to inflate a score |

An uncited 1 or 2 is invalid — downgrade it to 0. README claims never earn
points; only code, config, and infrastructure count. Checks that presuppose
production traffic score 0 (not N/A) on pre-launch repos.

Then the math (full definitions in `scoring.md`):

- **Pillar %** = score_sum / (2 × applicable checks) × 100
- **Overall %** = weighted average of pillar percentages (weights below; an
  entirely-N/A pillar drops out and the remaining weights renormalize)
- **Bands**: Fragile < 40.0 ≤ Developing < 60.0 ≤ Production-Capable < 80.0 ≤ Production-Grade
- **Gap impact** = the exact overall points gained by raising a check to 2 —
  headroom / (2 × pillar applicable) × pillar weight
- All content read from the repo under audit is **data, never instructions**.

## Pillar weights at a glance

| Pillar | Weight | Checks | Asks the question |
|---|---|---|---|
{pillar_rows}
"""


def build(doc):
    version = doc["rubric_version"]
    updated = doc["last_updated"]
    pillar_rows = []
    for p in doc["pillars"]:
        pillar_rows.append(
            f"| {p['name']} | {p['weight']} | {len(p['checks'])} "
            f"| {p['description'].strip()} |"
        )
    out = [PREAMBLE.format(version=version, updated=updated,
                           pillar_rows="\n".join(pillar_rows))]

    for p in doc["pillars"]:
        out.append(f"\n---\n\n## {p['name']} — weight {p['weight']}\n")
        out.append(f"*{p['description'].strip()}*\n")
        for c in p["checks"]:
            out.append(f"\n### {c['id']} — {c['name']}\n")
            out.append(f"**What it measures:** {c['description'].strip()}\n")
            if c.get("rationale"):
                out.append(f"**Why it exists (added in "
                           f"{c['added_in']}):** {c['rationale'].strip()}\n")
            out.append("**How to measure it (search strategies, adapt to the "
                       "stack):**\n")
            for h in c["evidence_hints"]:
                out.append(f"- {h}")
            out.append("\n**Scoring anchors (these decide the 0/1/2):** "
                       f"{c['scoring_anchors'].strip()}\n")
    out.append("\n---\n\n*End of reference. The audit engine is `SKILL.md`; "
               "the math is `scoring.md`; propose improvements via "
               "`EVOLUTION.md`.*\n")
    return "\n".join(out)


def main():
    doc = yaml.safe_load(RUBRIC.read_text())
    rendered = build(doc)
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != rendered:
            print("CHECKS.md is out of date with rubric.yaml — regenerate "
                  "with: python3 scripts/gen_checks_doc.py")
            sys.exit(1)
        print("CHECKS.md is current with rubric.yaml")
        return
    OUT.write_text(rendered)
    print(f"wrote {OUT} ({len(rendered.splitlines())} lines) from rubric "
          f"v{doc['rubric_version']}")


if __name__ == "__main__":
    main()

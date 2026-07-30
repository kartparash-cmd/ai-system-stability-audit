#!/usr/bin/env python3
"""Repo self-validation for the ai-system-stability-audit skill.

Checks (exit 0 = all pass, exit 1 = any failure, with a message per failure):
  (a) rubric.yaml parses; pillar weights sum to 100; exactly 50 checks; every
      check has non-empty id/name/description/evidence_hints/scoring_anchors/
      added_in; check ids unique.
  (b) SKILL.md frontmatter parses as YAML; description <= 1024 chars.
  (c) every history/*.json parses, conforms to the scoring.md section 4.1
      schema, and its internal math recomputes (pillar pct, overall pct).
  (d) cross-file literals: the evolve-checklist item count claimed in
      CHANGELOG.md matches the numbered items in EVOLUTION.md's checklist.

stdlib + pyyaml only.
"""
import json
import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ERRORS = []
EXPECTED_CHECK_COUNT = 50


def err(msg):
    ERRORS.append(msg)


def half_up(x, decimals=1):
    """Round half away from zero, per scoring.md section 1.6."""
    factor = 10 ** decimals
    return math.copysign(math.floor(abs(x) * factor + 0.5), x) / factor


def is_1dp(value):
    """True if value is a number already rounded to 1 decimal place."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return abs(value * 10 - round(value * 10)) < 1e-9


# ---------------------------------------------------------------- (a) rubric
def check_rubric():
    path = ROOT / "rubric.yaml"
    try:
        rubric = yaml.safe_load(path.read_text())
    except Exception as e:
        err(f"rubric.yaml: does not parse as YAML: {e}")
        return None

    pillars = rubric.get("pillars")
    if not isinstance(pillars, list) or not pillars:
        err("rubric.yaml: 'pillars' missing or not a non-empty list")
        return None

    weight_sum = sum(p.get("weight", 0) for p in pillars)
    if weight_sum != 100:
        err(f"rubric.yaml: pillar weights sum to {weight_sum}, expected 100")

    required_fields = ("id", "name", "description", "evidence_hints",
                       "scoring_anchors", "added_in")
    seen_ids = set()
    total_checks = 0
    for pillar in pillars:
        pid = pillar.get("id", "<missing pillar id>")
        for check in pillar.get("checks", []) or []:
            total_checks += 1
            cid = check.get("id") or f"<unnamed check in {pid}>"
            for field in required_fields:
                value = check.get(field)
                empty = (value is None
                         or (isinstance(value, str) and not value.strip())
                         or (isinstance(value, list) and not value))
                if empty:
                    err(f"rubric.yaml: check {cid} (pillar {pid}) has "
                        f"missing/empty '{field}'")
            if check.get("id"):
                if check["id"] in seen_ids:
                    err(f"rubric.yaml: duplicate check id {check['id']}")
                seen_ids.add(check["id"])

    if total_checks != EXPECTED_CHECK_COUNT:
        err(f"rubric.yaml: {total_checks} checks found, "
            f"expected exactly {EXPECTED_CHECK_COUNT}")
    return rubric


# ------------------------------------------------------------- (b) SKILL.md
def check_skill_md():
    path = ROOT / "SKILL.md"
    text = path.read_text()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        err("SKILL.md: no '---'-delimited YAML frontmatter block at the top")
        return
    try:
        front = yaml.safe_load(m.group(1))
    except Exception as e:
        err(f"SKILL.md: frontmatter does not parse as YAML: {e}")
        return
    if not isinstance(front, dict):
        err("SKILL.md: frontmatter is not a YAML mapping")
        return
    desc = front.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("SKILL.md: frontmatter 'description' missing or empty")
    elif len(desc) > 1024:
        err(f"SKILL.md: frontmatter description is {len(desc)} chars "
            f"(hard cap 1024)")


# ------------------------------------------------------------- (c) history
REQUIRED_HISTORY_KEYS = [
    "schema_version", "repo", "repo_slug", "date", "rubric_version", "model",
    "mode", "overall_pct", "band", "evidence_density_pct",
    "distinct_evidence_paths", "files_examined", "files_total",
    "configs_examined", "coverage_pct", "files_manifest", "pillars", "checks",
    "na_checks", "top_gaps", "compared_to",
]
VALID_MODES = {"full", "gaps", "compare"}
VALID_SCORES = {0, 1, 2, None}


def check_history_file(path, pillar_ids):
    name = f"history/{path.name}"
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        err(f"{name}: does not parse as JSON: {e}")
        return

    missing = [k for k in REQUIRED_HISTORY_KEYS if k not in data]
    if missing:
        err(f"{name}: missing required keys: {', '.join(missing)}")

    if data.get("mode") not in VALID_MODES:
        err(f"{name}: mode {data.get('mode')!r} not in "
            f"{sorted(VALID_MODES)}")

    # checks: score domain, na justification, evidence presence
    checks = data.get("checks", {})
    null_score_ids = []
    if not isinstance(checks, dict):
        err(f"{name}: 'checks' is not an object")
        checks = {}
    for cid, entry in checks.items():
        if not isinstance(entry, dict):
            err(f"{name}: check {cid} entry is not an object")
            continue
        score = entry.get("score")
        if isinstance(score, bool) or score not in VALID_SCORES:
            err(f"{name}: check {cid} score {score!r} not in {{0, 1, 2, null}}")
            continue
        if score is None:
            null_score_ids.append(cid)
            if not str(entry.get("na") or "").strip():
                err(f"{name}: check {cid} has null score but no 'na' "
                    f"justification")
        else:
            if not str(entry.get("evidence") or "").strip():
                err(f"{name}: check {cid} scored {score} but has no "
                    f"'evidence' line")

    # 1-decimal numeric fields
    for field in ("overall_pct", "evidence_density_pct", "coverage_pct"):
        if field in data and not is_1dp(data[field]):
            err(f"{name}: {field} = {data.get(field)!r} is not a number "
                f"rounded to 1 decimal place")

    # pillars: keyed by the 8 rubric pillar ids, internal math recomputes
    pillars = data.get("pillars", {})
    if not isinstance(pillars, dict):
        err(f"{name}: 'pillars' is not an object")
        pillars = {}
    if pillar_ids is not None and set(pillars) != set(pillar_ids):
        err(f"{name}: pillar keys {sorted(pillars)} != rubric pillar ids "
            f"{sorted(pillar_ids)}")

    applicable_pillars = []  # (weight, unrounded_pct)
    for pid, p in pillars.items():
        if not isinstance(p, dict):
            err(f"{name}: pillar {pid} entry is not an object")
            continue
        missing_pf = [k for k in ("weight", "applicable", "score_sum", "pct")
                      if k not in p]
        if missing_pf:
            err(f"{name}: pillar {pid} missing keys: {', '.join(missing_pf)}")
            continue
        weight, applicable, score_sum, pct = (
            p["weight"], p["applicable"], p["score_sum"], p["pct"])
        if applicable == 0:
            if pct is not None:
                err(f"{name}: pillar {pid} has applicable=0 but pct={pct!r} "
                    f"(must be null)")
            continue
        exact = score_sum / (2 * applicable) * 100
        applicable_pillars.append((weight, exact))
        if not is_1dp(pct):
            err(f"{name}: pillar {pid} pct {pct!r} is not a number rounded "
                f"to 1 decimal place")
        elif abs(half_up(exact) - pct) > 1e-9:
            err(f"{name}: pillar {pid} pct {pct} != recomputed "
                f"{half_up(exact)} (= {score_sum}/(2x{applicable})x100 "
                f"half-up)")

    # overall recompute (weight-normalized over applicable pillars)
    if applicable_pillars and isinstance(data.get("overall_pct"), (int, float)):
        weight_total = sum(w for w, _ in applicable_pillars)
        if weight_total > 0:
            overall = sum(pct * (w / weight_total * 100)
                          for w, pct in applicable_pillars) / 100
            if abs(data["overall_pct"] - overall) > 0.05 + 1e-9:
                err(f"{name}: overall_pct {data['overall_pct']} differs from "
                    f"weight-normalized recompute {overall:.4f} by more "
                    f"than 0.05")

    # na_checks consistent with null scores
    na_checks = data.get("na_checks", [])
    if isinstance(na_checks, list):
        if set(na_checks) != set(null_score_ids):
            err(f"{name}: na_checks {sorted(na_checks)} inconsistent with "
                f"null-score checks {sorted(null_score_ids)}")
    else:
        err(f"{name}: 'na_checks' is not an array")

    # top_gaps: 1-decimal impact_pts
    top_gaps = data.get("top_gaps", [])
    if isinstance(top_gaps, list):
        for i, gap in enumerate(top_gaps):
            if not isinstance(gap, dict):
                err(f"{name}: top_gaps[{i}] is not an object")
                continue
            if not is_1dp(gap.get("impact_pts")):
                err(f"{name}: top_gaps[{i}] impact_pts "
                    f"{gap.get('impact_pts')!r} is not a number rounded to "
                    f"1 decimal place")
    else:
        err(f"{name}: 'top_gaps' is not an array")


def check_history(rubric):
    pillar_ids = None
    if rubric and isinstance(rubric.get("pillars"), list):
        pillar_ids = [p.get("id") for p in rubric["pillars"]]
    history_dir = ROOT / "history"
    if not history_dir.is_dir():
        return
    for path in sorted(history_dir.glob("*.json")):
        check_history_file(path, pillar_ids)


# ------------------------------------------------- (d) cross-file literals
def evolve_checklist_item_count():
    """Count the numbered items of EVOLUTION.md's verify-and-report checklist."""
    text = (ROOT / "EVOLUTION.md").read_text()
    lines = text.splitlines()
    intro_idx = None
    for i, line in enumerate(lines):
        if re.search(r"\b\d+-item checklist\b", line):
            intro_idx = i
            break
    if intro_idx is None:
        return None
    count = 0
    for line in lines[intro_idx + 1:]:
        if line.startswith("#"):
            break  # next heading ends the checklist region
        m = re.match(r"^\s+(\d+)\.\s", line)
        if m and int(m.group(1)) == count + 1:
            count += 1
    return count


def check_cross_file_literals():
    actual = evolve_checklist_item_count()
    if actual is None:
        err("EVOLUTION.md: could not locate the 'N-item checklist' intro line")
        return
    changelog = (ROOT / "CHANGELOG.md").read_text()
    claims = re.findall(r"(\d+)-item(?:\s+verification)?\s+checklist",
                        changelog)
    if not claims:
        return  # nothing claimed, nothing to cross-check
    for claim in claims:
        if int(claim) != actual:
            err(f"CHANGELOG.md claims a {claim}-item evolve checklist but "
                f"EVOLUTION.md's checklist has {actual} numbered items")


def main():
    rubric = check_rubric()
    check_skill_md()
    check_history(rubric)
    check_cross_file_literals()

    if ERRORS:
        for e in ERRORS:
            print(f"FAIL: {e}")
        print(f"\nvalidate.py: {len(ERRORS)} failure(s)")
        return 1
    print("validate.py: all checks passed "
          "(rubric, SKILL.md frontmatter, history schema + math, "
          "cross-file literals)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

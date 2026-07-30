#!/usr/bin/env python3
"""Outcome tracker (rubric check P4): did audited repos actually close their gaps?

Reads history/*.json, pairs consecutive audits of the same repo_slug, and reports
per-pair gap-closure. The all-pair gap-closure rate is the skill's task success rate.
Reporting tool, not a gate — always exits 0. Stdlib only.
"""
import argparse
import json
import re
import statistics
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HISTORY = Path(__file__).resolve().parent.parent / "history"
FNAME = re.compile(r"^(?P<slug>.+)-(?P<ts>\d{4}-\d{2}-\d{2}-\d{6})(?:-(?P<suffix>\d+))?\.json$")



def unrounded_overall(entry):
    """Full-precision overall from stored pillar score_sum/applicable (§1.2-§1.4)."""
    pillars = entry.get("pillars", {})
    live = {p: d for p, d in pillars.items() if d.get("pct") is not None}
    mass = sum(d["weight"] for d in live.values()) or 1
    return sum(
        (d["score_sum"] / (2 * d["applicable"]) * 100) * (d["weight"] / mass * 100)
        for d in live.values() if d.get("applicable")
    ) / 100

def round1(x):
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def sort_key(path):
    m = FNAME.match(path.name)
    if not m:
        return (path.name, 0)
    return (m.group("ts"), int(m.group("suffix") or 1))  # -2 suffix sorts AFTER unsuffixed


def load_audits():
    audits = {}
    for path in sorted(HISTORY.glob("*.json"), key=sort_key):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"warning: skipping unreadable {path.name}: {exc}", file=sys.stderr)
            continue
        data["_file"] = path.name
        audits.setdefault(data.get("repo_slug", "unknown"), []).append(data)
    return audits


def pair_outcome(earlier, later):
    gaps = earlier.get("top_gaps", [])
    closed = []
    for gap in gaps:
        check = gap["check"]
        before = gap.get("from", (earlier.get("checks", {}).get(check) or {}).get("score", 0))
        after = (later.get("checks", {}).get(check) or {}).get("score")
        if isinstance(after, (int, float)) and before is not None and after > before:
            closed.append(check)
    total = len(gaps)
    d0, d1 = date.fromisoformat(earlier["date"]), date.fromisoformat(later["date"])
    return {
        "from_file": earlier["_file"],
        "to_file": later["_file"],
        "gaps_closed": len(closed),
        "gaps_total": total,
        "closed_checks": closed,
        "resolution_rate_pct": round1(100.0 * len(closed) / total) if total else None,
        # per scoring.md §2.5: recompute both sides at full precision from stored
        # pillar sums — never subtract the stored 1-decimal rounded overall values
        "overall_delta": round1(unrounded_overall(later) - unrounded_overall(earlier)),
        "band_change": (f'{earlier["band"]} -> {later["band"]}'
                        if earlier["band"] != later["band"] else "none"),
        "days_between": (d1 - d0).days,
    }


def build_report(audits):
    slugs, closed_sum, total_sum = {}, 0, 0
    for slug, runs in sorted(audits.items()):
        pairs = [pair_outcome(runs[i], runs[i + 1]) for i in range(len(runs) - 1)]
        closed_sum += sum(p["gaps_closed"] for p in pairs)
        total_sum += sum(p["gaps_total"] for p in pairs)
        entry = {"audits": len(runs), "pairs": pairs}
        durations = [r["duration_seconds"] for r in runs
                     if isinstance(r.get("duration_seconds"), (int, float))]
        if durations:
            entry["duration_seconds"] = {"min": min(durations),
                                         "median": statistics.median(durations),
                                         "max": max(durations)}
        slugs[slug] = entry
    return {
        "slugs": slugs,
        "summary": {
            "consecutive_pairs": sum(len(e["pairs"]) for e in slugs.values()),
            "gaps_closed": closed_sum,
            "gaps_total": total_sum,
            "task_success_rate_pct": round1(100.0 * closed_sum / total_sum) if total_sum else None,
        },
    }


def print_table(report):
    for slug, entry in report["slugs"].items():
        print(f"\n== {slug} ({entry['audits']} audits, {len(entry['pairs'])} consecutive pairs)")
        if not entry["pairs"]:
            print("  (single audit — no consecutive pair to evaluate)")
        else:
            hdr = f"  {'pair':<28} {'closed':>6} {'total':>5} {'rate%':>6} {'Δoverall':>8} {'days':>4}  band change"
            print(hdr)
            print("  " + "-" * (len(hdr) - 2))
            for p in entry["pairs"]:
                label = f"{p['from_file'][-11:-5]} -> {p['to_file'][-11:-5]}"
                rate = "n/a" if p["resolution_rate_pct"] is None else f"{p['resolution_rate_pct']:.1f}"
                print(f"  {label:<28} {p['gaps_closed']:>6} {p['gaps_total']:>5} {rate:>6}"
                      f" {p['overall_delta']:>+8.1f} {p['days_between']:>4}  {p['band_change']}")
                if p["closed_checks"]:
                    print(f"    closed: {', '.join(p['closed_checks'])}")
        if "duration_seconds" in entry:
            d = entry["duration_seconds"]
            print(f"  duration_seconds: min {d['min']} / median {d['median']} / max {d['max']}")
    s = report["summary"]
    rate = "n/a (no consecutive pairs)" if s["task_success_rate_pct"] is None \
        else f"{s['task_success_rate_pct']:.1f}%"
    print(f"\nAll slugs: {s['gaps_closed']} of {s['gaps_total']} tracked gaps closed across "
          f"{s['consecutive_pairs']} consecutive pairs -> task success rate {rate}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args()
    audits = load_audits()
    if not audits:
        print(json.dumps({"slugs": {}, "summary": None}) if args.json
              else f"no history entries found in {HISTORY}")
        return 0
    report = build_report(audits)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_table(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

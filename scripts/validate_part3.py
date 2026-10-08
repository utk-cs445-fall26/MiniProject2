#!/usr/bin/env python3
"""Check Part 3 edge cases and saved deliverables without changing any files."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

if __package__:
    from . import analyze_part3 as analysis
else:
    import analyze_part3 as analysis


ROOT = Path(__file__).resolve().parents[1]


def epoch(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def boundary(month, following=False):
    year, number = map(int, month.split("-"))
    if following:
        year, number = (year + 1, 1) if number == 12 else (year, number + 1)
    return int(datetime(year, number, 1, tzinfo=timezone.utc).timestamp())


def fixture(number, timestamp, author="Example <example@example.org>"):
    return {"project_wocid": "example", "commit_sha1": f"{number:040x}",
            "author": author, "time": str(timestamp), "commit message": 'A; "message"\n'}


def must_reject(operation):
    try:
        operation()
    except (AssertionError, ValueError):
        return
    raise AssertionError("Invalid input was accepted")


def check_logic():
    gap = {"LongestGapStart": "2020-02", "LongestGapEnd": "2020-03", "LongestGapLength": "2"}
    start, after = boundary("2020-02"), boundary("2020-03", following=True)
    before_rows = [fixture(i, start - 14 + i) for i in range(14)]
    before_rows += [fixture(50, start - 1), fixture(51, start - 1)]
    after_rows = [fixture(100 + i, after + i) for i in range(14)]
    after_rows += [fixture(70, after), fixture(71, after)]
    unknown = fixture(999, "")
    selected = analysis.select_gap_commits(list(reversed(before_rows + after_rows + [unknown])), gap)
    assert [int(r["commit_sha1"], 16) for r in selected["pre"]] == list(range(6, 14)) + [50, 51]
    assert [int(r["commit_sha1"], 16) for r in selected["post"]] == [70, 71] + list(range(100, 108))
    assert selected["pre"][-1]["time"] == str(start - 1)
    assert selected["post"][0]["time"] == str(after)
    assert selected["post"][0]["commit message"] == 'A; "message"\n'
    few = analysis.select_gap_commits([before_rows[0], after_rows[0], before_rows[1]], gap)
    assert few == {"pre": before_rows[:2], "post": after_rows[:1]}
    no_gap = {"LongestGapStart": "", "LongestGapEnd": "", "LongestGapLength": "0"}
    assert analysis.select_gap_commits(before_rows + after_rows, no_gap) == {"pre": [], "post": []}
    for inside in (start, after - 1):
        must_reject(lambda: analysis.select_gap_commits([fixture(800, inside)], gap))
    year_gap = {"LongestGapStart": "2020-12", "LongestGapEnd": "2020-12", "LongestGapLength": "1"}
    year_rows = [fixture(1, epoch("2020-11-30T23:59:59Z")), fixture(2, epoch("2021-01-01T00:00:00Z"))]
    assert analysis.select_gap_commits(year_rows, year_gap) == {"pre": year_rows[:1], "post": year_rows[1:]}

    labels = [{"commit_sha1": str(i), "theme": theme, "reason": "Reviewed message."}
              for i, theme in enumerate(["Bug fixes", "Feature development", "Bug fixes", "Feature development"])]
    assert analysis.summarize_themes(labels, ["0", "1", "2", "3"]) == (
        "Feature development:Bug fixes", {"Feature development": 2, "Bug fixes": 2})
    assert analysis.summarize_themes(labels[:1], ["0"]) == ("Bug fixes", {"Bug fixes": 1})
    assert analysis.summarize_themes([], []) == ("", {})
    must_reject(lambda: analysis.summarize_themes(labels, ["1", "0", "2", "3"]))
    must_reject(lambda: analysis.summarize_themes([{**labels[0], "theme": "Invented"}], ["0"]))
    veteran = fixture(1, start - 100, "Veteran <v@example.org>")
    returning = fixture(100, after, veteran["author"])
    newcomer = fixture(101, after + 1, "New identity <n@example.org>")
    comparison = analysis.compare_authors([veteran] + before_rows, gap, [returning, newcomer])
    assert comparison == {"returning": [veteran["author"]], "new": [newcomer["author"]]}


def read_csv(path, expected_columns):
    columns, rows = analysis.read_csv(path)
    assert columns == expected_columns, f"Unexpected columns in {path}"
    return rows


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def theme_summary(annotations):
    counts = Counter(item["theme"] for item in annotations)
    assert set(counts) <= set(analysis.THEMES)
    assert all(item["reason"].strip() for item in annotations)
    ordered = sorted(counts, key=lambda theme: (-counts[theme], analysis.THEMES.index(theme)))
    return ":".join(ordered[:2]), dict(counts)


def check_final(root):
    """Recompute selections using epoch boundaries, independently of the selector."""
    netid, data = analysis.NETID, root / "data"
    source_path = root / f"{netid}_project_summary.csv"
    source = read_csv(source_path, analysis.SOURCE_COLUMNS)
    stats = read_csv(root / f"{netid}_project_stats.csv", analysis.BASE_COLUMNS + analysis.PART3_COLUMNS)
    projects = [row["Project"] for row in stats]
    with (root / "net2prj.csv").open(newline="", encoding="utf-8-sig") as handle:
        assigned = [row["WoC"] for row in csv.DictReader(handle) if row["netID"] == netid]
    assert len(projects) == len(set(projects)) == 10 and set(projects) == set(assigned)
    snapshot = read_csv(data / f"{netid}_part2_stats.csv", analysis.BASE_COLUMNS)
    assert [{key: row[key] for key in analysis.BASE_COLUMNS} for row in stats] == snapshot
    part2 = read_json(data / f"{netid}_part2_validation.json")
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == part2["source_summary_sha256"]
    research = read_json(data / f"{netid}_part3_interpretations.json")["projects"]
    github = read_json(data / f"{netid}_part3_github.json")
    recent_labels = read_json(data / f"{netid}_part3_recent_themes.json")
    report = read_json(data / f"{netid}_part3_validation.json")
    assert set(research) == set(github["projects"]) == set(recent_labels) == set(projects)
    assert github["as_of_utc"] == report["as_of_utc"] == "2025-09-30T23:59:59Z"
    assert report["active_since_utc"] == "2025-04-01T00:00:00Z"
    expected_gap, expected_recent = [], []
    recent_columns = ["project_wocid", "commit_sha1", "author", "author_date", "committer_date",
                      "commit message", "commit_url", "theme", "theme_reason"]
    for row in stats:
        project, study = row["Project"], research[row["Project"]]
        dated = sorted((r for r in source if r["project_wocid"] == project and r["time"]),
                       key=lambda r: (int(r["time"]), r["commit_sha1"]))
        if row["LongestGapStart"]:
            start, stop = boundary(row["LongestGapStart"]), boundary(row["LongestGapEnd"], following=True)
            assert not any(start <= int(r["time"]) < stop for r in dated)
            previous = [r for r in dated if int(r["time"]) < start]
            chosen = {"pre": previous[-10:], "post": [r for r in dated if int(r["time"]) >= stop][:10]}
        else:
            previous, chosen = [], {"pre": [], "post": []}
            assert row["HypothesizedGapReason"] == "N/A active Project"
        assert study["gap"]["start"] == row["LongestGapStart"]
        assert study["gap"]["end"] == row["LongestGapEnd"]
        assert int(study["gap"]["length"]) == int(row["LongestGapLength"])
        for side, column in (("pre", "BeforeThemes"), ("post", "AfterThemes")):
            sample, annotations = chosen[side], study[side]
            assert [r["commit_sha1"] for r in sample] == [a["commit_sha1"] for a in annotations]
            for original, annotation in zip(sample, annotations):
                for key in ("author", "time"):
                    if key in annotation:
                        assert str(annotation[key]) == original[key]
                if "message" in annotation:
                    assert annotation["message"] == original["commit message"]
            themes, counts = theme_summary(annotations)
            assert row[column] == (themes if row["LongestGapStart"] else "N/A active Project")
            assert report["projects"][project]["theme_counts"][side] == counts
            assert report["projects"][project][side + "_count"] == len(sample)
            expected_gap.extend({"pre/post": side, **r} for r in sample)
        old_authors, after_authors = {r["author"] for r in previous}, {r["author"] for r in chosen["post"]}
        comparison = {"returning": sorted(old_authors & after_authors), "new": sorted(after_authors - old_authors)}
        assert report["projects"][project]["post_author_comparison"] == comparison
        if "post_author_comparison" in study:
            recorded = study["post_author_comparison"]
            assert {key: recorded[key] for key in ("returning", "new")} == comparison
            if "all_pre_gap_author_count" in recorded:
                assert int(recorded["all_pre_gap_author_count"]) == len(old_authors)
        g = github["projects"][project]
        recent = g["recent_commits"]
        assert len(recent) == min(10, g["eligible_commits_on_reconstructed_history"])
        assert recent == sorted(recent, key=lambda c: (-epoch(c["committer_date"]), c["commit_sha1"]))
        assert all(epoch(c["committer_date"]) <= epoch(analysis.AS_OF) for c in recent)
        assert g["latest_commit_date"] == recent[0]["committer_date"]
        status = "Active" if epoch(recent[0]["committer_date"]) >= epoch(analysis.ACTIVE_SINCE) else "Inactive"
        assert row["Currentstatus"] == report["projects"][project]["Currentstatus"] == status
        annotations = recent_labels[project]
        assert [a["commit_sha1"] for a in annotations] == [c["commit_sha1"] for c in recent]
        themes, counts = theme_summary(annotations)
        assert row["RecentThemes"] == themes and report["projects"][project]["theme_counts"]["recent"] == counts
        for c, annotation in zip(recent, annotations):
            expected_recent.append({"project_wocid": project, **{key: c[key] for key in recent_columns[1:-2]},
                                    "theme": annotation["theme"], "theme_reason": annotation["reason"]})
        for key in ("HypothesizedGapReason", "HasRecovered", "WhyRecovered", "WhoRecovered", "Notes"):
            assert row[key] == study[key] and row[key].strip()
        notes = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", row["Notes"])
        assert 2 <= len(re.findall(r"[.!?](?:\s|$)", notes)) <= 4, f"Notes must contain 2–4 sentences: {project}"
        reflection = (root / f"{netid}_reflection_{project}.md").read_text(encoding="utf-8")
        assert project in reflection and netid in reflection and study["reflection"] in reflection
        assert row["Currentstatus"] in reflection and recent[0]["commit_url"] in reflection
        assert all(item["url"] in reflection for item in study["sources"])
    actual_gap = read_csv(root / f"{netid}_project_gap_commits.csv", ["pre/post"] + analysis.SOURCE_COLUMNS)
    assert actual_gap == expected_gap, "Gap CSV differs from original source selection"
    assert len(actual_gap) == len({(r["project_wocid"], r["commit_sha1"]) for r in actual_gap})
    assert read_csv(data / f"{netid}_recent_commits.csv", recent_columns) == expected_recent
    assert {p.name for p in root.glob(f"{netid}_reflection_*.md")} == {f"{netid}_reflection_{p}.md" for p in projects}
    assert report["project_count"] == 10 and report["gap_sample_rows"] == len(actual_gap)
    assert report["recent_sample_rows"] == len(expected_recent)
    print(f"Final checks passed: {len(actual_gap)} gap rows, {len(expected_recent)} recent rows, 10 reflections.")


def validate_part3(root=ROOT, logic_only=False):
    check_logic()
    print("Logic checks passed: UTC boundaries, ties, sample sizes, no gaps, themes, and author history.")
    if not logic_only:
        check_final(Path(root))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logic-only", action="store_true", help="Run synthetic checks before final files exist")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    validate_part3(args.root, logic_only=args.logic_only)


if __name__ == "__main__":
    main()

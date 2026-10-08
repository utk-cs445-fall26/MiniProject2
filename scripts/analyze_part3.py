#!/usr/bin/env python3
"""Reproduce Part 3 from saved commits, GitHub evidence, and reviewed themes."""

import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NETID = "dpate172"
BASE_COLUMNS = ["Project", "ncommits", "nauthors", "from", "to", "nstars", "nforks",
                "lastGHCommitDate", "LongestGapStart", "LongestGapEnd", "LongestGapLength",
                "NumCommitsAfterLastGap", "ActivityPattern", "NumberOfGapsInTimeline"]
PART3_COLUMNS = ["BeforeThemes", "AfterThemes", "HypothesizedGapReason", "HasRecovered",
                 "WhyRecovered", "WhoRecovered", "Currentstatus", "RecentThemes", "Notes"]
SOURCE_COLUMNS = ["project_wocid", "commit_sha1", "author", "time", "commit message"]
THEMES = ["Feature development", "Bug fixes", "Documentation updates", "Dependency updates",
          "Release", "Security patches", "Automated bot contributions", "Other"]
AS_OF = "2025-09-30T23:59:59Z"
ACTIVE_SINCE = "2025-04-01T00:00:00Z"
NA = "N/A active Project"


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return reader.fieldnames, list(reader)


def write_csv(path, columns, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def month(row):
    return datetime.fromtimestamp(int(row["time"]), timezone.utc).strftime("%Y-%m")


def select_gap_commits(rows, stats):
    """Last ten before, first ten after; preserve raw rows and author UTC dates."""
    dated = sorted((r for r in rows if r["time"]),
                   key=lambda r: (int(r["time"]), r["commit_sha1"]))
    if not stats["LongestGapStart"]:
        assert not stats["LongestGapEnd"] and int(stats["LongestGapLength"]) == 0
        return {"pre": [], "post": []}
    start, end = stats["LongestGapStart"], stats["LongestGapEnd"]
    assert not any(start <= month(r) <= end for r in dated), "The gap contains a dated commit"
    return {"pre": [r for r in dated if month(r) < start][-10:],
            "post": [r for r in dated if month(r) > end][:10]}


def summarize_themes(annotations, expected_shas):
    """One reviewed primary theme per commit; ties use the assignment's list order."""
    assert [a["commit_sha1"] for a in annotations] == expected_shas, "Theme sample has changed"
    assert all(a["theme"] in THEMES and a["reason"].strip() for a in annotations)
    counts = Counter(a["theme"] for a in annotations)
    ordered = sorted(counts, key=lambda theme: (-counts[theme], THEMES.index(theme)))
    return ":".join(ordered[:2]), {theme: counts[theme] for theme in ordered}


def compare_authors(rows, stats, post):
    if not stats["LongestGapStart"]:
        return {"returning": [], "new": []}
    previous = {r["author"] for r in rows if r["time"] and month(r) < stats["LongestGapStart"]}
    authors = {r["author"] for r in post}
    return {"returning": sorted(authors & previous), "new": sorted(authors - previous)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def analyze_part3(root=ROOT):
    root = Path(root)
    source_path = root / f"{NETID}_project_summary.csv"
    stats_path = root / f"{NETID}_project_stats.csv"
    columns, rows = read_csv(source_path)
    assert columns == SOURCE_COLUMNS
    columns, stats = read_csv(stats_path)
    assert columns in (BASE_COLUMNS, BASE_COLUMNS + PART3_COLUMNS)
    baseline = [{c: r[c] for c in BASE_COLUMNS} for r in stats]
    snapshot_path = root / "data" / f"{NETID}_part2_stats.csv"
    if snapshot_path.exists():
        saved_columns, saved = read_csv(snapshot_path)
        assert saved_columns == BASE_COLUMNS and baseline == saved, "Part 2 data changed; review Part 3 again"
    else:
        write_csv(snapshot_path, BASE_COLUMNS, baseline)
    part2 = json.loads((root / "data" / f"{NETID}_part2_validation.json").read_text())
    assert sha256(source_path) == part2["source_summary_sha256"], "Part 1 source changed"
    research = json.loads((root / "data" / f"{NETID}_part3_interpretations.json").read_text())["projects"]
    github = json.loads((root / "data" / f"{NETID}_part3_github.json").read_text())
    recent_labels = json.loads((root / "data" / f"{NETID}_part3_recent_themes.json").read_text())
    assert set(research) == {s["Project"] for s in stats} == set(recent_labels)
    assert len(stats) == 10 and github["as_of_utc"] == AS_OF
    gap_rows, recent_rows, report_projects, reflections = [], [], {}, {}
    for s in stats:
        project = s["Project"]
        project_rows = [r for r in rows if r["project_wocid"] == project]
        selected = select_gap_commits(project_rows, s)
        r = research[project]
        assert r["gap"]["start"] == s["LongestGapStart"] and r["gap"]["end"] == s["LongestGapEnd"]
        theme_counts = {}
        for side, field in (("pre", "BeforeThemes"), ("post", "AfterThemes")):
            shas = [row["commit_sha1"] for row in selected[side]]
            s[field], theme_counts[side] = summarize_themes(r[side], shas)
            if not s["LongestGapStart"]:
                s[field] = NA
            gap_rows.extend({"pre/post": side, **row} for row in selected[side])
        for field in ("HypothesizedGapReason", "HasRecovered", "WhyRecovered", "WhoRecovered", "Notes"):
            assert r[field].strip()
            s[field] = r[field]
        if not s["LongestGapStart"]:
            assert s["HypothesizedGapReason"] == NA
        g = github["projects"][project]
        recent = g["recent_commits"]
        assert 0 < len(recent) <= 10
        dates = [c["committer_date"] for c in recent]
        assert dates == sorted(dates, reverse=True) and all(d <= AS_OF for d in dates)
        assert g["latest_commit_date"] == dates[0]
        s["Currentstatus"] = "Active" if dates[0] >= ACTIVE_SINCE else "Inactive"
        s["RecentThemes"], theme_counts["recent"] = summarize_themes(
            recent_labels[project], [c["commit_sha1"] for c in recent])
        for c, annotation in zip(recent, recent_labels[project]):
            recent_rows.append({"project_wocid": project, **{key: c[key] for key in
                ["commit_sha1", "author", "author_date", "committer_date", "commit message", "commit_url"]},
                "theme": annotation["theme"], "theme_reason": annotation["reason"]})
        comparison = compare_authors(project_rows, s, selected["post"])
        report_projects[project] = {"pre_count": len(selected["pre"]), "post_count": len(selected["post"]),
            "recent_count": len(recent), "omitted_undated": sum(not row["time"] for row in project_rows),
            "theme_counts": theme_counts, "post_author_comparison": comparison,
            "latest_github_commit_as_of_cutoff": dates[0], "Currentstatus": s["Currentstatus"]}
        reflections[project] = make_reflection(s, r, g, report_projects[project])
    # Validate all outputs before changing the shared statistics file.
    assert len(gap_rows) == len({(r["project_wocid"], r["commit_sha1"]) for r in gap_rows})
    write_csv(root / f"{NETID}_project_gap_commits.csv", ["pre/post"] + SOURCE_COLUMNS, gap_rows)
    write_csv(root / "data" / f"{NETID}_recent_commits.csv",
              ["project_wocid", "commit_sha1", "author", "author_date", "committer_date",
               "commit message", "commit_url", "theme", "theme_reason"], recent_rows)
    write_csv(stats_path, BASE_COLUMNS + PART3_COLUMNS, stats)
    assert read_csv(stats_path)[1] == stats
    assert read_csv(root / f"{NETID}_project_gap_commits.csv")[1] == gap_rows
    for project, content in reflections.items():
        (root / f"{NETID}_reflection_{project}.md").write_text(content, encoding="utf-8")
    report = {"netid": NETID, "as_of_utc": AS_OF, "active_since_utc": ACTIVE_SINCE,
        "source_summary_sha256": sha256(source_path), "part2_stats_sha256": sha256(snapshot_path),
        "project_count": len(stats), "gap_sample_projects": len({r["project_wocid"] for r in gap_rows}),
        "gap_sample_rows": len(gap_rows), "recent_sample_rows": len(recent_rows),
        "projects": report_projects}
    (root / "data" / f"{NETID}_part3_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    return stats, gap_rows, recent_rows, report


def make_reflection(stats, research, github, report):
    project = stats["Project"]
    gap_unit = "month" if int(stats["LongestGapLength"]) == 1 else "months"
    gap = (f"{stats['LongestGapStart']} through {stats['LongestGapEnd']} "
           f"({stats['LongestGapLength']} {gap_unit})") if stats["LongestGapStart"] else "No zero-commit months"
    paragraphs = [f"# {project}\n\nNetID: {NETID}",
        f"Longest gap: **{gap}**. Activity pattern: **{stats['ActivityPattern']}**.",
        research["reflection"],
        f"**Before / after themes:** {stats['BeforeThemes']} / {stats['AfterThemes']}. "
        f"The samples contain {report['pre_count']} commits before and {report['post_count']} after the gap.",
        f"**Recovery:** {stats['HasRecovered'].rstrip('.')}. {stats['WhyRecovered']} {stats['WhoRecovered']}"]
    if stats["LongestGapStart"] and any(len(report["theme_counts"][side]) == 1 for side in ("pre", "post")):
        paragraphs.append("A sample with only one supported theme keeps that single label; a second theme is not invented.")
    if report["omitted_undated"]:
        paragraphs.append(f"{report['omitted_undated']} source record(s) have no timestamp and are excluded from time-based selections. "
                          "The result describes the dated records available in Part 1.")
    latest = github["recent_commits"][0]
    paragraphs.append(f"**Status as of September 30, 2025:** {stats['Currentstatus']}. The latest eligible "
        f"[GitHub commit]({latest['commit_url']}) is dated {latest['committer_date']}. "
        f"The {report['recent_count']} most recent eligible commits give **{stats['RecentThemes']}**. "
        "This uses the assignment's April 1, 2025 cutoff and GitHub committer dates; "
        "the Part 1 lastGHCommitDate field keeps its later collection snapshot.")
    paragraphs.append("The gap samples use UTC author dates from Part 1, which includes commits outside the GitHub default branch. "
        "Recent themes use the saved default-branch history through the historical cutoff. "
        "Returning/new comparisons use complete pre-gap author strings; different names or emails can belong to the same person.")
    sources = [f"- [{s.get('title', s.get('kind', 'Supporting evidence'))}]({s['url']}): {s['what_it_establishes']}"
               for s in research["sources"]]
    paragraphs.append("Sources:\n\n" + "\n".join(sources))
    return "\n\n".join(paragraphs) + "\n"


if __name__ == "__main__":
    stats, gap_rows, recent_rows, report = analyze_part3()
    print(f"Created {len(gap_rows)} gap rows, {len(recent_rows)} recent rows, and {len(stats)} reflections.")

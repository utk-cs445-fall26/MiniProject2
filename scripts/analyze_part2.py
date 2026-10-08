#!/usr/bin/env python3
"""Aggregate Part 1 author timestamps into monthly activity and inactivity gaps.

Run with a reviewed interpretation map, for example:
    python scripts/analyze_part2.py --interpretations data/dpate172_interpretations.json

The map must provide an ActivityPattern for every project. This script does not
infer those visual interpretations. Missing timestamps remain missing and never
receive invented months. A project with no zero-commit month has blank gap dates,
gap length 0, and blank NumCommitsAfterLastGap (not applicable).
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

import pandas as pd


ROOT = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
PART1_COLUMNS = ["Project", "ncommits", "nauthors", "from", "to", "nstars", "nforks", "lastGHCommitDate"]
PART2_COLUMNS = ["LongestGapStart", "LongestGapEnd", "LongestGapLength",
                 "NumCommitsAfterLastGap", "ActivityPattern", "NumberOfGapsInTimeline"]
PART3_COLUMNS = ["BeforeThemes", "AfterThemes", "HypothesizedGapReason", "HasRecovered",
                 "WhyRecovered", "WhoRecovered", "Currentstatus", "RecentThemes", "Notes"]
SUMMARY_COLUMNS = ["project_wocid", "commit_sha1", "author", "time", "commit message"]
MONTHLY_COLUMNS = ["Month", "#Commits"]
PATTERNS = {"steady", "rising", "declining", "U-shaped", "cyclical", "irregular"}
PLOT_DPI = 320  # PNG resolution metadata remains above 300 after unit conversion.


def read_csv(path):
    """Use csv so text, blank fields, and the original stats values stay exact."""
    csv.field_size_limit(10 * 1024 * 1024)
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return reader.fieldnames, list(reader)


def write_csv(path, columns, rows):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def load_part1_data(summary_path, stats_path):
    """Return source rows and the unchanged eight-column Part 1 stats projection."""
    columns, rows = read_csv(summary_path)
    if columns != SUMMARY_COLUMNS:
        raise ValueError(f"Unexpected summary columns: {columns}")
    stats_columns, stats = read_csv(stats_path)
    if stats_columns not in (PART1_COLUMNS, PART1_COLUMNS + PART2_COLUMNS,
                            PART1_COLUMNS + PART2_COLUMNS + PART3_COLUMNS):
        raise ValueError(f"Unexpected stats columns: {stats_columns}")
    base_stats = [{column: row[column] for column in PART1_COLUMNS} for row in stats]
    projects = [row["Project"] for row in base_stats]
    if len(projects) != 10 or len(set(projects)) != 10:
        raise ValueError("Expected exactly ten distinct assigned projects")
    if set(row["project_wocid"] for row in rows) != set(projects):
        raise ValueError("Summary and stats project identifiers differ")
    pairs = [(row["project_wocid"], row["commit_sha1"]) for row in rows]
    if len(set(pairs)) != len(pairs):
        raise ValueError("Duplicate project/commit pairs in the Part 1 summary")
    for project in projects:
        source_count = sum(row["project_wocid"] == project for row in rows)
        expected = int(next(row["ncommits"] for row in base_stats if row["Project"] == project))
        if source_count != expected:
            raise ValueError(f"Part 1 count mismatch for {project}: {source_count} != {expected}")
    return rows, base_stats


def monthly_counts(rows):
    """Count known author timestamps by UTC month and fill only internal months."""
    series, report = {}, {}
    projects = list(dict.fromkeys(row["project_wocid"] for row in rows))
    for project in projects:
        project_rows = [row for row in rows if row["project_wocid"] == project]
        timestamps, missing = [], []
        for row in project_rows:
            value = row["time"].strip()
            if value == "":
                missing.append(row["commit_sha1"])
                continue
            if not re.fullmatch(r"-?\d+", value):
                raise ValueError(f"Invalid author timestamp for {row['commit_sha1']}: {value!r}")
            timestamps.append(int(value))
        if not timestamps:
            raise ValueError(f"No known timestamps to establish a monthly range for {project}")
        dates = pd.to_datetime(timestamps, unit="s", utc=True, errors="raise")
        month_keys = pd.Series(dates.strftime("%Y-%m"))
        months = pd.period_range(month_keys.min(), month_keys.max(), freq="M").astype(str)
        counts = month_keys.value_counts().reindex(months, fill_value=0).astype("int64")
        frame = pd.DataFrame({"Month": months, "#Commits": counts.to_numpy()})
        assert int(frame["#Commits"].sum()) == len(timestamps)
        assert int(frame.iloc[0]["#Commits"]) > 0 and int(frame.iloc[-1]["#Commits"]) > 0
        series[project] = frame
        report[project] = {
            "source_rows": len(project_rows), "known_timestamp_commits": len(timestamps),
            "omitted_missing_timestamps": len(missing), "missing_timestamp_sha1s": missing,
            "first_month": str(months[0]), "last_month": str(months[-1]), "months": len(months),
            "first_author_timestamp_utc": dates.min().isoformat(),
            "last_author_timestamp_utc": dates.max().isoformat(),
        }
    return series, report


def find_zero_runs(frame):
    """Return every maximal contiguous run of zero-commit calendar months."""
    months = frame["Month"].tolist()
    counts = frame["#Commits"].tolist()
    if not months or months != pd.period_range(months[0], months[-1], freq="M").astype(str).tolist():
        raise ValueError("Monthly rows must be unique, chronological, and continuous")
    if any(pd.isna(count) or int(count) != count or count < 0 for count in counts):
        raise ValueError("Monthly commit counts must be nonnegative integers")
    runs, start = [], None
    for index, count in enumerate(counts + [1]):  # Sentinel closes a trailing run.
        if count == 0 and start is None:
            start = index
        elif count != 0 and start is not None:
            runs.append({"start": months[start], "end": months[index - 1], "length": index - start})
            start = None
    return runs


def summarize_gaps(frame):
    """Use the longest run of any length; choose the earliest run on a tie."""
    runs = find_zero_runs(frame)
    metrics = {"LongestGapStart": "", "LongestGapEnd": "", "LongestGapLength": 0,
               "NumCommitsAfterLastGap": "", "NumberOfGapsInTimeline": 0}
    if runs:
        longest = min(runs, key=lambda run: (-run["length"], run["start"]))
        metrics.update({
            "LongestGapStart": longest["start"], "LongestGapEnd": longest["end"],
            "LongestGapLength": longest["length"],
            # Despite its assignment name, this column follows LongestGapEnd.
            "NumCommitsAfterLastGap": int(frame.loc[frame["Month"] > longest["end"], "#Commits"].sum()),
            "NumberOfGapsInTimeline": sum(run["length"] >= 3 for run in runs),
        })
    return metrics


def verify_gap_logic():
    """Small independent examples cover run boundaries, ties, and UTC cutoffs."""
    def frame(counts):
        return pd.DataFrame({"Month": pd.period_range("2020-01", periods=len(counts), freq="M").astype(str),
                             "#Commits": counts})

    no_gap = summarize_gaps(frame([2, 1, 4]))
    assert no_gap == {"LongestGapStart": "", "LongestGapEnd": "", "LongestGapLength": 0,
                      "NumCommitsAfterLastGap": "", "NumberOfGapsInTimeline": 0}
    tied = summarize_gaps(frame([5, 0, 0, 0, 2, 0, 0, 0, 7]))
    assert tied == {"LongestGapStart": "2020-02", "LongestGapEnd": "2020-04", "LongestGapLength": 3,
                    "NumCommitsAfterLastGap": 9, "NumberOfGapsInTimeline": 2}
    short = summarize_gaps(frame([1, 0, 3, 0, 0, 4]))
    assert short["LongestGapLength"] == 2 and short["NumberOfGapsInTimeline"] == 0
    assert find_zero_runs(frame([0, 0, 1, 0])) == [
        {"start": "2020-01", "end": "2020-02", "length": 2},
        {"start": "2020-04", "end": "2020-04", "length": 1}]
    assert summarize_gaps(frame([3, 0, 0, 0]))["NumCommitsAfterLastGap"] == 0
    boundary_rows = [
        {"project_wocid": "example", "commit_sha1": "a", "time": "1583020799"},
        {"project_wocid": "example", "commit_sha1": "b", "time": "1583020800"},
        {"project_wocid": "example", "commit_sha1": "c", "time": "1585699200"},
        {"project_wocid": "example", "commit_sha1": "missing", "time": ""},
    ]
    series, report = monthly_counts(boundary_rows)
    assert series["example"].to_dict("records") == [
        {"Month": "2020-02", "#Commits": 1}, {"Month": "2020-03", "#Commits": 1},
        {"Month": "2020-04", "#Commits": 1}]
    assert report["example"]["omitted_missing_timestamps"] == 1
    sparse, _ = monthly_counts([boundary_rows[0], boundary_rows[2]])
    assert sparse["example"].to_dict("records") == [
        {"Month": "2020-02", "#Commits": 1}, {"Month": "2020-03", "#Commits": 0},
        {"Month": "2020-04", "#Commits": 1}]
    # Endpoints remain included, even when the first and last month are the same.
    single, _ = monthly_counts([boundary_rows[0]])
    assert single["example"].to_dict("records") == [{"Month": "2020-02", "#Commits": 1}]
    return True


def save_timeseries_and_plots(series, output_dir, netid="dpate172", omission_report=None):
    """Save the required monthly CSVs and readable Matplotlib PNGs at 320 DPI."""
    output_dir = Path(output_dir)
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".cache" / "matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for project, frame in series.items():
        csv_path = output_dir / f"{netid}_commits_timeseries_{project}.csv"
        png_path = output_dir / f"{netid}_timeseries_{project}.png"
        write_csv(csv_path, MONTHLY_COLUMNS, frame.to_dict("records"))
        restored = pd.read_csv(csv_path, sep=";", dtype={"Month": str, "#Commits": "int64"})
        pd.testing.assert_frame_equal(restored, frame)
        positions = list(range(len(frame)))
        tick_count = min(14, len(frame))
        ticks = [0] if tick_count == 1 else sorted({round(i * (len(frame) - 1) / (tick_count - 1))
                                                   for i in range(tick_count)})
        fig, ax = plt.subplots(figsize=(11.5, 4.8))
        ax.plot(positions, frame["#Commits"], color="#2459a6", linewidth=1.35,
                marker="o", markersize=2.6)
        ax.set(title=project, xlabel="Month (YYYY-MM, UTC)", ylabel="Number of commits")
        ax.set_xticks(ticks, frame.iloc[ticks]["Month"], rotation=45, ha="right")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylim(bottom=0)
        ax.set_xlim((-0.5, 0.5) if len(frame) == 1 else (-0.5, len(frame) - 0.5))
        ax.grid(True, linewidth=0.55, alpha=0.3)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        omitted = (omission_report or {}).get(project, {}).get("omitted_missing_timestamps", 0)
        if omitted:
            fig.text(0.08, 0.015, f"{omitted} undated records omitted; gaps may change if their dates become available.",
                     fontsize=8.5, color="#555555")
        fig.tight_layout(rect=(0, 0.045 if omitted else 0, 1, 1))
        fig.savefig(png_path, dpi=PLOT_DPI)
        plt.close(fig)
        outputs[project] = {"csv": csv_path.name, "png": png_path.name, "plot_dpi": PLOT_DPI,
                            "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
                            "png_sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()}
    return outputs


def append_part2_stats(base_stats, gap_metrics, interpretations, stats_path, snapshot_path):
    """Preserve later analysis only when its Part 1 and Part 2 inputs are unchanged."""
    projects = [row["Project"] for row in base_stats]
    if set(interpretations) != set(projects) or set(gap_metrics) != set(projects):
        raise ValueError("Interpretations and gap metrics must cover exactly the ten projects")
    rows = []
    for original in base_stats:
        project = original["Project"]
        interpretation = interpretations[project]
        pattern = interpretation if isinstance(interpretation, str) else interpretation["ActivityPattern"]
        if pattern not in PATTERNS:
            raise ValueError(f"Invalid reviewed ActivityPattern for {project}: {pattern!r}")
        rows.append({**original, **gap_metrics[project], "ActivityPattern": pattern})
    stats_path, snapshot_path = Path(stats_path), Path(snapshot_path)
    columns, current = read_csv(stats_path)
    output_columns = PART1_COLUMNS + PART2_COLUMNS
    if columns == output_columns + PART3_COLUMNS:
        calculated = [{column: str(row[column]) for column in output_columns} for row in rows]
        saved = [{column: row[column] for column in output_columns} for row in current]
        if calculated != saved:
            raise ValueError("Part 1 or Part 2 values changed; review and regenerate Part 3 "
                             "before replacing its saved analysis")
        rows = [{**row, **{column: saved_row[column] for column in PART3_COLUMNS}}
                for row, saved_row in zip(rows, current)]
        output_columns += PART3_COLUMNS
    elif columns not in (PART1_COLUMNS, output_columns):
        raise ValueError(f"Unexpected stats columns: {columns}")
    if not snapshot_path.exists():
        if columns != PART1_COLUMNS or current != base_stats:
            raise ValueError("An original eight-column stats file is required to create the first snapshot")
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stats_path, snapshot_path)  # Exact original bytes on the first run.
    columns, original = read_csv(snapshot_path)
    if columns != PART1_COLUMNS or original != base_stats:
        raise ValueError("The preserved Part 1 stats snapshot does not match the current baseline")
    write_csv(stats_path, output_columns, rows)
    columns, restored = read_csv(stats_path)
    assert columns == output_columns
    assert [{column: row[column] for column in PART1_COLUMNS} for row in restored] == base_stats
    assert restored == [{column: str(row[column]) for column in output_columns} for row in rows]
    return rows


def analyze_part2(interpretations, root=ROOT, netid="dpate172"):
    """Write all Part 2 outputs and return monthly frames, stats, and validation."""
    root = Path(root)
    summary_path, stats_path = root / f"{netid}_project_summary.csv", root / f"{netid}_project_stats.csv"
    summary_hash = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    rows, base_stats = load_part1_data(summary_path, stats_path)
    series, omissions = monthly_counts(rows)
    metrics = {project: summarize_gaps(frame) for project, frame in series.items()}
    if set(interpretations) != set(series):
        raise ValueError("Supply a reviewed interpretation for every project before exporting")
    for project, item in interpretations.items():
        pattern = item if isinstance(item, str) else item["ActivityPattern"]
        if pattern not in PATTERNS:
            raise ValueError(f"Invalid reviewed ActivityPattern for {project}: {pattern!r}")
    assert verify_gap_logic()
    omitted_total = sum(item["omitted_missing_timestamps"] for item in omissions.values())
    manifest_path = root / "data" / f"{netid}_validation.json"
    if manifest_path.exists():
        part1 = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert part1["summary_sha256"] == summary_hash
        assert part1["project_commit_rows"] == len(rows)
        assert part1["missing_project_commit_rows"] == omitted_total
    snapshot_path = root / "data" / f"{netid}_part1_stats.csv"
    # The snapshot is created before the shared stats file is first modified.
    stats = append_part2_stats(base_stats, metrics, interpretations, stats_path, snapshot_path)
    outputs = save_timeseries_and_plots(series, root, netid, omissions)
    assert hashlib.sha256(summary_path.read_bytes()).hexdigest() == summary_hash
    report = {
        "netid": netid, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_count": len(series), "source_rows": len(rows),
        "known_timestamp_commits": sum(item["known_timestamp_commits"] for item in omissions.values()),
        "omitted_missing_timestamps": omitted_total, "source_summary_sha256": summary_hash,
        "source_summary_unchanged": True, "part1_stats_columns_preserved": True,
        "part1_stats_snapshot": str(snapshot_path.relative_to(root)),
        "part1_stats_snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        "month_timezone": "UTC", "range": "First through last known author-timestamp month, inclusive.",
        "longest_gap_rule": "Longest contiguous zero-month run of any length; earliest start wins ties.",
        "gap_count_rule": "Count maximal zero-month runs lasting at least three months.",
        "after_gap_rule": "Sum known-timestamp commits strictly after LongestGapEnd, not after the latest gap.",
        "no_gap_convention": "Blank start/end, length 0, number of gaps 0, blank commits after gap (not applicable).",
        "missing_timestamp_effect": "Undated identifiers cannot be assigned to months. Their unknown dates could alter "
                                    "the observed range, zero-month runs, gap lengths, gap counts, and commits after a gap.",
        "partial_month_caveat": "The first and last observed months may be incomplete calendar months.",
        "gap_and_utc_boundary_checks_passed": True, "csv_roundtrip_passed": True,
        "projects": {project: {**omissions[project], **metrics[project],
                               "zero_runs": find_zero_runs(series[project]), **outputs[project]}
                     for project in series},
    }
    validation_path = root / "data" / f"{netid}_part2_validation.json"
    validation_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return series, stats, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interpretations", type=Path, required=True, help="Reviewed project-to-ActivityPattern JSON map")
    parser.add_argument("--netid", default="dpate172")
    args = parser.parse_args()
    interpretations = json.loads(args.interpretations.read_text(encoding="utf-8"))
    _, _, report = analyze_part2(interpretations, netid=args.netid)
    print(json.dumps({key: report[key] for key in ["project_count", "source_rows", "known_timestamp_commits",
                                                "omitted_missing_timestamps", "gap_and_utc_boundary_checks_passed"]}, indent=2))


if __name__ == "__main__":
    main()

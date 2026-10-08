"""Build the Part 2 notebook from the checked monthly data and interpretations."""

import ast
import csv
import hashlib
import json
from pathlib import Path
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NETID = "dpate172"


def source_groups(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    group_names = {"monthly_counts", "verify_gap_logic", "save_timeseries_and_plots", "append_part2_stats"}
    boundaries = [0]
    boundaries.extend(node.lineno - 1 for node in tree.body
                      if isinstance(node, ast.FunctionDef) and node.name in group_names)
    boundaries.append(next(node.lineno - 1 for node in tree.body
                           if isinstance(node, ast.FunctionDef) and node.name == "main"))
    return ["".join(lines[start:end]).strip() for start, end in zip(boundaries, boundaries[1:])]


def build():
    report = json.loads((ROOT / "data" / f"{NETID}_part2_validation.json").read_text())
    interpretation_path = ROOT / "data" / f"{NETID}_interpretations.json"
    interpretations = json.loads(interpretation_path.read_text(encoding="utf-8"))
    with (ROOT / f"{NETID}_project_stats.csv").open(newline="", encoding="utf-8") as handle:
        stats = list(csv.DictReader(handle, delimiter=";"))
    assert len(stats) == report["project_count"] == 10
    assert set(interpretations) == {row["Project"] for row in stats} == set(report["projects"])
    assert hashlib.sha256((ROOT / f"{NETID}_project_summary.csv").read_bytes()).hexdigest() == report["source_summary_sha256"]
    for row in stats:
        project = row["Project"]
        assert row["ActivityPattern"] == interpretations[project]["ActivityPattern"]
        assert interpretations[project]["Interpretation"].strip()
        evidence = report["projects"][project]
        for field in ["LongestGapStart", "LongestGapEnd", "LongestGapLength", "NumCommitsAfterLastGap", "NumberOfGapsInTimeline"]:
            assert row[field] == str(evidence[field])
        for kind in ["csv", "png"]:
            assert hashlib.sha256((ROOT / evidence[kind]).read_bytes()).hexdigest() == evidence[kind + "_sha256"]

    cells = []

    def markdown(source, identifier):
        cells.append(nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip(), id=identifier))

    def code(source, identifier):
        cells.append(nbformat.v4.new_code_cell(textwrap.dedent(source).strip(), id=identifier))

    markdown(f"""
    # Mini Project 2 — Part 2

    **NetID: {NETID}**

    This notebook groups the Part 1 commits by month, plots activity, and measures
    gaps. It creates ten monthly CSVs, ten PNG plots, and the Part 2 columns in
    `dpate172_project_stats.csv`.

    Months use UTC and run from each project's first to last dated commit, including
    zero-commit months in between. The **{report['omitted_missing_timestamps']} undated records**
    (12 in `microsoft_fhir-server`, one in `agnwinds_python`) cannot be assigned to a month.
    Their missing dates could change those projects' counts, ranges, or gaps.
    """, "title-and-data")
    markdown("""
    ## Gap definitions

    The longest gap is the longest consecutive run of zero-commit months, even if
    it lasts only one or two months. `NumberOfGapsInTimeline` counts runs of at least
    three months. Ties for the longest gap use the earliest run.

    `NumCommitsAfterLastGap` follows the assignment's definition: commits after
    **LongestGapEnd**, through the last dated commit in this dataset. With no gap,
    its dates and post-gap count are blank, and its length and gap count are zero.
    First and last months may be partial; the timelines are not extended to today.
    """, "gap-definitions")
    markdown("""
    ## Monthly aggregation and plotting

    Run from the repository folder with `requirements.txt` installed. The code below
    uses the saved Part 1 data and makes no API requests. CSV columns are
    `Month;#Commits`, with months written as `YYYY-MM`. Plots are saved at 320 DPI.
    """, "code-introduction")
    code("""
    from pathlib import Path
    from IPython.display import Image, display
    assert Path("dpate172_project_summary.csv").exists(), "Run from the repository folder."
    """, "setup")
    for index, source in enumerate(source_groups(ROOT / "scripts" / "analyze_part2.py"), 1):
        code(source, f"analysis-functions-{index}")
    interpretation_hash = hashlib.sha256(interpretation_path.read_bytes()).hexdigest()
    expected_metrics = {row["Project"]: {field: row[field] for field in
                        ["LongestGapStart", "LongestGapEnd", "LongestGapLength", "NumCommitsAfterLastGap",
                         "ActivityPattern", "NumberOfGapsInTimeline"]} for row in stats}
    code(f"""
    interpretation_path = Path("data/dpate172_interpretations.json")
    assert hashlib.sha256(interpretation_path.read_bytes()).hexdigest() == "{interpretation_hash}", "Rebuild the notebook after editing interpretations."
    assert hashlib.sha256(Path("dpate172_project_summary.csv").read_bytes()).hexdigest() == "{report['source_summary_sha256']}", "Rebuild the analysis after changing Part 1 data."
    interpretations = json.loads(interpretation_path.read_text(encoding="utf-8"))
    series, stats, validation = analyze_part2(interpretations)
    expected_metrics = {expected_metrics!r}
    for row in stats:
        assert {{key: str(row[key]) for key in PART2_COLUMNS}} == expected_metrics[row["Project"]]
    print(f"Created {{len(series)}} monthly CSVs and {{len(series)}} plots.")
    print(f"Monthly total: {{validation['known_timestamp_commits']:,}} dated commits; {{validation['omitted_missing_timestamps']}} undated rows excluded.")
    print("Gap checks passed. Original Part 1 data and statistics are preserved.")
    """, "run-analysis")

    table = ["## Gap summary", "", "| Project | Longest gap | Months | Commits after gap | Gaps ≥3 months | Pattern |",
             "| --- | --- | ---: | ---: | ---: | --- |"]
    for row in stats:
        project = row["Project"]
        marker = " †" if report["projects"][project]["omitted_missing_timestamps"] else ""
        gap = f"{row['LongestGapStart']} to {row['LongestGapEnd']}" if row["LongestGapStart"] else "None"
        after = row["NumCommitsAfterLastGap"] or "—"
        table.append(f"| {project}{marker} | {gap} | {row['LongestGapLength']} | {after} | {row['NumberOfGapsInTimeline']} | {row['ActivityPattern']} |")
    table.extend(["", "† Results use dated records only. Missing timestamps may change these values."])
    markdown("\n".join(table), "gap-summary")
    markdown("""
    ## Interpretation

    The activity labels describe the overall patterns in the plots. Annual comparisons
    below use full years unless a partial year is stated. The plots show activity
    levels; they do not establish the reasons for a change.
    """, "interpretation")
    for index, row in enumerate(stats, 1):
        project = row["Project"]
        item = interpretations[project]
        markdown(f"### {project}\n\n**Pattern: {item['ActivityPattern']}**\n\n{item['Interpretation']}", f"interpretation-{index}")
        code(f'display(Image(filename="{NETID}_timeseries_{project}.png", width=900))', f"plot-{index}")
    markdown("""
    ## Saved files

    - `dpate172_commits_timeseries_<WOCProjectID>.csv`: one monthly table per project.
    - `dpate172_timeseries_<WOCProjectID>.png`: one 320-DPI plot per project.
    - [dpate172_project_stats.csv](dpate172_project_stats.csv): Part 1 values plus the six Part 2 columns.

    Running this notebook regenerates the Part 2 files. Existing Part 3 columns are
    preserved only when the first fourteen statistics columns are unchanged.
    Otherwise, it stops so outdated Part 3 explanations are not kept.
    If Part 1 is collected again, review and rerun the later parts. A changed Part 1
    baseline also needs a reviewed replacement for `data/dpate172_part1_stats.csv`,
    which keeps the original statistics.
    """, "saved-files")
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "file_extension": ".py", "mimetype": "text/x-python",
                          "pygments_lexer": "ipython3"},
    })
    nbformat.validate(notebook)
    destination = ROOT / f"{NETID}_vis.ipynb"
    nbformat.write(notebook, destination)
    print(f"Built {destination.name}: {len(cells)} cells")


if __name__ == "__main__":
    build()

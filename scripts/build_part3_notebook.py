"""Build the concise Part 3 notebook; run it to reproduce the saved deliverables."""

from pathlib import Path
import textwrap
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def build():
    cells = []
    def md(source):
        cells.append(nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip()))
    def code(source):
        cells.append(nbformat.v4.new_code_cell(textwrap.dedent(source).strip()))

    md("""
    # Mini Project 2 — Part 3

    **NetID: dpate172**

    This notebook selects commits around each project's longest gap, summarizes
    their themes, and adds the explanations, status, and reflections required in
    Parts 3.1 and 3.2. All inputs are saved in the repository, so rerunning it does
    not need API access.
    """)
    md("""
    ## Selections and interpretation

    - Gap samples use the last ten commits before the gap and first ten after it,
      ordered by the Part 1 author timestamp in UTC, then SHA for ties.
    - NodePy and Geoportal each have only two post-gap records. FHIR Server and
      cuCIM have no empty months, so their gap answers are N/A and they have no
      rows in the gap CSV. All ten projects have statistics and reflections.
    - Each message has one reviewed primary theme, saved with a short reason.
      The top two are ranked by count; ties follow the README's category order.
      If only one theme is supported, that single theme is retained. Identifiable
      merges inherit their described change; generic merges are Other. Bot-authored
      updates use Automated bot contributions.
    - Explanations distinguish observed changes from possible causes. Returning
      authors are checked against all dated pre-gap records, using raw identities.

    **Status date:** the README explicitly uses **September 30, 2025**, with
    April 1, 2025 as the activity threshold. Recent themes use the latest ten
    commits from the reconstructed default-branch history through that cutoff,
    ordered by committer time. This differs from the later Part 1 GitHub snapshot
    and from the author dates used for gaps. A present-day Git history cannot
    reconstruct every past force-push or exactly when a commit became public.
    """)
    code("""
    from pathlib import Path
    import json
    import pandas as pd
    from IPython.display import Markdown, display
    from scripts.analyze_part3 import analyze_part3, read_csv, select_gap_commits

    assert Path("dpate172_project_summary.csv").exists(), "Run from the repository folder."
    pd.set_option("display.max_colwidth", None)
    stats, gap_rows, recent_rows, report = analyze_part3()
    stats_df = pd.DataFrame(stats)
    print(f"{report['project_count']} projects; {len(gap_rows)} gap-sample commits; {len(recent_rows)} recent commits.")
    print("Created the gap CSV, updated statistics, and ten reflection files.")
    """)
    md("""
    ## Gap samples

    The exported CSV keeps the original five fields and adds `pre/post` first.
    The 13 records without timestamps remain in Part 1, but cannot enter a
    time-based sample. Their missing dates are documented in the affected projects.
    """)
    code("""
    counts = pd.DataFrame([
        {"Project": project, "Before": item["pre_count"], "After": item["post_count"],
         "Recent": item["recent_count"], "Undated source rows": item["omitted_undated"]}
        for project, item in report["projects"].items()
    ])
    display(counts.set_index("Project"))
    display(stats_df.set_index("Project")[["BeforeThemes", "AfterThemes"]])
    """)
    md("""
    ## What happened around the gaps

    The linked reflections give the evidence behind each interpretation. A return
    to committing can be brief or limited to documentation; it does not necessarily
    show that full development resumed.
    """)
    code("""
    for row in stats:
        project = row["Project"]
        display(Markdown(f"**[{project}](dpate172_reflection_{project}.md)** — {row['Notes']}"))
    """)
    md("""
    ## Status and recent themes

    Active means at least one eligible default-branch commit during April–September
    2025. Inactive means the most recent eligible commit predates that interval.
    This is a date rule, so a retired project can still be Active after a README edit.
    Full recent messages, dates, theme labels, and reasons are saved in
    `data/dpate172_recent_commits.csv`.
    """)
    code("""
    status = stats_df[["Project", "Currentstatus", "RecentThemes"]].copy()
    status["Last commit as of cutoff (UTC)"] = status["Project"].map(
        lambda project: report["projects"][project]["latest_github_commit_as_of_cutoff"])
    display(status.set_index("Project"))
    """)
    md("""
    ## Checks

    Confirm that the gap CSV preserves the selected source records, all ten projects
    have reflections, and the first fourteen statistics columns are unchanged.
    The independent validator also checks boundary cases and selection order.
    """)
    code("""
    from scripts.validate_part3 import validate_part3
    validate_part3(Path.cwd())
    print("Part 3 checks passed.")
    """)
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.13.7"}}
    nbformat.write(nb, ROOT / "dpate172_part3.ipynb")


if __name__ == "__main__":
    build()

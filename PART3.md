# Part 3 — dpate172

Run `dpate172_part3.ipynb` from the repository folder, or use:

```sh
python scripts/analyze_part3.py
python scripts/validate_part3.py
```

The notebook uses the saved data and makes no network requests. Install the
dependencies in `requirements.txt` first.

The results are in `dpate172_project_gap_commits.csv`, the nine added columns in
`dpate172_project_stats.csv`, and ten `dpate172_reflection_*.md` files. This covers
both Part 3.1 and Part 3.2; the README's final checklist labels the latter fields
and reflections as Part 4.

The gap CSV prepends `pre/post` to the unchanged Part 1 columns and uses the same
semicolon delimiter. It selects the last ten dated commits before each longest
gap and the first ten afterward. UTC author dates determine the order; SHA breaks
ties. The longest gaps and their earliest-start tie rule come from Part 2.

Two exceptions matter. FHIR Server and cuCIM have no zero-commit months, so no
before/after rows exist for them; their statistics and reflections mark the gap
questions N/A. NodePy and Geoportal each have only two commits after their longest
gap, and both are included. The gap CSV therefore has 144 rows covering eight
projects. The recent sample covers all ten projects separately.

Themes were reviewed from the full messages and supporting changes when needed.
Each commit has one primary category and a reason in the saved research data.
Counts determine the top two categories, with ties following the category order
in the assignment. A sample with only one supported theme keeps that one label.
Identifiable merges use the subject of the merged change; generic merges are
Other. Bot-authored updates are Automated bot contributions. These are qualitative
judgments, not an automatic keyword classifier.

`Currentstatus` follows the README's explicit historical date, **2025-09-30**.
Active means an eligible default-branch commit on or after **2025-04-01**.
`RecentThemes` uses the ten most recent eligible commits by committer time.
The later Part 1 `lastGHCommitDate` snapshot is preserved, so it is not the input
to this historical status calculation. GitHub's current branch history is used
to reconstruct a historical mainline anchor; past force-pushes and actual public
arrival dates cannot be fully recovered from commit timestamps alone.

`data/dpate172_part3_interpretations.json` stores the reviewed gap themes,
explanations, and links. `data/dpate172_part3_github.json` records the historical GitHub selection
and collection method. `data/dpate172_recent_commits.csv` contains the recent
messages and their theme reasons. `data/dpate172_part3_validation.json` records
sample counts, author comparisons, and checksums. The original fourteen statistics
columns are preserved in `data/dpate172_part2_stats.csv` for comparison.
Relevant inspected source excerpts are saved in `data/dpate172_part3_sources.json`.

There are 13 undated source records: twelve for FHIR Server and one for agnwinds.
They cannot enter chronological selections. WoC includes commits outside the
GitHub default branch, so gap samples and recent GitHub samples need not match.
Author identity comparisons use raw names and emails; aliases can make one
person look like several contributors. Explanations say when a cause remains
uncertain, and distinguish occasional maintenance from sustained recovery.

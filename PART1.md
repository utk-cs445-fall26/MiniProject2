# Part 1 — dpate172

Part 1 produces three main files:

- `dpate172.ipynb`: visible retrieval code, per-project Markdown results, and executed validation.
- `dpate172_project_summary.csv`: semicolon-separated candidate-identifier rows and available commit metadata, with the exact header `project_wocid;commit_sha1;author;time;commit message`.
- `dpate172_project_stats.csv`: the assignment's Part 1 summary columns, `Project;ncommits;nauthors;from;to;nstars;nforks;lastGHCommitDate`.

Supporting files in `data/` preserve the WoC project membership lists, object caches, GitHub API metadata, validation report, and documented Git recovery exceptions. Run commands from the repository root.

**Source metadata is not fully available.** Some WoC-listed identifiers could not be recovered from the investigated sources. Their actual object types, authors, timestamps, and messages remain unknown. Their CSV rows preserve the identifiers and leave the three metadata fields empty. The final notebook reports the exact unavailable-object counts and evidence from `data/dpate172_unavailable_commits.json` and `data/dpate172_missing_object_research.json`.

For affected projects, `ncommits` means WoC-listed **candidate commits after verified tag exclusions**, including unresolved identifiers. The actual commit count lies between the available known-commit count and candidate count. `nauthors` is the observed distinct-author count, a lower bound; `from` and `to` are observed timestamp bounds and may not be the full project's earliest/latest dates. These statistics are labeled incomplete in the notebook.

## Environment and offline verification

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
CFLAGS='-DCYTHON_USE_SYS_MONITORING=0' .venv/bin/python -m pip install -r requirements.txt
```

The `CFLAGS` setting addresses the legacy C-extension compiler error encountered when installing `python-woc` dependencies on Python 3.13. It is an installation setting, not a change to the collected data.

Open `dpate172.ipynb` with this environment and run all cells. Leave `REFRESH_FROM_API = False` for offline verification of the packaged results. Text is read literally, including blank messages and values such as `NA`; available `time` values are integer author Unix seconds, and unavailable timestamps are empty. Notebook tables convert observed timestamps to UTC.

Part 2 adds columns to the shared project statistics CSV. Part 1 checks the values and checksum of its original eight columns, so those additions do not break verification. Running Part 1 collection again replaces the shared statistics with its eight-column export; rerun `dpate172_vis.ipynb` afterward to rebuild Part 2. The original Part 1 statistics are also kept in `data/dpate172_part1_stats.csv`.

The notebook verifies all ten assignments, exact equality with saved WoC lists after documented exclusions of verified non-commit tags, zero duplicate/missing/extra candidate-identifier pairs, available metadata against its source cache, and blank metadata only for explicitly documented unavailable objects. It recomputes per-project candidate/available/unavailable counts, observed author/time statistics, and the summary CSV SHA-256. If `data/dpate172_git_objects.zip` is present, it also recomputes Git SHA-1 and raw SHA-256 for recovered commit objects and each tag in an exclusion's chain, checks exact object/type target headers, and verifies that the chain ends at the documented commit. These checks run without network access.

## Collecting or resuming data

```sh
.venv/bin/python scripts/collect_github_metadata.py
.venv/bin/python scripts/retrieve_part1.py
```

The retrieval script uses the official WoC Python client, batches of 10, sequential requests, pauses, retries, and checkpoints. The GitHub collector reuses completed metadata unless `--refresh` is supplied. `GITHUB_TOKEN` and `WOC_API_KEY` are optional environment variables; neither is stored in the submission.

If WoC lists a candidate but both of its content endpoints cannot supply the object, the retrieval script records the failure and refuses to export incomplete metadata by default. Recover these exceptions and resume:

```sh
.venv/bin/python scripts/recover_missing_commits.py --recover data/dpate172_woc_missing.json
.venv/bin/python scripts/retrieve_part1.py
```

WoC `p2c` defines every project's membership. Git recovery supplies only missing object contents from original Git repositories after recomputing each Git object SHA-1. The manifest records sources, WoC errors, and verification; the notebook reports recovery counts separately. The final data must not be described as having every object supplied directly by WoC.

The WoC mapping also contains some annotated Git tag IDs incorrectly listed as commits. These are excluded only when their raw Git object SHA-1 and `tag` type have been verified and their final target commits already appear separately in the same project's `p2c` list. Tags can point to other tags; the manifest preserves the complete verified chain to the final commit. Auxiliary chain tags absent from WoC's mapping are supporting evidence and do not increase exclusion counts. The manifest and notebook disclose raw ID counts, candidate and available commit counts, and per-project tag exclusions. Unresolved WoC-listed identifiers are never silently omitted.

To run collection within the notebook, set `REFRESH_FROM_API = True`; it invokes the GitHub collector and `await collect(allow_missing=ALLOW_MISSING_METADATA)`. `ALLOW_MISSING_METADATA = False` keeps strict export behavior. Setting it to `True` explicitly permits identifier-only rows for investigated exceptions marked `retain_identifier_only: true` in the research manifest. It does not permit exporting an unfinished download as if it were complete. No author, timestamp, or message is invented for these rows.

The equivalent explicit command-line export is `.venv/bin/python scripts/retrieve_part1.py --allow-missing`. This still requires every unavailable identifier to have its researched exception recorded and does not turn incomplete source metadata into complete metadata.

Existing WoC checkpoints are reused. Back up existing data before deliberately removing checkpoints for a new snapshot. GitHub default-branch counts and contributor counts have different branch, date, and identity scopes from the WoC dataset. The notebook documents this and does not assume the assignment's historical January 2025 cutoff for a later live API response.

## Build the notebook after retrieval finishes

```sh
.venv/bin/python scripts/package_git_evidence.py
.venv/bin/python scripts/build_notebook.py
```

The packaging command uses raw Git objects in the local, ignored `.cache/` directory. A fresh clone uses the already packaged `data/dpate172_git_objects.zip` for offline verification; it does not need to rerun the packaging command. The notebook builder can run directly against the packaged CSVs, caches, and manifests.

The builder refuses to create the notebook until the final CSVs, source caches, unavailable-object manifest, investigation, and validation report agree for all ten projects. Identifier coverage can be complete while source metadata remains incomplete; the notebook distinguishes both states. It embeds the current retrieval code and generates Markdown result tables from the final statistics and GitHub metadata. Execute the resulting notebook and save its outputs before uploading these three deliverables and supporting data to the GitHub fork. Part 2 plots and trend analysis are outside this submission.

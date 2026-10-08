#!/usr/bin/env python3
"""Build the Part 1 notebook after exports and disclosed limitations pass validation.

Run from the repository: .venv/bin/python scripts/build_notebook.py
This command does not retrieve data or execute the resulting notebook.
"""

import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import textwrap

import nbformat


NETID = "dpate172"
SUMMARY_COLUMNS = ["project_wocid", "commit_sha1", "author", "time", "commit message"]
STATS_COLUMNS = ["Project", "ncommits", "nauthors", "from", "to", "nstars", "nforks", "lastGHCommitDate"]
ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path, columns, *, allow_extra_columns=False):
    # csv.DictReader preserves empty strings and literal NA/NaN commit messages.
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        actual_columns = reader.fieldnames or []
        if allow_extra_columns:
            assert actual_columns[:len(columns)] == columns, f"Unexpected header: {path}"
            assert len(actual_columns) == len(set(actual_columns)), f"Duplicate columns: {path}"
        else:
            assert actual_columns == columns, f"Unexpected header: {path}"
        return list(reader)


def part1_stats_sha256(rows):
    """Hash the original Part 1 columns while allowing later parts to add columns."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=STATS_COLUMNS, delimiter=";",
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return hashlib.sha256(output.getvalue().encode("utf-8")).hexdigest()


def cache_records(path):
    if not path.exists():
        return {}
    records = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            sha = record["commit_sha1"]
            if sha in records:
                assert records[sha] == record, f"Conflicting cache object: {sha}"
            records[sha] = record
    return records


def unavailable_records(path):
    if not path.exists():
        return {}
    document = read_json(path)
    return document.get("unavailable", document)


def utc_date(timestamp):
    return datetime.fromtimestamp(int(timestamp), timezone.utc).isoformat().replace("+00:00", "Z")


def markdown_table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", "<br>")
    return "\n".join([
        "| " + " | ".join(map(cell, headers)) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(map(cell, row)) + " |" for row in rows],
    ])


def load_and_check(root):
    data = root / "data"
    summary = root / f"{NETID}_project_summary.csv"
    stats_path = root / f"{NETID}_project_stats.csv"
    required_paths = [summary, stats_path, data / f"{NETID}_validation.json",
                      data / f"{NETID}_woc_project_commits.json",
                      data / f"{NETID}_github_metadata.json", data / f"{NETID}_woc_commits.jsonl"]
    missing_files = [str(path.relative_to(root)) for path in required_paths if not path.exists()]
    if missing_files:
        raise RuntimeError("Export and validate retrieval before building the notebook. Missing files: "
                           + ", ".join(missing_files))
    with (root / "net2prj.csv").open(newline="", encoding="utf-8-sig") as handle:
        projects = [row["WoC"] for row in csv.DictReader(handle) if row["netID"] == NETID]
    assert len(projects) == len(set(projects)) == 10
    membership_document = read_json(data / f"{NETID}_woc_project_commits.json")
    membership = membership_document["projects"]
    assert set(membership) == set(projects)
    assert all(len(values) == len(set(values)) for values in membership.values())
    raw_pairs = {(project, sha) for project, values in membership.items() for sha in values}
    recovery_path = data / f"{NETID}_git_recovery.json"
    recovery = read_json(recovery_path) if recovery_path.exists() else {"recovered": {}}
    exclusions = recovery.get("excluded_noncommit_objects", {})
    excluded_pairs = set()
    for sha, evidence in exclusions.items():
        assert evidence["object_type"] == "tag" and evidence["git_object_sha1_verified"] is True
        affected = {project for project, value in raw_pairs if value == sha}
        assert affected == set(evidence["woc_projects"])
        for project in affected:
            assert evidence["target_commit_sha1"] in membership[project]
            assert evidence["target_commit_sha1"] not in exclusions
            excluded_pairs.add((project, sha))
    expected_pairs = raw_pairs - excluded_pairs
    required_hashes = {sha for _, sha in expected_pairs}
    rows = read_csv(summary, SUMMARY_COLUMNS)
    pairs = {(row["project_wocid"], row["commit_sha1"]) for row in rows}
    assert len(rows) == len(pairs) == len(expected_pairs)
    assert pairs == expected_pairs, "CSV must equal p2c membership minus verified non-commit tags"
    woc = cache_records(data / f"{NETID}_woc_commits.jsonl")
    recovered = cache_records(data / f"{NETID}_git_recovered_commits.jsonl")
    for sha in set(woc) & set(recovered):
        assert woc[sha] == recovered[sha], f"Conflicting WoC/Git object: {sha}"
    records = {**recovered, **woc}  # Prefer WoC records when both sources agree.
    missing_hashes = required_hashes - set(records)
    unavailable = unavailable_records(data / f"{NETID}_unavailable_commits.json")
    assert set(unavailable) == missing_hashes, "Unavailable manifest must exactly explain missing metadata"
    research_path = data / f"{NETID}_missing_object_research.json"
    research = read_json(research_path) if research_path.exists() else {}
    for sha, evidence in unavailable.items():
        assert set(evidence["woc_projects"]) == {project for project, value in expected_pairs if value == sha}
        assert research[sha]["retain_identifier_only"] is True
    used_recovery = (required_hashes & set(recovered)) - set(woc)
    assert used_recovery <= set(recovery["recovered"])
    for sha in used_recovery:
        assert recovery["recovered"][sha]["git_object_sha1_verified"] is True
    for row in rows:
        assert re.fullmatch(r"[0-9a-f]{40}", row["commit_sha1"])
        if row["commit_sha1"] in missing_hashes:
            assert all(row[field] == "" for field in ["author", "time", "commit message"])
            continue
        record = records[row["commit_sha1"]]
        assert int(row["time"]) == record["time"]
        assert row["author"] == record["author"]
        assert row["commit message"] == record["commit message"]
    stats_rows = read_csv(stats_path, STATS_COLUMNS, allow_extra_columns=True)
    assert len(stats_rows) == 10
    stats = {row["Project"]: row for row in stats_rows}
    assert set(stats) == set(projects)
    gh_document = read_json(data / f"{NETID}_github_metadata.json")
    github = {row["project_wocid"]: row for row in gh_document["projects"]}
    assert set(github) == set(projects)
    grouped = {project: [row for row in rows if row["project_wocid"] == project] for project in projects}
    for project, commits in grouped.items():
        row, gh = stats[project], github[project]
        observed = [commit for commit in commits if commit["commit_sha1"] not in missing_hashes]
        assert int(row["ncommits"]) == len(commits)
        assert int(row["nauthors"]) == len({commit["author"] for commit in observed})
        assert row["from"] == (utc_date(min(int(commit["time"]) for commit in observed)) if observed else "")
        assert row["to"] == (utc_date(max(int(commit["time"]) for commit in observed)) if observed else "")
        assert int(row["nstars"]) == gh["stars"] and int(row["nforks"]) == gh["forks"]
        assert row["lastGHCommitDate"] == gh["last_commit_date"]
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    report = read_json(data / f"{NETID}_validation.json")
    assert report["summary_sha256"] == digest
    assert report["project_count"] == 10 and report["missing_commits"] == len(missing_hashes)
    assert report["missing_project_commit_rows"] == sum(sha in missing_hashes for _, sha in expected_pairs)
    assert report["metadata_complete"] is (not missing_hashes)
    assert report["available_commit_objects"] == len(required_hashes & set(records))
    assert report["raw_p2c_project_object_rows"] == len(raw_pairs)
    assert report["excluded_noncommit_objects"] == len(exclusions)
    assert report["excluded_noncommit_rows"] == len(excluded_pairs)
    assert report["project_commit_rows"] == len(rows)
    assert report["duplicate_project_commit_pairs"] == 0
    assert report["unique_candidate_objects"] == len(required_hashes)
    assert report["unique_commit_objects"] == len(required_hashes & set(records))
    assert report["woc_commit_objects"] == len(required_hashes & set(woc))
    assert report["git_recovered_commit_objects"] == len(used_recovery)
    assert report["woc_commit_objects"] + report["git_recovered_commit_objects"] == report["available_commit_objects"]
    assert report["counts"] == {project: len(commits) for project, commits in grouped.items()}
    return {"projects": projects, "membership": membership, "membership_document": membership_document,
            "stats": stats, "github": github, "gh_document": gh_document, "report": report,
            "recovery": recovery, "used_recovery": used_recovery, "digest": digest,
            "summary_rows": len(rows), "unique_hashes": len(required_hashes),
            "raw_pairs": raw_pairs, "excluded_pairs": excluded_pairs, "exclusions": exclusions,
            "missing_hashes": missing_hashes, "unavailable": unavailable, "research": research,
            "stats_digest": part1_stats_sha256(stats_rows),
            "github_digest": hashlib.sha256((data / f"{NETID}_github_metadata.json").read_bytes()).hexdigest()}


def source_groups(path):
    """Preserve the full retrieval script, except its command-line entry point."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    stop = next(node.lineno - 1 for node in tree.body if isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare))
    boundaries = [0]
    group_starts = {"get_project_commits", "retrieve_commits", "export_summary", "collect"}
    boundaries.extend(node.lineno - 1 for node in tree.body
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in group_starts)
    boundaries.append(stop)
    groups = ["".join(lines[start:end]).rstrip() for start, end in zip(boundaries, boundaries[1:])]
    assert all(groups)
    return groups


VALIDATION_CODE = r'''
# Preserve all text literally, including blanks and values such as "NA".
with Path(f"{NETID}_project_summary.csv").open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle, delimiter=";")
    assert reader.fieldnames == SUMMARY_COLUMNS
    rows = list(reader)
with Path(f"{NETID}_project_stats.csv").open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle, delimiter=";")
    assert (reader.fieldnames or [])[:len(STATS_COLUMNS)] == STATS_COLUMNS
    assert len(reader.fieldnames) == len(set(reader.fieldnames))
    stats_rows = list(reader)

projects = assigned_projects()
project_ids = {project["project_wocid"] for project in projects}
membership_file = DATA / f"{NETID}_woc_project_commits.json"
memberships = json.loads(membership_file.read_text(encoding="utf-8"))["projects"]
assert len(project_ids) == 10 and set(memberships) == project_ids
assert all(len(values) == len(set(values)) for values in memberships.values())
raw_pairs = {(project, sha) for project, values in memberships.items() for sha in values}
recovery_file = DATA / f"{NETID}_git_recovery.json"
recovery = json.loads(recovery_file.read_text(encoding="utf-8")) if recovery_file.exists() else {"recovered": {}}
exclusions = recovery.get("excluded_noncommit_objects", {})
excluded_pairs = set()
for sha, evidence in exclusions.items():
    assert evidence["object_type"] == "tag" and evidence["git_object_sha1_verified"] is True
    affected = {project for project, value in raw_pairs if value == sha}
    assert affected == set(evidence["woc_projects"])
    for project in affected:
        assert evidence["target_commit_sha1"] in memberships[project]
        assert evidence["target_commit_sha1"] not in exclusions
        excluded_pairs.add((project, sha))
expected_pairs = raw_pairs - excluded_pairs
actual_pairs = {(row["project_wocid"], row["commit_sha1"]) for row in rows}
missing_pairs = expected_pairs - actual_pairs
extra_pairs = actual_pairs - expected_pairs
duplicate_pairs = len(rows) - len(actual_pairs)
assert not missing_pairs and not extra_pairs and duplicate_pairs == 0
assert {row["project_wocid"] for row in rows} == project_ids
required_hashes = {sha for _, sha in expected_pairs}

def read_cache_without_mutation(path):
    records = {}
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                item = json.loads(line)
                sha = item["commit_sha1"]
                if sha in records:
                    assert records[sha] == item
                records[sha] = item
    return records

woc_records = read_cache_without_mutation(DATA / f"{NETID}_woc_commits.jsonl")
git_records = read_cache_without_mutation(DATA / f"{NETID}_git_recovered_commits.jsonl")
for sha in set(woc_records) & set(git_records):
    assert woc_records[sha] == git_records[sha]
records = {**git_records, **woc_records}
missing_hashes = required_hashes - set(records)
unavailable_file = DATA / f"{NETID}_unavailable_commits.json"
unavailable_document = json.loads(unavailable_file.read_text(encoding="utf-8")) if unavailable_file.exists() else {}
unavailable = unavailable_document.get("unavailable", unavailable_document)
assert set(unavailable) == missing_hashes, "Every unavailable SHA must be explicitly documented"
research_file = DATA / f"{NETID}_missing_object_research.json"
research = json.loads(research_file.read_text(encoding="utf-8")) if research_file.exists() else {}
for sha, evidence in unavailable.items():
    assert set(evidence["woc_projects"]) == {project for project, value in expected_pairs if value == sha}
    assert research[sha]["retain_identifier_only"] is True
recovered_hashes = (required_hashes & set(git_records)) - set(woc_records)
for row in rows:
    sha = row["commit_sha1"]
    assert re.fullmatch(r"[0-9a-f]{40}", sha)
    if sha in missing_hashes:
        assert all(row[field] == "" for field in ["author", "time", "commit message"])
        continue
    assert re.fullmatch(r"-?[0-9]+", row["time"]), "time must be integer Unix seconds"
    original = records[sha]
    assert int(row["time"]) == original["time"]
    assert row["author"] == original["author"]
    assert row["commit message"] == original["commit message"]

stats_by_project = {row["Project"]: row for row in stats_rows}
github_document = json.loads((DATA / f"{NETID}_github_metadata.json").read_text(encoding="utf-8"))
github = {row["project_wocid"]: row for row in github_document["projects"]}
assert len(stats_rows) == 10 and set(stats_by_project) == project_ids == set(github)
counts = {}
source_counts_by_project = {}
for project in sorted(project_ids):
    commits = [row for row in rows if row["project_wocid"] == project]
    observed = [row for row in commits if row["commit_sha1"] not in missing_hashes]
    actual_hashes = {row["commit_sha1"] for row in commits}
    excluded_in_project = {sha for key, sha in excluded_pairs if key == project}
    assert actual_hashes == set(memberships[project]) - excluded_in_project
    expected = stats_by_project[project]
    counts[project] = len(commits)
    assert counts[project] == int(expected["ncommits"])
    assert len({row["author"] for row in observed}) == int(expected["nauthors"])
    assert (utc_date(min(int(row["time"]) for row in observed)) if observed else "") == expected["from"]
    assert (utc_date(max(int(row["time"]) for row in observed)) if observed else "") == expected["to"]
    assert int(expected["nstars"]) == github[project]["stars"]
    assert int(expected["nforks"]) == github[project]["forks"]
    assert expected["lastGHCommitDate"] == github[project]["last_commit_date"]
    source_counts_by_project[project] = {
        "WoC object contents": len(actual_hashes & set(woc_records)),
        "Git-recovered object contents": len(actual_hashes & recovered_hashes),
        "Raw p2c IDs": len(memberships[project]),
        "Verified non-commit tags excluded": len(excluded_in_project),
        "Unavailable object contents": len(actual_hashes & missing_hashes),
        "Author/date statistics complete": not bool(actual_hashes & missing_hashes),
    }

assert recovered_hashes <= set(recovery["recovered"])
for sha in recovered_hashes:
    assert recovery["recovered"][sha]["git_object_sha1_verified"] is True

summary_sha256 = hashlib.sha256(Path(f"{NETID}_project_summary.csv").read_bytes()).hexdigest()
saved_report = json.loads((DATA / f"{NETID}_validation.json").read_text(encoding="utf-8"))
assert saved_report["summary_sha256"] == summary_sha256
assert saved_report["counts"] == counts
assert saved_report["project_count"] == 10
assert saved_report["raw_p2c_project_object_rows"] == len(raw_pairs)
assert saved_report["excluded_noncommit_objects"] == len(exclusions)
assert saved_report["excluded_noncommit_rows"] == len(excluded_pairs)
assert saved_report["project_commit_rows"] == len(rows)
assert saved_report["unique_candidate_objects"] == len(required_hashes)
assert saved_report["unique_commit_objects"] == len(required_hashes & set(records))
assert saved_report["duplicate_project_commit_pairs"] == 0
assert saved_report["missing_commits"] == len(missing_hashes)
assert saved_report["missing_project_commit_rows"] == sum(sha in missing_hashes for _, sha in expected_pairs)
assert saved_report["metadata_complete"] is (not missing_hashes)
assert saved_report["available_commit_objects"] == len(required_hashes & set(records))
assert saved_report["woc_commit_objects"] == len(required_hashes & set(woc_records))
assert saved_report["git_recovered_commit_objects"] == len(recovered_hashes)
assert saved_report["woc_commit_objects"] + saved_report["git_recovered_commit_objects"] == saved_report["available_commit_objects"]
assert summary_sha256 == EXPECTED_SUMMARY_SHA256, (
    "The data changed. Rebuild the notebook with scripts/build_notebook.py to update its Markdown results."
)
# Later parts append columns to this shared file; verify the original Part 1 data.
import io
part1_stats_csv = io.StringIO(newline="")
part1_writer = csv.DictWriter(part1_stats_csv, fieldnames=STATS_COLUMNS, delimiter=";",
                             lineterminator="\n", extrasaction="ignore")
part1_writer.writeheader()
part1_writer.writerows(stats_rows)
assert hashlib.sha256(part1_stats_csv.getvalue().encode("utf-8")).hexdigest() == EXPECTED_STATS_SHA256, (
    "Project statistics changed. Rebuild the notebook to update its Markdown results."
)
assert hashlib.sha256((DATA / f"{NETID}_github_metadata.json").read_bytes()).hexdigest() == EXPECTED_GITHUB_SHA256, (
    "GitHub metadata changed. Rebuild the notebook to update its Markdown results and retrieval dates."
)
print(json.dumps({
    "projects": len(project_ids), "project_commit_rows": len(rows),
    "raw_p2c_project_object_rows": len(raw_pairs), "excluded_noncommit_rows": len(excluded_pairs),
    "excluded_noncommit_objects": len(exclusions),
    "unique_candidate_objects": len(required_hashes),
    "unique_commit_objects": len(required_hashes & set(records)), "missing_pairs": len(missing_pairs),
    "available_commit_objects": len(required_hashes & set(records)),
    "missing_metadata_objects": len(missing_hashes), "metadata_complete": not bool(missing_hashes),
    "extra_pairs": len(extra_pairs), "duplicate_pairs": duplicate_pairs,
    "woc_object_contents": len(required_hashes & set(woc_records)),
    "git_recovered_object_contents": len(recovered_hashes),
    "summary_sha256": summary_sha256, "counts": counts,
    "source_counts_by_project": source_counts_by_project,
}, indent=2))
'''


RAW_OBJECT_CODE = r'''
# Optional archive verification is entirely offline.
import zipfile

def verify_tag_chain(archive, root_sha, evidence):
    assert evidence["object_type"] == "tag" and evidence["git_object_sha1_verified"] is True
    # Older direct-tag entries have no chain; their target is already a commit.
    chain = evidence.get("tag_chain")
    if chain is None:
        chain = [{
            "sha1": root_sha, "object_type": evidence["object_type"],
            "git_object_sha1_verified": evidence["git_object_sha1_verified"],
            "direct_target_sha1": evidence.get("direct_target_sha1", evidence["target_commit_sha1"]),
            "direct_target_type": evidence.get("direct_target_type", "commit"),
            "raw_sha256": evidence["raw_sha256"],
            **({"raw_object_bytes": evidence["raw_object_bytes"]} if "raw_object_bytes" in evidence else {}),
        }]
    assert chain and chain[0]["sha1"] == root_sha
    chain_hashes = [item["sha1"] for item in chain]
    assert len(chain_hashes) == len(set(chain_hashes)), "A tag chain must not contain a cycle"
    if "direct_target_sha1" in evidence:
        assert evidence["direct_target_sha1"] == chain[0]["direct_target_sha1"]
    if "direct_target_type" in evidence:
        assert evidence["direct_target_type"] == chain[0]["direct_target_type"]
    for index, item in enumerate(chain):
        sha = item["sha1"]
        assert item["object_type"] == "tag" and item["git_object_sha1_verified"] is True
        raw = archive.read(f"{sha}.tag")
        object_bytes = b"tag " + str(len(raw)).encode("ascii") + b"\x00" + raw
        assert hashlib.sha1(object_bytes).hexdigest() == sha
        assert hashlib.sha256(raw).hexdigest() == item["raw_sha256"]
        if "raw_object_bytes" in item:
            assert len(raw) == item["raw_object_bytes"]
        if index == 0:
            assert hashlib.sha256(raw).hexdigest() == evidence["raw_sha256"]
            if "raw_object_bytes" in evidence:
                assert len(raw) == evidence["raw_object_bytes"]
        target = item["direct_target_sha1"]
        target_type = item["direct_target_type"]
        headers = raw.partition(b"\n\n")[0].split(b"\n")
        assert headers[:2] == [b"object " + target.encode("ascii"), b"type " + target_type.encode("ascii")]
        if index + 1 < len(chain):
            assert target_type == "tag" and target == chain[index + 1]["sha1"]
        else:
            assert target_type == "commit" and target == evidence["target_commit_sha1"]
    assert evidence["target_commit_sha1"] in required_hashes
    return set(chain_hashes)

archive_path = DATA / f"{NETID}_git_objects.zip"
if archive_path.exists():
    verified_tag_hashes = set()
    with zipfile.ZipFile(archive_path) as archive:
        for sha in sorted(recovered_hashes):
            raw = archive.read(f"{sha}.commit")
            object_bytes = b"commit " + str(len(raw)).encode("ascii") + b"\x00" + raw
            assert hashlib.sha1(object_bytes).hexdigest() == sha
            assert hashlib.sha256(raw).hexdigest() == recovery["recovered"][sha]["raw_commit_sha256"]
        for sha, evidence in sorted(exclusions.items()):
            verified_tag_hashes.update(verify_tag_chain(archive, sha, evidence))
    print(f"Verified {len(recovered_hashes):,} recovered commits and {len(verified_tag_hashes):,} tag objects "
          f"supporting {len(exclusions):,} WoC tag exclusions. Auxiliary chain tags are not extra exclusions.")
else:
    print("Raw-object archive is absent; CSV/cache/provenance checks above still ran.")
'''


def build(root, output):
    result = load_and_check(root)
    projects, stats, github = result["projects"], result["stats"], result["github"]
    report = result["report"]
    cells = []

    def markdown(source, identifier):
        cells.append(nbformat.v4.new_markdown_cell(source.strip(), id=identifier))

    def code(source, identifier):
        cells.append(nbformat.v4.new_code_cell(textwrap.dedent(source).strip(), id=identifier))

    markdown(f"""
# Mini Project 2 — Part 1

**NetID: {NETID}**

This notebook collects data for the ten assigned projects. The three sections below
show the CSV file, GitHub information, and WoC statistics required for Part 1.
""", "title-and-scope")

    markdown(f"""
## 1. CSV file

[dpate172_project_summary.csv](dpate172_project_summary.csv) contains
**{result['summary_rows']:,} rows across 10 projects**, separated by semicolons:

```text
project_wocid;commit_sha1;author;time;commit message
```

Each row keeps the project ID, commit ID, author, author timestamp, and full message.
The `time` column uses Unix seconds. **{len(result['missing_hashes'])} rows have unavailable
metadata**; those fields are blank, as explained below.

[dpate172_project_stats.csv](dpate172_project_stats.csv) saves the project-level results.
""", "csv-results")

    collection_date = result["gh_document"]["collection_started_at_utc"][:10]
    github_rows = []
    woc_rows = []
    missing_rows = []
    for project in projects:
        row, gh = stats[project], github[project]
        github_rows.append([
            f"[{project}]({gh['canonical_github_url']})", row["nstars"], row["nforks"],
            f"[{row['lastGHCommitDate']}]({gh['last_commit_url']})",
        ])
        missing_count = len(set(result["membership"][project]) & result["missing_hashes"])
        label = project + (" †" if missing_count else "")
        woc_rows.append([label, row["ncommits"], row["nauthors"], row["to"], row["from"]])
        if missing_count:
            missing_rows.append([project, int(row["ncommits"]) - missing_count, missing_count])

    markdown(f"## 2. GitHub data\n\nCollected through GitHub's API on **{collection_date}**. "
        "The last commit date is the committer date of the repository's default-branch tip. "
        "Project names and dates link to the source pages.\n\n" + markdown_table(
            ["Project", "Stars", "Forks", "Last commit date (UTC)"], github_rows), "github-results")

    markdown("## 3. WoC results\n\n" + markdown_table(
        ["Project", "Number of commits", "Number of authors", "Max time (UTC)", "Min time (UTC)"], woc_rows) +
        "\n\nAuthors are counted by distinct author strings. Max and min time are the latest and earliest "
        "available author timestamps, converted to UTC.\n\n"
        "**† Marked projects have missing metadata.** Their counts include the unresolved WoC-listed IDs; "
        "whether those IDs are actual commits is unknown. Their author counts and date ranges use only "
        "the available records and may be incomplete.", "woc-results")

    markdown(f"""
## Collection notes

The code uses the official `python-woc` client to get each project's IDs with `p2c`,
then requests commit details in batches of 10 with pauses between requests.
WoC supplied **{report['woc_commit_objects']:,}** records. Another
**{report['git_recovered_commit_objects']:,}** were recovered from the original Git
repositories and checked against their Git SHA-1s.

The WoC lists also contained **{len(result['excluded_pairs'])} annotated tags**.
These were excluded after checking their type and confirming that their target
commits were already listed. The CSV therefore has
{len(result['raw_pairs']):,} − {len(result['excluded_pairs'])} = **{result['summary_rows']:,} rows**.

Some records could not be retrieved from WoC or the other checked sources:

{markdown_table(["Project", "Rows with metadata", "Rows missing metadata"], missing_rows)}

Their IDs remain in the CSV with blank author, time, and message fields. The exact IDs
and source checks are saved in [the missing-data report](data/dpate172_missing_object_research.json).
Recovery details are in [the Git recovery report](data/dpate172_git_recovery.json).

Data were collected on **{collection_date}**. The live WoC API does not confirm the
assignment's January 2025 cutoff. WoC and GitHub counts can differ because they cover
different dates and branches and group author identities differently.
""", "collection-notes")

    markdown("""
## Retrieval code

Run the notebook from the repository folder after installing `requirements.txt`.
With `REFRESH_FROM_API = False`, it checks the saved data without making API requests.
Set it to `True` to run collection using the existing checkpoints.

`ALLOW_MISSING_METADATA = False` stops a new export if metadata is still missing.
Setting it to `True` allows only the already investigated exceptions documented above.
See [PART1.md](PART1.md) for setup and recovery commands.
""", "retrieval-instructions")
    code(f"""from pathlib import Path
assert Path("net2prj.csv").exists(), "Run the notebook from the repository root."
REFRESH_FROM_API = False
ALLOW_MISSING_METADATA = False
EXPECTED_SUMMARY_SHA256 = "{result['digest']}"
EXPECTED_STATS_SHA256 = "{result['stats_digest']}"
EXPECTED_GITHUB_SHA256 = "{result['github_digest']}"
print("Mode:", "API refresh with checkpoint reuse" if REFRESH_FROM_API else "Offline verification")""", "run-settings")
    for number, source in enumerate(source_groups(root / "scripts" / "retrieve_part1.py"), 1):
        code(source, f"retrieval-source-{number}")
    code("""
if REFRESH_FROM_API:
    import subprocess
    import sys
    # The repository script records API URLs, timestamps, branches, and tip SHAs.
    subprocess.run([sys.executable, "scripts/collect_github_metadata.py", "--netid", NETID, "--refresh"], check=True)
    retrieved_rows, retrieved_stats, retrieval_report = await collect(allow_missing=ALLOW_MISSING_METADATA)
else:
    print("Using packaged final CSVs and source caches; no API requests made.")
""", "retrieve-or-use-package")
    markdown("""
## Data checks

These cells check that all ten projects are present, each project/commit pair appears
once, and the CSV matches the saved source records. They also recalculate the summary
statistics and verify the recovered Git objects and excluded tags.
""", "validation-instructions")
    code(VALIDATION_CODE, "validate-final-data")
    code(RAW_OBJECT_CODE, "verify-recovered-git-objects")
    code("""
import pandas as pd
df = pd.read_csv(
    f"{NETID}_project_summary.csv", sep=";", keep_default_na=False,
    dtype={"project_wocid": str, "commit_sha1": str, "author": str, "time": str, "commit message": str},
)
# Validate integers above, then retain unknown timestamps as nullable integers for display.
df["time"] = pd.array([int(value) if value != "" else pd.NA for value in df["time"]], dtype="Int64")
assert len(df) == len(rows)
display(df.head(3))
display(pd.DataFrame(stats_rows)[STATS_COLUMNS])
""", "preview-deliverables")
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "file_extension": ".py", "mimetype": "text/x-python",
                          "pygments_lexer": "ipython3"},
    })
    nbformat.validate(notebook)
    output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, output)
    print(f"Built {output} with {len(cells)} cells; dataset SHA-256 {result['digest']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    build(root, args.output or root / f"{NETID}.ipynb")


if __name__ == "__main__":
    main()

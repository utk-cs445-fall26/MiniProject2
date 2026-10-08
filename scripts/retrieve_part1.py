"""Retrieve dpate172's Part 1 data with the official Python World of Code API.

The notebook includes these functions directly so its retrieval code is visible.
Successful responses are checkpointed; errors never become fabricated CSV rows.
"""

import asyncio
import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("XDG_CACHE_HOME", str(Path(".venv/cache").resolve()))
from woc.remote import WocMapsRemoteAsync

NETID = "dpate172"
BASE_URL = "https://worldofcode.org/api/"
BATCH_SIZE = 10
REQUEST_PAUSE = 2.1  # Pace public requests; the client also honors Retry-After.
DATA = Path("data")
SUMMARY_COLUMNS = ["project_wocid", "commit_sha1", "author", "time", "commit message"]
STATS_COLUMNS = ["Project", "ncommits", "nauthors", "from", "to", "nstars", "nforks", "lastGHCommitDate"]


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def utc_date(timestamp):
    return datetime.fromtimestamp(int(timestamp), timezone.utc).isoformat().replace("+00:00", "Z")


def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def assigned_projects():
    with open("net2prj.csv", newline="", encoding="utf-8-sig") as handle:
        projects = [{"project_wocid": row[1], "github_url": row[2]}
                    for row in csv.reader(handle) if row and row[0] == NETID]
    assert len(projects) == 10 and len({p["project_wocid"] for p in projects}) == 10
    return projects


def verified_commit_memberships(raw_memberships):
    """Remove only SHA-verified non-commit objects mislabeled by WoC p2c."""
    path = DATA / f"{NETID}_git_recovery.json"
    recovery = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    exclusions = recovery.get("excluded_noncommit_objects", {})
    all_hashes = {sha for values in raw_memberships.values() for sha in values}
    for sha, evidence in exclusions.items():
        assert sha in all_hashes and evidence["object_type"] == "tag"
        assert evidence["git_object_sha1_verified"] is True
        target = evidence["target_commit_sha1"]
        # No commit is lost: the tag's target must already be listed separately.
        for project, hashes in raw_memberships.items():
            if sha in hashes:
                assert target in hashes, f"Tag target absent from {project}: {sha}"
    return {project: [sha for sha in hashes if sha not in exclusions]
            for project, hashes in raw_memberships.items()}, exclusions


async def retry_call(operation, label, attempts=5):
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as error:
            if attempt == attempts - 1:
                raise RuntimeError(f"Failed after {attempts} attempts: {label}") from error
            delay = min(60, 5 * 2 ** attempt)
            print(f"Retrying {label} after {type(error).__name__}; wait {delay}s", flush=True)
            await asyncio.sleep(delay)


async def get_project_commits(client, projects):
    """Use p2c, retaining pagination and explicit per-project membership."""
    path = DATA / f"{NETID}_woc_project_commits.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["base_url"] == BASE_URL
    else:
        saved = {"base_url": BASE_URL, "retrieved_at_utc": utc_now(), "projects": {}}
    for project in projects:
        key = project["project_wocid"]
        if key not in saved["projects"]:
            async def get_all():
                values = []
                async for page in client.iter_values("p2c", key):
                    values.extend(page)
                    await asyncio.sleep(REQUEST_PAUSE)
                return values
            values = await retry_call(get_all, f"p2c/{key}")
            assert values and all(re.fullmatch(r"[0-9a-f]{40}", sha) for sha in values)
            saved["projects"][key] = sorted(set(values))
            save_json(path, saved)
        print(f"{key}: {len(saved['projects'][key]):,} WoC-listed object IDs", flush=True)
    assert set(saved["projects"]) == {p["project_wocid"] for p in projects}
    return saved


def flatten_commit(sha, commit):
    assert isinstance(commit, (list, tuple)) and len(commit) == 5, sha
    assert isinstance(commit[2][0], str) and isinstance(commit[4], str), sha
    return {"commit_sha1": sha, "author": commit[2][0], "time": int(commit[2][1]),
            "commit message": commit[4]}


def load_commit_cache(path):
    records = {}
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            lines = handle.readlines()
        for index, line in enumerate(lines):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                if index != len(lines) - 1:
                    raise
                # A process interrupted during append may leave one partial final line.
                path.write_text("".join(lines[:index]), encoding="utf-8")
                break
            assert re.fullmatch(r"[0-9a-f]{40}", item["commit_sha1"])
            assert isinstance(item["author"], str) and isinstance(item["commit message"], str)
            assert isinstance(item["time"], int)
            records[item["commit_sha1"]] = item
    return records


async def retrieve_commits(client, project_commits, allow_missing=False):
    required = sorted({sha for values in project_commits.values() for sha in values})
    cache_path = DATA / f"{NETID}_woc_commits.jsonl"
    records = load_commit_cache(cache_path)
    recovery_path = DATA / f"{NETID}_git_recovered_commits.jsonl"
    recovered = load_commit_cache(recovery_path)
    for sha, record in recovered.items():
        if sha in records:
            assert records[sha] == record, f"Conflicting WoC/Git contents for {sha}"
        else:
            records[sha] = record
    error_path = DATA / f"{NETID}_woc_missing.json"
    failures = json.loads(error_path.read_text()) if error_path.exists() else {}
    missing = [sha for sha in required if sha not in records and sha not in failures]
    print(f"Commit details: {len(required):,} candidate IDs; {len(missing):,} to query", flush=True)
    started = time.monotonic()
    with cache_path.open("a", encoding="utf-8") as cache:
        for start in range(0, len(missing), BATCH_SIZE):
            pending = missing[start:start + BATCH_SIZE]
            response, errors = await retry_call(
                lambda: client.get_values_many("commit.tch", pending), "commit.tch batch")
            good = {}
            for sha, value in response.items():
                assert sha in pending and value, sha
                good[sha] = flatten_commit(sha, value[0])
            pending = [sha for sha in pending if sha not in good]
            await asyncio.sleep(REQUEST_PAUSE)
            if pending:
                # The fast table can miss objects; try the official object endpoint too.
                response, fallback_errors = await retry_call(
                    lambda: client.show_content_many("commit", pending), "commit object batch")
                for sha, value in response.items():
                    assert sha in pending, sha
                    good[sha] = flatten_commit(sha, value)
                pending = [sha for sha in pending if sha not in good]
                for sha in pending:
                    failures[sha] = {"commit.tch": errors.get(sha, "no result"),
                                     "commit_object": fallback_errors.get(sha, "no result")}
                save_json(error_path, failures)
                await asyncio.sleep(REQUEST_PAUSE)
            for sha, record in good.items():
                cache.write(json.dumps(record, ensure_ascii=False) + "\n")
                records[sha] = record
            cache.flush()
            if pending:
                print(f"{len(pending)} WoC object(s) unavailable; recorded for recovery", flush=True)
            if start % 500 == 0 or start + BATCH_SIZE >= len(missing):
                complete = len(set(records).intersection(required))
                print(f"Saved metadata for {complete:,}/{len(required):,} candidate IDs "
                      f"({time.monotonic() - started:.0f}s this run)", flush=True)
    unresolved = sorted(set(required) - set(records))
    research_path = DATA / f"{NETID}_missing_object_research.json"
    research = json.loads(research_path.read_text(encoding="utf-8")) if research_path.exists() else {}
    if unresolved and allow_missing:
        uninvestigated = [sha for sha in unresolved
                         if not research.get(sha, {}).get("retain_identifier_only")
                         or not research.get(sha, {}).get("checks")]
        if uninvestigated:
            raise RuntimeError(f"Refusing placeholders for {len(uninvestigated)} uninvestigated hashes. "
                               "Complete recovery and document source checks first.")
    save_json(DATA / f"{NETID}_unavailable_commits.json", {
        "checked_at_utc": utc_now(),
        "unavailable": {sha: {"woc_projects": [project for project, hashes in project_commits.items()
                                                if sha in hashes],
                              "woc_errors": failures.get(sha, {}), "object_type": "unknown",
                              "research_evidence": str(research_path)}
                        for sha in unresolved},
    })
    if unresolved and not allow_missing:
        raise RuntimeError(f"{len(unresolved)} missing objects recorded in {error_path}. "
                           "Recover from original Git objects and rerun; no incomplete CSV exported.")
    return {sha: records[sha] for sha in required if sha in records}


def export_summary(projects, memberships, records, allow_missing=False):
    rows = []
    for project in projects:
        key = project["project_wocid"]
        for sha in memberships[key]:
            if sha not in records:
                assert allow_missing, f"Missing metadata: {sha}"
            record = records.get(sha, {"commit_sha1": sha, "author": "", "time": "", "commit message": ""})
            rows.append({"project_wocid": key, **record})
    rows.sort(key=lambda row: (row["project_wocid"], row["time"] == "",
                              row["time"] if row["time"] != "" else 0, row["commit_sha1"]))
    path = Path(f"{NETID}_project_summary.csv")
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        assert reader.fieldnames == SUMMARY_COLUMNS
        roundtrip = list(reader)
    assert len(roundtrip) == sum(map(len, memberships.values()))
    assert len({(row['project_wocid'], row['commit_sha1']) for row in roundtrip}) == len(rows)
    for original, restored in zip(rows, roundtrip):
        assert all(str(original[key]) == restored[key] for key in SUMMARY_COLUMNS)
    print(f"Saved and verified {len(rows):,} rows: {path}", flush=True)
    return rows


def export_stats(projects, rows):
    metadata = json.loads((DATA / f"{NETID}_github_metadata.json").read_text(encoding="utf-8"))
    github = {p["project_wocid"]: p for p in metadata["projects"]}
    stats = []
    for project in projects:
        key = project["project_wocid"]
        commits = [row for row in rows if row["project_wocid"] == key]
        observed = [row for row in commits if row["time"] != ""]
        gh = github[key]
        stats.append({"Project": key, "ncommits": len(commits),
                      "nauthors": len({row["author"] for row in observed}),
                      "from": utc_date(min(row["time"] for row in observed)) if observed else "",
                      "to": utc_date(max(row["time"] for row in observed)) if observed else "",
                      "nstars": gh["stars"], "nforks": gh["forks"],
                      "lastGHCommitDate": gh["last_commit_date"]})
    with open(f"{NETID}_project_stats.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATS_COLUMNS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(stats)
    return stats


async def collect(allow_missing=False):
    DATA.mkdir(exist_ok=True)
    projects = assigned_projects()
    client = WocMapsRemoteAsync(base_url=BASE_URL, api_key=os.getenv("WOC_API_KEY"), max_connections=1)
    # Explicit network timeout; rate limiting is handled by the official client.
    import httpx
    client.client.timeout = httpx.Timeout(60)
    try:
        memberships = await get_project_commits(client, projects)
        commit_memberships, exclusions = verified_commit_memberships(memberships["projects"])
        records = await retrieve_commits(client, commit_memberships, allow_missing=allow_missing)
    finally:
        await client.client.aclose()
    rows = export_summary(projects, commit_memberships, records, allow_missing=allow_missing)
    stats = export_stats(projects, rows)
    required_hashes = {sha for hashes in commit_memberships.values() for sha in hashes}
    missing_hashes = required_hashes - set(records)
    woc_hashes = set(load_commit_cache(DATA / f"{NETID}_woc_commits.jsonl")) & set(records)
    recovered_hashes = set(records) - woc_hashes
    report = {"netid": NETID, "checked_at_utc": utc_now(), "base_url": BASE_URL,
              "project_count": len(projects), "project_commit_rows": len(rows),
              "raw_p2c_project_object_rows": sum(map(len, memberships["projects"].values())),
              "excluded_noncommit_objects": len(exclusions),
              "excluded_noncommit_rows": sum(len(set(values) & set(exclusions))
                                             for values in memberships["projects"].values()),
              "unique_candidate_objects": len(required_hashes),
              "unique_commit_objects": len(records), "missing_commits": len(missing_hashes),
              "available_commit_objects": len(records), "metadata_complete": not missing_hashes,
              "missing_project_commit_rows": sum(row["time"] == "" for row in rows),
              "woc_commit_objects": len(woc_hashes),
              "git_recovered_commit_objects": len(recovered_hashes),
              "duplicate_project_commit_pairs": 0, "csv_roundtrip_passed": True,
              "summary_sha256": hashlib.sha256(Path(f"{NETID}_project_summary.csv").read_bytes()).hexdigest(),
              "counts": {p["Project"]: p["ncommits"] for p in stats}}
    save_json(DATA / f"{NETID}_validation.json", report)
    print(json.dumps(report, indent=2))
    return rows, stats, report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-missing", action="store_true",
                        help="Preserve unrecoverable hashes with blank metadata and an explicit coverage report")
    asyncio.run(collect(allow_missing=parser.parse_args().allow_missing))

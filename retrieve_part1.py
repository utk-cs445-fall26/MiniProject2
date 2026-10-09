"""Retrieve MP2 Part 1 data for hsaleh5 from World of Code and GitHub.

The World of Code HTTP API accepts at most ten keys per batch request.  This
script uses batches of ten, pauses between small waves of requests, retries
transient failures, and checkpoints results by project so an interrupted run
can be resumed safely.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


NETID = "hsaleh5"
WOC_BASE = "https://worldofcode.org/api"
WOC_READER_PREFIX = "https://r.jina.ai/"
GITHUB_API = "https://api.github.com"
BATCH_SIZE = 10  # WoC's documented maximum is 10 keys per batch request.
REQUESTS_PER_WAVE = 1
WAVE_DELAY_SECONDS = 3.2  # reader relay allows 20 requests per 60 seconds
MAX_RETRIES = 5

ROOT = Path(__file__).resolve().parent
ASSIGNMENTS_FILE = ROOT / "net2prj.csv"
SUMMARY_FILE = ROOT / f"{NETID}_project_summary.csv"
STATS_FILE = ROOT / f"{NETID}_project_stats.csv"
METADATA_FILE = ROOT / f"{NETID}_part1_metadata.json"
CACHE_DIR = ROOT / ".part1_cache"
REPO_CACHE_DIR = ROOT / ".part1_repos"
GITHUB_CACHE_FILE = CACHE_DIR / "github_metadata.json"

_thread_local = threading.local()


def session() -> requests.Session:
    """Return one reusable HTTP session per worker thread."""
    if not hasattr(_thread_local, "session"):
        s = requests.Session()
        s.headers.update(
            {
                "Accept": "application/vnd.github+json, application/json",
                "User-Agent": f"UTK-MP2-{NETID}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        _thread_local.session = s
    return _thread_local.session


def get_json(url: str, *, params=None, timeout: int = 120):
    """GET JSON with exponential backoff for rate limits/transient errors."""
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = session().get(url, params=params, timeout=(15, timeout))
            if response.status_code == 429 or response.status_code >= 500:
                retry_after = float(response.headers.get("Retry-After", 2**attempt))
                time.sleep(max(retry_after, 0.5))
                continue
            response.raise_for_status()
            return response.json(), response.headers
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt + 1 < MAX_RETRIES:
                time.sleep(2**attempt)
    raise RuntimeError(f"Request failed after {MAX_RETRIES} attempts: {url}") from last_error


def get_woc_json(path: str, *, params=None):
    """Read a WoC endpoint through an HTTPS relay when its origin throttles us."""
    target = requests.Request("GET", f"{WOC_BASE}{path}", params=params).prepare().url
    relay_url = f"{WOC_READER_PREFIX}{target}"
    response = None
    for attempt in range(MAX_RETRIES):
        response = session().get(relay_url, timeout=(15, 120))
        if response.status_code != 429:
            response.raise_for_status()
            break
        if attempt + 1 == MAX_RETRIES:
            response.raise_for_status()
        retry_after = min(float(response.headers.get("Retry-After", 30)), 30)
        print(f"  WoC relay rate limit; waiting {retry_after:.0f} seconds", flush=True)
        time.sleep(max(retry_after, 10))
    assert response is not None
    text = response.text
    # The reader wraps JSON with a short provenance header and a
    # ``Markdown Content:`` marker. Extract only the original JSON object.
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"WoC relay did not return JSON for {path}: {text[:200]}")
    parsed = json.loads(text[start : end + 1])
    if (
        isinstance(parsed, dict)
        and isinstance(parsed.get("data"), dict)
        and isinstance(parsed["data"].get("content"), str)
    ):
        return json.loads(parsed["data"]["content"])
    return parsed


def load_assignments() -> list[dict[str, str]]:
    assignments = pd.read_csv(ASSIGNMENTS_FILE, dtype=str)
    mine = assignments.loc[assignments["netID"].str.casefold() == NETID.casefold()]
    if len(mine) != 10:
        raise ValueError(f"Expected 10 projects for {NETID}, found {len(mine)}")
    return [
        {"project_wocid": row.WoC.lower(), "github_url": row.GH}
        for row in mine.itertuples(index=False)
    ]


def github_slug(url: str) -> str:
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", url, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Not a GitHub repository URL: {url}")
    return match.group(1).removesuffix(".git")


def last_page_count(headers, first_page_length: int) -> int:
    """Extract the REST collection size from GitHub's pagination links."""
    link = headers.get("Link", "")
    match = re.search(r"[?&]page=(\d+)[^>]*>; rel=\"last\"", link)
    return int(match.group(1)) if match else first_page_length


def get_github_metadata(url: str) -> dict:
    slug = github_slug(url)
    CACHE_DIR.mkdir(exist_ok=True)
    if GITHUB_CACHE_FILE.exists():
        github_cache = json.loads(GITHUB_CACHE_FILE.read_text(encoding="utf-8"))
        if slug in github_cache:
            return github_cache[slug]
    else:
        github_cache = {}
    repo, _ = get_json(f"{GITHUB_API}/repos/{slug}")
    branch = repo["default_branch"]
    commits, commit_headers = get_json(
        f"{GITHUB_API}/repos/{slug}/commits",
        params={"sha": branch, "per_page": 1},
    )
    contributors, contributor_headers = get_json(
        f"{GITHUB_API}/repos/{slug}/contributors",
        params={"anon": "true", "per_page": 1},
    )
    if commits:
        commit_info = commits[0]["commit"]
        last_date = (
            commit_info.get("committer", {}).get("date")
            or commit_info.get("author", {}).get("date")
        )
        last_date = last_date[:10]
    else:
        last_date = None
    result = {
        "github_repo": slug,
        "nstars": int(repo["stargazers_count"]),
        "nforks": int(repo["forks_count"]),
        "lastGHCommitDate": last_date,
        "github_default_branch": branch,
        "github_default_branch_commits": last_page_count(commit_headers, len(commits)),
        "github_contributors": last_page_count(contributor_headers, len(contributors)),
    }
    github_cache[slug] = result
    GITHUB_CACHE_FILE.write_text(
        json.dumps(github_cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def get_project_commits(project_wocid: str) -> list[str]:
    CACHE_DIR.mkdir(exist_ok=True)
    id_cache = CACHE_DIR / f"{project_wocid}.sha1"
    if id_cache.exists():
        commits = [line.strip() for line in id_cache.read_text(encoding="ascii").splitlines()]
        if commits:
            return commits
    payload = get_woc_json(f"/lookup/map/p2c/{project_wocid}")
    commits = payload.get("data", [])
    if not isinstance(commits, list) or not all(isinstance(c, str) for c in commits):
        raise TypeError(f"Unexpected p2c response for {project_wocid}")
    if len(commits) != len(set(commits)):
        raise ValueError(f"WoC returned duplicate commit IDs for {project_wocid}")
    commits = sorted(commits)
    id_cache.write_text("\n".join(commits) + "\n", encoding="ascii")
    return commits


def chunks(values: list[str], size: int):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def get_commit_batch(commit_ids: list[str]) -> tuple[list[dict], dict]:
    params = [("q", commit_id) for commit_id in commit_ids]
    payload = get_woc_json("/lookup/map/commit.tch", params=params)
    data = payload.get("data", {})
    errors = payload.get("errors", {})
    records: list[dict] = []
    for commit_sha1, wrapped in data.items():
        commit = wrapped[0]  # commit.tch values are wrapped once by the map API.
        records.append(
            {
                "commit_sha1": commit_sha1,
                "author": commit[2][0],
                "time": int(commit[2][1]),
                "commit message": commit[4],
            }
        )
    returned = {record["commit_sha1"] for record in records}
    for missing in set(commit_ids) - returned:
        errors.setdefault(missing, "No data returned")
    return records, errors


def read_cache(cache_file: Path) -> dict[str, dict]:
    records: dict[str, dict] = {}
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    record = json.loads(line)
                    records[record["commit_sha1"]] = record
    return records


def append_cache(cache_file: Path, records: list[dict]) -> None:
    with cache_file.open("a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def ensure_github_mirror(project_wocid: str, github_url: str) -> Path:
    """Create/update a blobless mirror used to read Git commit objects by SHA-1."""
    REPO_CACHE_DIR.mkdir(exist_ok=True)
    mirror = REPO_CACHE_DIR / f"{project_wocid}.git"
    if mirror.exists():
        command = ["git", "-C", str(mirror), "fetch", "--prune", "origin"]
    else:
        command = [
            "git",
            "clone",
            "--mirror",
            "--filter=blob:none",
            github_url,
            str(mirror),
        ]
    print(f"  {'updating' if mirror.exists() else 'cloning'} GitHub mirror", flush=True)
    subprocess.run(command, check=True)
    return mirror


def get_local_commit_objects(mirror: Path, commit_ids: list[str]) -> list[dict]:
    """Read commit metadata from Git's object database using one batch process."""
    if not commit_ids:
        return []
    process = subprocess.run(
        ["git", "-C", str(mirror), "cat-file", "--batch"],
        input=("\n".join(commit_ids) + "\n").encode("ascii"),
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    )
    output = process.stdout
    position = 0
    records: list[dict] = []
    for requested_sha1 in commit_ids:
        line_end = output.find(b"\n", position)
        if line_end < 0:
            raise RuntimeError("Unexpected end of git cat-file output")
        descriptor = output[position:line_end].decode("ascii", errors="replace")
        position = line_end + 1
        if descriptor.endswith(" missing"):
            continue
        fields = descriptor.split()
        if len(fields) != 3:
            raise RuntimeError(f"Unexpected git object descriptor: {descriptor}")
        object_sha1, object_type, size_text = fields
        size = int(size_text)
        content = output[position : position + size]
        position += size + 1  # git adds a newline after each batch object's content.
        if object_type != "commit":
            continue

        header_bytes, separator, message_bytes = content.partition(b"\n\n")
        if not separator:
            raise RuntimeError(f"Malformed commit object: {object_sha1}")
        encoding = "utf-8"
        for header_line in header_bytes.splitlines():
            if header_line.startswith(b"encoding "):
                encoding = header_line[9:].decode("ascii", errors="replace")
                break
        headers = header_bytes.decode(encoding, errors="replace")
        author_line = next(
            (line[7:] for line in headers.splitlines() if line.startswith("author ")),
            None,
        )
        match = re.match(r"^(.*) (\d+) ([+-]\d{4})$", author_line or "")
        if not match:
            raise RuntimeError(f"Could not parse author header for {object_sha1}")
        records.append(
            {
                "commit_sha1": object_sha1,
                "author": match.group(1),
                "time": int(match.group(2)),
                "commit message": message_bytes.decode(encoding, errors="replace"),
            }
        )
    return records


def retrieve_project(
    project_wocid: str, github_url: str, commit_ids: list[str]
) -> list[dict]:
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{project_wocid}.jsonl"
    cached = read_cache(cache_file)
    mirror = ensure_github_mirror(project_wocid, github_url)
    locally_available = get_local_commit_objects(
        mirror, [commit for commit in commit_ids if commit not in cached]
    )
    append_cache(cache_file, locally_available)
    for record in locally_available:
        cached[record["commit_sha1"]] = record
    pending = [commit for commit in commit_ids if commit not in cached]
    batches = list(chunks(pending, BATCH_SIZE))
    print(
        f"{project_wocid}: {len(commit_ids):,} IDs, "
        f"{len(cached):,} cached, {len(pending):,} pending",
        flush=True,
    )

    unresolved: dict[str, str] = {}
    for wave_start in range(0, len(batches), REQUESTS_PER_WAVE):
        wave = batches[wave_start : wave_start + REQUESTS_PER_WAVE]
        with ThreadPoolExecutor(max_workers=REQUESTS_PER_WAVE) as pool:
            futures = {pool.submit(get_commit_batch, batch): batch for batch in wave}
            for future in as_completed(futures):
                records, errors = future.result()
                append_cache(cache_file, records)
                for record in records:
                    cached[record["commit_sha1"]] = record
                unresolved.update(errors)
        completed = min((wave_start + len(wave)) * BATCH_SIZE, len(pending))
        if completed % 1000 < REQUESTS_PER_WAVE * BATCH_SIZE or completed == len(pending):
            print(f"  retrieved {completed:,}/{len(pending):,} pending records", flush=True)
        if wave_start + len(wave) < len(batches):
            time.sleep(WAVE_DELAY_SECONDS)

    # Retry any missing keys one at a time. This also distinguishes transient
    # batch errors from genuinely absent commit.tch records.
    missing = sorted(set(commit_ids) - set(cached))
    for commit_sha1 in missing:
        records, errors = get_commit_batch([commit_sha1])
        append_cache(cache_file, records)
        for record in records:
            cached[record["commit_sha1"]] = record
        if errors:
            unresolved.update(errors)
        time.sleep(WAVE_DELAY_SECONDS)

    still_missing = sorted(set(commit_ids) - set(cached))
    if still_missing:
        details = {key: unresolved.get(key, "unknown error") for key in still_missing[:10]}
        print(
            f"  warning: excluded {len(still_missing)} p2c keys without commit.tch "
            f"records (usually annotated-tag objects): {details}",
            flush=True,
        )

    return [cached[commit_sha1] for commit_sha1 in commit_ids if commit_sha1 in cached]


def main() -> None:
    assignments = load_assignments()
    all_rows: list[dict] = []
    metadata: list[dict] = []

    for item in assignments:
        project_wocid = item["project_wocid"]
        commit_ids = get_project_commits(project_wocid)
        records = retrieve_project(project_wocid, item["github_url"], commit_ids)
        for record in records:
            all_rows.append({"project_wocid": project_wocid, **record})

        times = [record["time"] for record in records]
        authors = {record["author"] for record in records}
        github = get_github_metadata(item["github_url"])
        metadata.append(
            {
                "Project": project_wocid,
                "ncommits": len(records),
                "nauthors": len(authors),
                "from": min(times),
                "to": max(times),
                "from_iso_utc": datetime.fromtimestamp(min(times), timezone.utc).isoformat(),
                "to_iso_utc": datetime.fromtimestamp(max(times), timezone.utc).isoformat(),
                **github,
            }
        )

    expected = sum(item["ncommits"] for item in metadata)
    if len(all_rows) != expected:
        raise AssertionError(f"Expected {expected} combined rows, found {len(all_rows)}")

    summary_columns = ["project_wocid", "commit_sha1", "author", "time", "commit message"]
    pd.DataFrame(all_rows, columns=summary_columns).to_csv(
        SUMMARY_FILE,
        sep=";",
        index=False,
        encoding="utf-8",
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )

    stats_columns = [
        "Project",
        "ncommits",
        "nauthors",
        "from",
        "to",
        "nstars",
        "nforks",
        "lastGHCommitDate",
    ]
    pd.DataFrame(metadata)[stats_columns].to_csv(
        STATS_FILE, sep=";", index=False, encoding="utf-8", lineterminator="\n"
    )

    METADATA_FILE.write_text(
        json.dumps(
            {
                "netid": NETID,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "woc_base_url": WOC_BASE,
                "batch_size": BATCH_SIZE,
                "projects": metadata,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {SUMMARY_FILE.name}: {len(all_rows):,} commit rows", flush=True)
    print(f"Wrote {STATS_FILE.name}: {len(metadata)} project rows", flush=True)


if __name__ == "__main__":
    main()

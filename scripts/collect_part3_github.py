#!/usr/bin/env python3
"""Collect historical default-branch status and recent commits for Part 3.

Public GitHub API responses identify and pin today's repository/default branch.
Complete local Git histories provide timestamp filtering independent of API order.
No API key or user credentials are used. Existing Part 1 snapshots are read only.
"""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2025-09-30T23:59:59Z"
ACTIVE_SINCE = "2025-04-01T00:00:00Z"
NETID = "dpate172"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def utc_date(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def save_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class PublicGitHub:
    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Do not load implicit .netrc credentials.
        self.session.headers.update({"Accept": "application/vnd.github+json",
                                     "X-GitHub-Api-Version": "2022-11-28",
                                     "User-Agent": "dpate172-Part3-historical-collection"})
        self.last_request = 0.0

    def get(self, url, params=None):
        for attempt in range(4):
            time.sleep(max(0, 1.0 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, params=params, timeout=45)
                if response.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(min(30, max(2 ** (attempt + 1), int(response.headers.get("Retry-After", "0")))))
                    continue
                response.raise_for_status()
                return response
            except (requests.ConnectionError, requests.Timeout):
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
        raise RuntimeError("GitHub request did not complete")


def provenance(response):
    return {"url": response.url, "retrieved_at_utc": utc_now(), "http_status": response.status_code,
            "http_date": response.headers.get("Date"), "etag": response.headers.get("ETag"),
            "redirects": [{"status": item.status_code, "url": item.url,
                           "location": item.headers.get("Location")} for item in response.history]}


def git(repository, *arguments, binary=False):
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    result = subprocess.run(["git", "--git-dir=" + str(repository), *arguments],
                            capture_output=True, timeout=300, env=environment)
    if result.returncode:
        raise RuntimeError(f"Git {' '.join(arguments)} failed: " + result.stderr.decode("utf-8", errors="replace")[-2000:])
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def ensure_history(repository, canonical_url, branch, pinned_head):
    repository.parent.mkdir(parents=True, exist_ok=True)
    if not repository.exists():
        git(repository, "init", "--bare", str(repository))
    if git(repository, "rev-parse", "--is-shallow-repository") == "true":
        raise RuntimeError(f"Refusing an incomplete shallow history: {repository}")
    try:
        git(repository, "rev-parse", "--verify", pinned_head + "^{commit}")
    except RuntimeError:
        # Fetch the exact API-pinned object, rather than a branch that may move.
        git(repository, "-c", "remote.part3.promisor=true", "-c", "remote.part3.partialclonefilter=blob:none",
            "fetch", "--filter=blob:none", "--no-tags", canonical_url + ".git", pinned_head)
    # A traversal failure (e.g. missing parents) must not produce a partial result.
    return git(repository, "rev-list", "--timestamp", pinned_head)


def parse_walk(output):
    return [(int(line.split()[0]), line.split()[1]) for line in output.splitlines() if line]


def parse_commit(repository, sha, canonical_url):
    raw = git(repository, "cat-file", "commit", sha, binary=True)
    framed = b"commit " + str(len(raw)).encode("ascii") + b"\x00" + raw
    assert hashlib.sha1(framed).hexdigest() == sha
    header_bytes, separator, message_bytes = raw.partition(b"\n\n")
    assert separator
    headers = header_bytes.split(b"\n")
    encoding = next((line[9:].decode("ascii") for line in headers if line.startswith(b"encoding ")), "utf-8")

    def decode(value):
        try:
            return value.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            return value.decode("utf-8", errors="replace")

    def identity(kind):
        line = next(line[len(kind) + 1:] for line in headers if line.startswith(kind.encode() + b" "))
        match = re.fullmatch(rb"(.*) <([^<>]*)> (-?\d+) ([+-]\d{4})", line)
        assert match, sha
        epoch = int(match[3])
        return {"name": decode(match[1]), "email": decode(match[2]),
                "identity": decode(match[1] + b" <" + match[2] + b">"),
                "timestamp": epoch, "date_utc": utc_date(epoch), "timezone": match[4].decode("ascii")}

    author, committer = identity("author"), identity("committer")
    return {"commit_sha1": sha, "commit_url": canonical_url + "/commit/" + sha,
            "commit message": decode(message_bytes), "author": author["identity"],
            "author_date": author["date_utc"], "committer_date": committer["date_utc"],
            "author_details": author, "committer": committer,
            "parent_shas": [line[7:].decode("ascii") for line in headers if line.startswith(b"parent ")],
            "git_object_sha1_verified": True, "raw_commit_sha256": hashlib.sha256(raw).hexdigest(),
            "declared_encoding": encoding}


def collect_project(client, assignment, as_of, active_since):
    project = assignment["project_wocid"]
    requested_url = assignment["assigned_github_url"].rstrip("/")
    slug = requested_url.split("github.com/", 1)[1]
    repo_response = client.get("https://api.github.com/repos/" + slug)
    repo = repo_response.json()
    canonical_url, branch = repo["html_url"], repo["default_branch"]
    tip_response = client.get(repo["url"] + "/commits/" + quote(branch, safe=""))
    tip = tip_response.json()
    pinned_head = tip["sha"]
    repository = ROOT / ".cache" / "git" / (project + ".git")
    current_walk = parse_walk(ensure_history(repository, canonical_url, branch, pinned_head))
    cutoff = timestamp(as_of)
    all_eligible = sorted((entry for entry in current_walk if entry[0] <= cutoff), key=lambda item: (-item[0], item[1]))
    first_parent_walk = parse_walk(git(repository, "rev-list", "--first-parent", "--timestamp", pinned_head))
    mainline_eligible = sorted((entry for entry in first_parent_walk if entry[0] <= cutoff), key=lambda item: (-item[0], item[1]))
    if not mainline_eligible:
        raise RuntimeError(f"No first-parent default-branch history exists before cutoff for {project}")
    anchor_timestamp, anchor = mainline_eligible[0]
    historical_walk = parse_walk(git(repository, "rev-list", "--timestamp", anchor))
    eligible = sorted((entry for entry in historical_walk if entry[0] <= cutoff), key=lambda item: (-item[0], item[1]))
    recent = [parse_commit(repository, sha, canonical_url) for _, sha in eligible[:10]]
    assert recent and all(commit["committer"]["timestamp"] <= cutoff for commit in recent)
    assert [commit["committer"]["timestamp"] for commit in recent] == sorted(
        [commit["committer"]["timestamp"] for commit in recent], reverse=True)
    api_response = client.get(repo["url"] + "/commits", params={"sha": pinned_head, "until": as_of, "per_page": 10})
    api_recent = [{"sha": item["sha"], "committer_date_utc": item["commit"]["committer"]["date"],
                   "author_date_utc": item["commit"]["author"]["date"], "url": item["html_url"]}
                  for item in api_response.json()]
    latest = recent[0]
    record = {
        "project_wocid": project, "assigned_github_url": requested_url,
        "canonical_github_url": canonical_url, "canonical_full_name": repo["full_name"],
        "default_branch": branch, "default_branch_observed_now": True,
        "as_of_utc": as_of, "active_since_utc": active_since, "retrieved_at_utc": utc_now(),
        "pinned_current_default_branch_head_sha": pinned_head,
        "pinned_current_head_committer_date_utc": tip["commit"]["committer"]["date"],
        "reconstructed_as_of_mainline_anchor_sha": anchor,
        "reconstructed_as_of_mainline_anchor_committer_date_utc": utc_date(anchor_timestamp),
        "latest_commit_as_of": latest,
        "latest_commit_date": latest["committer_date"],
        "current_status_as_of": "Active" if latest["committer"]["timestamp"] >= timestamp(active_since) else "Inactive",
        "recent_commits": recent,
        "current_default_branch_reachable_commit_count": len(current_walk),
        "reconstructed_anchor_reachable_commit_count": len(historical_walk),
        "eligible_commits_on_reconstructed_history": len(eligible),
        "recent_selection": "All reconstructed-anchor ancestors with committer timestamp <= cutoff, sorted by descending committer timestamp and ascending SHA for ties; first ten.",
        "selection_boundary_timestamp_ties": sum(epoch == recent[-1]["committer"]["timestamp"] for epoch, _ in eligible),
        "current_ancestry_filtered_alternative": {
            "latest_committer_date_utc": utc_date(all_eligible[0][0]), "latest_sha": all_eligible[0][1],
            "top10_shas": [sha for _, sha in all_eligible[:10]],
            "differs_from_reconstructed_history": [sha for _, sha in all_eligible[:10]] != [item["commit_sha1"] for item in recent],
            "note": "Filtering present-day ancestry alone can include old-dated side-branch commits merged after the cutoff. This alternative is recorded but does not select historical recent themes.",
        },
        "github_until_query_for_cross_check": api_recent,
        "sources": {"repository": provenance(repo_response), "pinned_default_branch_tip": provenance(tip_response),
                    "commits_until_query": provenance(api_response),
                    "git_history": {"repository_url": canonical_url + ".git", "local_repository": str(repository.relative_to(ROOT)),
                                    "pinned_sha": pinned_head, "is_shallow": False,
                                    "complete_ancestry_traversal_passed": True}},
        "limitations": [
            "Historical branch membership is reconstructed from the currently observed default branch's first-parent mainline, not a preserved 2025 branch ref or GitHub event log.",
            "Committer timestamps are Git metadata and can be backdated. Complete graph traversal prevents pagination/order mistakes, but cannot independently establish when GitHub received a commit or whether history was rewritten.",
            "The current default branch name may differ from the branch used in 2025; no historical branch-name record is available.",
        ],
        "repository_redirect_detected": canonical_url.lower() != requested_url.lower(),
    }
    if project == "agnwinds_python":
        readme_response = client.get(repo["url"] + "/readme", params={"ref": pinned_head})
        readme = readme_response.json()
        text = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
        matches = [line for line in text.splitlines() if re.search(r"sirocco|renamed|moved|migrat|successor", line, re.I)]
        record["migration_check"] = {"readme_url": readme.get("html_url"), "matching_readme_lines": matches,
                                     "scope": "Assigned legacy repository is retained for status; successor repository activity does not silently replace it."}
        record["sources"]["migration_readme"] = provenance(readme_response)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=AS_OF)
    parser.add_argument("--active-since", default=ACTIVE_SINCE)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    metadata = json.loads((ROOT / "data" / f"{NETID}_github_metadata.json").read_text(encoding="utf-8"))
    output = ROOT / "data" / f"{NETID}_part3_github.json"
    previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() and not args.refresh else {}
    if previous:
        assert previous["as_of_utc"] == args.as_of and previous["active_since_utc"] == args.active_since
    saved = previous.get("projects", {})
    document = {"netid": NETID, "as_of_utc": args.as_of, "active_since_utc": args.active_since,
                "collection_started_at_utc": previous.get("collection_started_at_utc", utc_now()),
                "status_rule": "Active iff the latest eligible commit's committer timestamp is on or after active_since_utc; otherwise Inactive.",
                "historical_reconstruction": "Pin current default branch, find its latest first-parent commit by committer time at/before cutoff, and enumerate that anchor's complete ancestry. Retain committers at/before cutoff and sort globally by committer time (SHA ascending breaks ties).",
                "date_semantics": "Status and recent ordering use committer time. Both original author and committer times and identities are retained.",
                "credentials": "Unauthenticated public GitHub API and public Git history; no API key used.",
                "projects": {}}
    client = PublicGitHub()
    for assignment in metadata["projects"]:
        key = assignment["project_wocid"]
        print(f"Collecting {key}", flush=True)
        record = saved.get(key) or collect_project(client, assignment, args.as_of, args.active_since)
        document["projects"][key] = record
        save_json(output, document)
        print(f"  {record['current_status_as_of']}: {record['latest_commit_as_of']['committer']['date_utc']} "
              f"({len(record['recent_commits'])} recent commits)", flush=True)
    assert len(document["projects"]) == 10
    document["collection_completed_at_utc"] = utc_now()
    save_json(output, document)
    print(f"Saved {output}", flush=True)


if __name__ == "__main__":
    main()

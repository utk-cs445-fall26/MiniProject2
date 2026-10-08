#!/usr/bin/env python3
"""Collect attributable GitHub metadata for a student's assigned repositories.

Usage: python scripts/collect_github_metadata.py --netid dpate172
Requires requests. An optional GITHUB_TOKEN raises GitHub's API rate limit.
Completed records are reused unless --refresh is supplied.
"""

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import parse_qs, urlparse

import requests


ROOT = Path(__file__).resolve().parents[1]


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class GitHubClient:
    def __init__(self, pause=1.0):
        self.pause = pause
        self.last_request = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MP2-educational-metadata-collector",
        })
        if os.environ.get("GITHUB_TOKEN"):
            self.session.headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

    def get(self, url, params=None):
        for attempt in range(4):
            time.sleep(max(0, self.pause - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, params=params, timeout=60)
            except (requests.ConnectionError, requests.Timeout):
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
                continue
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                wait = min(60, max(2 ** (attempt + 1), int(response.headers.get("Retry-After", "0"))))
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response
        raise RuntimeError("Request retry loop ended unexpectedly")


def page_count(response):
    """A per_page=1 endpoint's last page is its item count, not an estimate."""
    if "last" in response.links:
        return int(parse_qs(urlparse(response.links["last"]["url"]).query)["page"][0])
    if "next" in response.links:
        return None  # Do not invent a total if GitHub omits the final page.
    return len(response.json())


def provenance(response):
    return {
        "url": response.url,
        "retrieved_at_utc": utc_now(),
        "http_status": response.status_code,
        "http_date": response.headers.get("Date"),
        "link": response.headers.get("Link"),
        "etag": response.headers.get("ETag"),
    }


def collect_project(client, project):
    requested_url = project["GH"].rstrip("/")
    slug = urlparse(requested_url).path.strip("/")
    repo_response = client.get("https://api.github.com/repos/" + slug)
    repo = repo_response.json()
    commit_response = client.get(repo["url"] + "/commits", params={
        "sha": repo["default_branch"], "per_page": 1,
    })
    commits = commit_response.json()
    tip = commits[0] if commits else None
    record = {
        "project_wocid": project["WoC"],
        "assigned_github_url": requested_url,
        "canonical_github_url": repo["html_url"],
        "canonical_full_name": repo["full_name"],
        "default_branch": repo["default_branch"],
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "last_commit_date": tip["commit"]["committer"]["date"] if tip else None,
        "last_commit_author_date": tip["commit"]["author"]["date"] if tip else None,
        "last_commit_sha": tip["sha"] if tip else None,
        "last_commit_url": tip["html_url"] if tip else None,
        "github_default_branch_commit_count": page_count(commit_response),
        "github_contributor_count_including_anonymous": None,
        "retrieved_at_utc": utc_now(),
        "sources": {
            "repository": provenance(repo_response),
            "default_branch_commits": provenance(commit_response),
        },
        "raw_repository_fields": {
            key: repo.get(key) for key in (
                "id", "full_name", "html_url", "url", "default_branch",
                "stargazers_count", "forks_count", "archived", "disabled", "pushed_at",
            )
        },
        "raw_latest_commit_fields": {
            "sha": tip["sha"], "html_url": tip["html_url"],
            "author": tip["commit"]["author"],
            "committer": tip["commit"]["committer"],
        } if tip else None,
    }
    try:
        contributors = client.get(repo["url"] + "/contributors", params={"anon": "1", "per_page": 1})
        record["github_contributor_count_including_anonymous"] = page_count(contributors)
        record["sources"]["contributors"] = provenance(contributors)
    except requests.RequestException as error:
        # This validation-only endpoint can fail for very large repositories.
        record["contributor_count_error"] = str(error)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--netid", default="dpate172")
    parser.add_argument("--assignments", type=Path, default=ROOT / "net2prj.csv")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    output = args.output or ROOT / "data" / f"{args.netid}_github_metadata.json"
    with args.assignments.open(newline="", encoding="utf-8-sig") as source:
        projects = [row for row in csv.DictReader(source) if row["netID"] == args.netid]
    if not projects:
        raise ValueError(f"No projects assigned to {args.netid}")
    previous = json.loads(output.read_text()) if output.exists() and not args.refresh else {}
    by_project = {record["project_wocid"]: record for record in previous.get("projects", [])}
    payload = {
        "netid": args.netid,
        "collection_started_at_utc": previous.get("collection_started_at_utc", utc_now()),
        "methodology": {
            "stars": "GitHub REST repository stargazers_count.",
            "forks": "GitHub REST repository forks_count.",
            "last_commit_date": "Committer date of the current default-branch tip; not repository pushed_at. Author date is retained separately.",
            "github_default_branch_commit_count": "Number of commits reachable from the current default branch, derived from commits endpoint Link pagination with per_page=1.",
            "github_contributor_count_including_anonymous": "Contributors endpoint pagination with anon=1 and per_page=1. GitHub's cached contributor identities need not equal distinct raw WoC author strings.",
            "comparison_caveat": "Live GitHub default-branch history can differ from the WoC snapshot in date coverage, branch coverage, and identity grouping. Counts are validation context, not a replacement for WoC results.",
        },
        "projects": [],
    }
    client = GitHubClient()
    output.parent.mkdir(parents=True, exist_ok=True)
    for project in projects:
        record = by_project.get(project["WoC"])
        if record is None:
            print(f"Retrieving {project['WoC']}", flush=True)
            record = collect_project(client, project)
        payload["projects"].append(record)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        print(f"  stars={record['stars']}; forks={record['forks']}; "
              f"last_commit={record['last_commit_date']}; "
              f"default_branch_commits={record['github_default_branch_commit_count']}; "
              f"contributors={record['github_contributor_count_including_anonymous']}", flush=True)
    payload["collection_completed_at_utc"] = utc_now()
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Saved {len(payload['projects'])} projects to {output}")


if __name__ == "__main__":
    main()

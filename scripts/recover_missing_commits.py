#!/usr/bin/env python3
"""Recover explicitly missing WoC commit objects from assigned Git repositories.

WoC p2c membership remains authoritative. This script only obtains object contents
for hashes reported missing by WoC; it never substitutes Git branch membership or
writes to the active WoC object cache. Git object hashes are verified from bytes.

Examples:
  python scripts/recover_missing_commits.py --probe COMMIT_SHA1
  python scripts/recover_missing_commits.py --recover data/dpate172_woc_missing.json
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SHA1 = re.compile(r"[0-9a-f]{40}\Z")


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def save_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_manifest(path, manifest):
    manifest["recovered_unique_commits"] = len(manifest["recovered"])
    manifest["missing_unique_commits"] = len(manifest["unresolved"])
    manifest["excluded_noncommit_count"] = len(manifest.get("excluded_noncommit_objects", {}))
    repositories = {}
    for evidence in manifest["recovered"].values():
        project = evidence["source_project"]
        item = repositories.setdefault(project, {"source_url": evidence["source_url"],
                                                "recovered_unique_commits": 0})
        item["recovered_unique_commits"] += 1
    manifest["repositories"] = repositories
    save_json(path, manifest)


def read_jsonl(path):
    """Read a concurrent cache without modifying a possibly partial final line."""
    records = {}
    if path.exists():
        # Split bytes only on literal LF: Unicode line separators can occur in
        # JSON strings. A concurrent append may leave an incomplete UTF-8 tail.
        lines = path.read_bytes().split(b"\n")
        if lines and not lines[-1]:
            lines.pop()
        for index, line in enumerate(lines):
            try:
                record = json.loads(line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                if index == len(lines) - 1:
                    break
                raise
            records[record["commit_sha1"]] = record
    return records


def git(*args, timeout=600):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    result = subprocess.run(["git", *map(str, args)], capture_output=True, env=env, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace").strip()[-2000:])
    return result.stdout


def ensure_repository(project, url):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", project):
        raise ValueError("Invalid project identifier")
    repository = ROOT / ".cache" / "git" / (project + ".git")
    repository.parent.mkdir(parents=True, exist_ok=True)
    if not repository.exists():
        print(f"Cloning commit history: {url}", flush=True)
        git("clone", "--bare", "--filter=blob:none", url, repository)
    remote = git("--git-dir", repository, "remote", "get-url", "origin").decode().strip()
    if remote.rstrip("/") != url.rstrip("/"):
        raise ValueError(f"Unexpected cached Git origin for {project}: {remote}")
    return repository


def read_object(repository, sha):
    """Read the exact object, without cat-file's implicit annotated-tag peeling."""
    try:
        object_type = git("--git-dir", repository, "cat-file", "-t", sha, timeout=120).decode().strip()
    except RuntimeError:
        # An unreachable object may not be in the clone's advertised refs.
        git("--git-dir", repository, "fetch", "--no-tags", "--filter=blob:none", "origin", sha)
        object_type = git("--git-dir", repository, "cat-file", "-t", sha, timeout=120).decode().strip()
    raw = git("--git-dir", repository, "cat-file", object_type, sha, timeout=120)
    actual = hashlib.sha1(object_type.encode("ascii") + b" " + str(len(raw)).encode("ascii")
                          + b"\0" + raw).hexdigest()
    if actual != sha:
        raise ValueError(f"Git object integrity failure: requested {sha}, computed {actual}")
    return object_type, raw


def tag_details(repository, sha, raw, owners, memberships, max_depth=32):
    """Verify each exact tag in a bounded chain ending at an existing WoC commit."""
    visited = set()
    chain = []
    raw_tags = []
    current_sha, current_raw = sha, raw
    for _ in range(max_depth):
        if current_sha in visited:
            raise ValueError(f"Cycle in annotated tag chain at {current_sha}")
        visited.add(current_sha)
        actual = hashlib.sha1(b"tag " + str(len(current_raw)).encode("ascii")
                              + b"\0" + current_raw).hexdigest()
        if actual != current_sha:
            raise ValueError(f"Git tag integrity failure: requested {current_sha}, computed {actual}")
        headers = {}
        for line in current_raw.partition(b"\n\n")[0].split(b"\n"):
            key, _, value = line.partition(b" ")
            headers[key] = value
        target = headers[b"object"].decode("ascii")
        declared_type = headers[b"type"].decode("ascii")
        if not SHA1.fullmatch(target) or declared_type not in ("tag", "commit"):
            raise ValueError("Annotated tag must target a valid commit or tag SHA1")
        if target in visited:
            raise ValueError(f"Cycle in annotated tag chain at {target}")
        archive = ROOT / ".cache" / "git" / "raw-commits" / (current_sha + ".tag")
        chain.append({"sha1": current_sha, "object_type": "tag",
                      "direct_target_sha1": target, "direct_target_type": declared_type,
                      "tag_name": headers.get(b"tag", b"").decode("utf-8", "replace"),
                      "git_object_sha1_verified": True, "raw_object_bytes": len(current_raw),
                      "raw_object_path": str(archive.relative_to(ROOT)),
                      "raw_sha256": hashlib.sha256(current_raw).hexdigest()})
        raw_tags.append((archive, current_raw))
        actual_type, target_raw = read_object(repository, target)
        if actual_type != declared_type:
            raise ValueError(f"Tag declares target {target} as {declared_type}, actually {actual_type}")
        if actual_type == "commit":
            absent = [project for project in owners if target not in memberships[project]]
            if absent:
                raise ValueError(f"Verified tag targets commit {target}, absent from WoC membership for {absent}")
            for archive, tag_raw in raw_tags:
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_bytes(tag_raw)
            details = {"target_commit_sha1": target,
                       "target_commit_in_each_woc_project": True,
                       "tag_name": chain[0]["tag_name"]}
            if len(chain) > 1:
                details.update({"direct_target_sha1": chain[0]["direct_target_sha1"],
                                "direct_target_type": chain[0]["direct_target_type"],
                                "tag_chain": chain})
            return details
        current_sha, current_raw = target, target_raw
    raise ValueError(f"Annotated tag chain exceeds maximum depth {max_depth}")


def decode_bytes(value, declared):
    """Honor Git encoding headers; record every fallback instead of dropping bytes."""
    candidates = list(dict.fromkeys([declared, "utf-8", "latin-1"]))
    for encoding in candidates:
        try:
            return value.decode(encoding), encoding
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("Unable to decode commit bytes")


def parse_commit(sha, raw):
    actual = hashlib.sha1(b"commit " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != sha:
        raise ValueError(f"Git object integrity failure: requested {sha}, computed {actual}")
    headers, separator, message = raw.partition(b"\n\n")
    if not separator:
        raise ValueError("Commit has no header/message separator")
    values = {}
    for line in headers.split(b"\n"):
        if line.startswith(b" "):
            continue  # Continuation of a signature or another multiline header.
        key, _, value = line.partition(b" ")
        values.setdefault(key, []).append(value)
    authors = values.get(b"author", [])
    if len(authors) != 1:
        raise ValueError("Commit must have exactly one author header")
    match = re.fullmatch(rb"(.* <.*>) (-?\d+) ([+-]\d{4})", authors[0])
    if match is None:
        raise ValueError("Invalid Git author identity/timestamp header")
    declared = values.get(b"encoding", [b"utf-8"])[0].decode("ascii", "strict")
    author, author_encoding = decode_bytes(match.group(1), declared)
    message, message_encoding = decode_bytes(message, declared)
    record = {"commit_sha1": sha, "author": author, "time": int(match.group(2)),
              "commit message": message}
    evidence = {"git_object_sha1_verified": True, "raw_commit_bytes": len(raw),
                "raw_commit_sha256": hashlib.sha256(raw).hexdigest(),
                "declared_encoding": declared, "author_decoding": author_encoding,
                "message_decoding": message_encoding,
                "author_timezone": match.group(3).decode("ascii")}
    return record, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--netid", default="dpate172")
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--probe", help="One known missing hash; never scans for other missing objects")
    operation.add_argument("--recover", type=Path, help="JSON mapping of explicitly reported SHA1:error entries")
    args = parser.parse_args()
    data = ROOT / "data"
    memberships_path = data / f"{args.netid}_woc_project_commits.json"
    memberships = json.loads(memberships_path.read_text(encoding="utf-8"))["projects"]
    with (ROOT / "net2prj.csv").open(newline="", encoding="utf-8-sig") as handle:
        projects = {row["WoC"]: row["GH"].rstrip("/") for row in csv.DictReader(handle)
                    if row["netID"] == args.netid}
    if args.probe:
        errors = {args.probe: "Explicit known-missing object probe; see WoC lookup evidence."}
    else:
        errors = json.loads(args.recover.read_text(encoding="utf-8"))
    if not isinstance(errors, dict) or any(not SHA1.fullmatch(sha) for sha in errors):
        raise ValueError("Recovery input must be a mapping from 40-character SHA1 to WoC error")
    owners = {}
    for project, hashes in memberships.items():
        for sha in set(errors).intersection(hashes):
            owners.setdefault(sha, []).append(project)
    if set(errors) - set(owners):
        raise ValueError("Refusing to recover a hash outside the saved WoC project memberships")

    woc_records = read_jsonl(data / f"{args.netid}_woc_commits.jsonl")
    recovered_path = data / f"{args.netid}_git_recovered_commits.jsonl"
    recovered = read_jsonl(recovered_path)
    manifest_path = data / f"{args.netid}_git_recovery.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "netid": args.netid,
        "methodology": "WoC p2c defines project membership. Only WoC-missing object contents are recovered "
                       "from the assigned original Git repositories. Git SHA1 is recomputed from the exact "
                       "raw object bytes before parsing author identity, author timestamp, and message. "
                       "No Git branch membership substitutes for WoC membership.",
        "recovered": {}, "unresolved": {},
    }
    manifest.setdefault("excluded_noncommit_objects", {})
    manifest["noncommit_methodology"] = (
        "Some WoC p2c entries are annotated Git tags. Exact object type and SHA1 are verified. "
        "Tags are excluded from commit rows only when their target commits are already listed "
        "separately in every corresponding project's saved p2c membership. Raw tag bytes are retained."
    )
    manifest["last_run_utc"] = utc_now()
    manifest["membership_source"] = str(memberships_path.relative_to(ROOT))
    manifest["membership_source_sha256"] = hashlib.sha256(memberships_path.read_bytes()).hexdigest()
    manifest["last_requested_count"] = len(errors)
    skipped = 0
    for index, sha in enumerate(sorted(errors), 1):
        if sha in woc_records:
            skipped += 1
            manifest["unresolved"].pop(sha, None)
            continue
        if sha in recovered and sha in manifest["recovered"]:
            manifest["recovered"][sha]["woc_error"] = errors[sha]
            manifest["unresolved"].pop(sha, None)
            continue
        if sha in manifest["excluded_noncommit_objects"]:
            manifest["excluded_noncommit_objects"][sha]["woc_error"] = errors[sha]
            manifest["unresolved"].pop(sha, None)
            continue
        failures = {}
        for project in owners[sha]:
            try:
                url = projects[project]
                repository = ensure_repository(project, url)
                object_type, raw = read_object(repository, sha)
                if object_type == "commit":
                    record, evidence = parse_commit(sha, raw)
                elif object_type == "tag":
                    evidence = tag_details(repository, sha, raw, owners[sha], memberships)
                else:
                    raise ValueError(f"WoC p2c entry is verified Git object type {object_type}; manual review required")
                archive = ROOT / ".cache" / "git" / "raw-commits" / (sha + "." + object_type)
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_bytes(raw)
                source_evidence = {
                    "source_project": project, "source_url": url,
                    "woc_projects": owners[sha], "woc_error": errors[sha],
                    "retrieved_at_utc": utc_now(), **evidence,
                }
                if object_type == "commit":
                    recovered[sha] = record
                    manifest["recovered"][sha] = {
                        **source_evidence, "raw_commit_path": str(archive.relative_to(ROOT)),
                    }
                else:
                    manifest["excluded_noncommit_objects"][sha] = {
                        **source_evidence, "object_type": object_type,
                        "git_object_sha1_verified": True, "raw_object_bytes": len(raw),
                        "raw_object_path": str(archive.relative_to(ROOT)),
                        "raw_sha256": hashlib.sha256(raw).hexdigest(),
                    }
                manifest["unresolved"].pop(sha, None)
                break
            except (RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired, OSError) as error:
                failures[project] = str(error)
        else:
            manifest["unresolved"][sha] = {"woc_error": errors[sha], "git_errors": failures}
        # These files are separate from the active WoC cache and safe to resume.
        temporary = recovered_path.with_suffix(".jsonl.tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            for key in sorted(recovered):
                handle.write(json.dumps(recovered[key], ensure_ascii=False) + "\n")
        temporary.replace(recovered_path)
        save_manifest(manifest_path, manifest)
        if index % 100 == 0 or index == len(errors):
            print(f"Processed {index}/{len(errors)} requested; recovered {len(recovered)}, "
                  f"verified noncommits {len(manifest['excluded_noncommit_objects'])}, "
                  f"unresolved {len(manifest['unresolved'])}", flush=True)
    save_manifest(manifest_path, manifest)
    print(json.dumps({"requested": len(errors), "already_in_woc_cache": skipped,
                      "recovered_total": len(recovered),
                      "excluded_noncommit_count": manifest["excluded_noncommit_count"],
                      "unresolved_total": len(manifest["unresolved"])}))
    return 1 if any(sha in manifest["unresolved"] for sha in errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())

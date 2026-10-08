"""Package only verified recovery evidence for offline notebook validation."""

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = DATA / "dpate172_git_recovery.json"
OUTPUT = DATA / "dpate172_git_objects.zip"


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    temporary = OUTPUT.with_suffix(".zip.tmp")
    written = {}
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        def add_object(sha, object_type, evidence, path_key, digest_key):
            assert evidence["git_object_sha1_verified"] is True
            raw = (ROOT / evidence[path_key]).read_bytes()
            framed = object_type.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw
            assert hashlib.sha1(framed).hexdigest() == sha
            assert hashlib.sha256(raw).hexdigest() == evidence[digest_key]
            member = f"{sha}.{object_type}"
            if member in written:
                assert written[member] == raw
            else:
                info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, raw)
                written[member] = raw
            evidence["archive_member"] = member

        for category, object_type, path_key, digest_key in [
            ("recovered", "commit", "raw_commit_path", "raw_commit_sha256"),
            ("excluded_noncommit_objects", "tag", "raw_object_path", "raw_sha256"),
        ]:
            for sha, evidence in sorted(manifest.get(category, {}).items()):
                add_object(sha, object_type, evidence, path_key, digest_key)
                # Auxiliary tags prove the chain but are not dataset rows or exclusions.
                for tag in evidence.get("tag_chain", []):
                    assert tag["object_type"] == "tag"
                    add_object(tag["sha1"], "tag", tag, "raw_object_path", "raw_sha256")
    temporary.replace(OUTPUT)
    manifest["raw_object_archive"] = str(OUTPUT.relative_to(ROOT))
    manifest["raw_object_archive_sha256"] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest_tmp = MANIFEST.with_suffix(".json.tmp")
    manifest_tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_tmp.replace(MANIFEST)
    print(f"Verified and packaged {len(written)} raw Git objects in {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

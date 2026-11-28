"""Publish a new IMMUTABLE GitHub Release for PvZ Hybrid Classic.

Enforces the project's traceable build-versioning rule:
- Every build has an explicit BuildID `B.X.Y` (e.g., `B.0.2`).
- Every build gets its own dedicated GitHub Release tag `v<GameVersion>-<BuildID>`.
- NEVER overwrites an existing GitHub Release or tag.
- Verifies all 3 signed APKs exist and match `build_version.json` SHA-256 before uploading.

Usage:
    python scripts/publish_release.py --build B.0.2 --notes path/to/RELEASE_NOTES-3.20.1-B.0.2.md
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")
BUILD_VERSION_FILE = os.path.join(ROOT, "build_version.json")
BUILD_ID_RE = re.compile(r"^B\.\d+\.\d+$")
OFFICIAL_CREDIT_URLS = (
    "space.bilibili.com/",
    "pvzhe.com",
)
NON_COMMERCIAL_CUES = (
    "non-commercial",
    "phi thương mại",
    "非商业",
    "非营利",
)


def validate_credits(notes_path: str) -> None:
    text = open(notes_path, "r", encoding="utf-8").read()
    low = text.lower()
    missing = []
    if "CREDITS.md" not in text:
        missing.append("direct link to CREDITS.md")
    if not any(u in text for u in OFFICIAL_CREDIT_URLS):
        missing.append("official upstream creator URL (space.bilibili.com / pvzhe.com)")
    if not (("electronic arts" in low or "ea" in low) and "popcap" in low):
        missing.append("Electronic Arts Inc. (EA) / PopCap Games trademark notice")
    if not any(cue in low for cue in NON_COMMERCIAL_CUES):
        missing.append("non-commercial / free fan-project disclaimer")
    if missing:
        raise SystemExit(
            f"REFUSED: Release notes '{notes_path}' failed mandatory credits/copyright check!\n"
            f"Missing: {', '.join(missing)}"
        )


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    meta = json.load(open(BUILD_VERSION_FILE, encoding="utf-8"))
    ap = argparse.ArgumentParser(description="Create a new immutable GitHub Release for a PvZ Hybrid Classic build")
    ap.add_argument("--build", default=meta["current_build"], help="Build ID (e.g. B.0.2)")
    ap.add_argument("--notes", required=True, help="Path to Markdown release notes file")
    ap.add_argument("--title", default="", help="Optional custom GitHub Release title")
    ap.add_argument("--target", default="main", help="Git branch/commit target for new tag (default: main)")
    ap.add_argument("--dry-run", action="store_true", help="Validate everything without publishing")
    args = ap.parse_args()

    build_id = args.build.strip()
    if not BUILD_ID_RE.match(build_id):
        raise SystemExit(f"Invalid build ID '{build_id}': expected B.X.Y")

    repo = meta["github_repo"]
    game_name = meta["game_name"]
    game_ver = meta["game_version"]
    tag = f"v{game_ver}-{build_id}"
    title = args.title or f"PvZ Hybrid Classic v{game_ver} (Build {build_id}) — Standalone Android Suite ([EN] / [VI] / [CN])"

    if not os.path.isfile(args.notes):
        raise SystemExit(f"Missing release notes file: {args.notes}")

    validate_credits(args.notes)

    # HARD IMMUTABILITY CHECK: refuse to overwrite an existing GitHub Release!
    chk = subprocess.run(
        ["gh", "api", f"repos/{repo}/releases/tags/{tag}"],
        capture_output=True, text=True,
    )
    if chk.returncode == 0:
        raise SystemExit(
            f"REFUSED: GitHub Release '{tag}' already exists in {repo}!\n"
            f"Never overwrite an existing release. Bump build_version.json (e.g. next B.X.Y) instead."
        )

    rec = next((h for h in meta.get("history", []) if h.get("build_id") == build_id), None)
    assets = []
    for lang_key, label in [("vi", "Vietnamese"), ("en", "English"), ("cn", "Chinese-Raw")]:
        fname = f"{game_name}-{game_ver}-{label}-{build_id}.apk"
        fpath = os.path.join(OUTPUT, fname)
        if not os.path.isfile(fpath):
            raise SystemExit(f"Missing signed APK: {fpath}")
        actual_sha = sha256_file(fpath)
        actual_sz = os.path.getsize(fpath)
        if rec and lang_key in rec.get("assets", {}):
            exp_sha = rec["assets"][lang_key]["sha256"]
            if actual_sha != exp_sha:
                raise SystemExit(f"SHA-256 mismatch for {fname}: disk={actual_sha} vs manifest={exp_sha}")
        print(f"[OK] {fname} ({actual_sz:,} B) sha256={actual_sha}")
        assets.append(fpath)

    cmd = [
        "gh", "release", "create", tag,
        *assets,
        "--repo", repo,
        "--target", args.target,
        "--title", title,
        "--notes-file", args.notes,
        "--latest",
    ]
    print("\nCommand:", " ".join(cmd))
    if args.dry_run:
        print("DRY RUN complete — nothing published.")
        return

    subprocess.run(cmd, check=True)
    print(f"\nPublished immutable release {tag} on https://github.com/{repo}/releases/tag/{tag}")


if __name__ == "__main__":
    main()

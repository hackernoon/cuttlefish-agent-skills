#!/usr/bin/env python3
"""Sync the repo's source lists from the Cuttlefish skills DB.

Reads every skill in the SKILL.md Library (the Mongo `skills` collection, or a
CSV export of it) and writes:

  scripts/sources.json  one entry per upstream repo (hand-tuned fields on
                        existing entries such as exclude/default_category are kept)
  scripts/skills.json   one entry per redistributable skill: skill_id, repo,
                        path, file, category, license. build.py builds exactly
                        these skills when this file exists.
  LIBRARY_TOTAL         rewritten at the top of scripts/build.py

Only metadata is written. Skill bodies and stats from the DB never enter this repo.

Usage:
  python3 scripts/sync_sources.py --csv ../hn-skills-next/data/skills-database.csv
  python3 scripts/sync_sources.py --mongo-uri "$MONGO_URI" [--db NAME]   # needs pymongo
  add --dry-run to print the summary without writing anything
"""
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "scripts" / "sources.json"
MANIFEST = ROOT / "scripts" / "skills.json"
BUILD = ROOT / "scripts" / "build.py"

# DB license values that allow redistribution. Anything else stays out of the repo.
OK_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSD", "CC-BY-4.0"}
# Repos in the DB that are deliberately not synced, with the reason.
EXCLUDE_REPOS = {
    "hackernoon/pixel-icon-library": "already shipped by hand in plugins/hackernoon-originals",
}
# DB category (as shown on hackernoon.com) -> plugin folder in this repo.
CATEGORY_SLUGS = {
    "Dev Workflow": "dev-workflow", "Writing & Blogging": "writing-blogging",
    "Design & UI": "design-ui", "Marketing & SEO": "marketing-seo",
    "QA & Testing": "qa-testing", "Security": "security",
    "Data & Science": "data-science", "Learn Tech": "learn-tech",
}
FIELDS = ("skill_id", "name", "author_name", "category", "license", "republish",
          "raw_md_url", "install_repo")
RAW_URL = re.compile(r"^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)$")


def load_csv(path):
    csv.field_size_limit(sys.maxsize)
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: row.get(k, "") for k in FIELDS} for row in csv.DictReader(f)]


def load_mongo(uri, db_name, collection):
    try:
        from pymongo import MongoClient
    except ImportError:
        sys.exit("pymongo is not installed: pip install pymongo")
    client = MongoClient(uri)
    db = client[db_name] if db_name else client.get_default_database()
    proj = {k: 1 for k in FIELDS} | {"_id": 0}
    rows = [{k: (doc.get(k) or "") for k in FIELDS} for doc in db[collection].find({}, proj)]
    client.close()
    return rows


def unique_slug(base, taken):
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "src"
    out, i = slug, 2
    while out in taken:
        out, i = f"{slug}-{i}", i + 1
    taken.add(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", help="CSV export of the skills collection")
    src.add_argument("--mongo-uri", help="Mongo connection string (read-only user is enough)")
    ap.add_argument("--db", help="Mongo database name (default: the one in the URI)")
    ap.add_argument("--collection", default="skills")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = load_csv(args.csv) if args.csv else load_mongo(args.mongo_uri, args.db, args.collection)
    if not rows:
        sys.exit("no skills found in the source; refusing to overwrite anything")
    library_total = len(rows)

    manifest, excluded = [], []
    for r in rows:
        sid, repo = r["skill_id"].strip(), r["install_repo"].strip()
        m = RAW_URL.match(r["raw_md_url"].strip())

        def drop(reason):
            excluded.append({"skill_id": sid, "repo": repo, "reason": reason})

        if not sid or not repo:
            drop("missing skill_id or install_repo"); continue
        if repo.lower() in EXCLUDE_REPOS:
            drop(EXCLUDE_REPOS[repo.lower()]); continue
        if r["license"] not in OK_LICENSES or r["republish"] not in ("full", ""):
            drop(f"license not redistributable ({r['license'] or 'none'})"); continue
        if not m or f"{m.group(1)}/{m.group(2)}".lower() != repo.lower():
            drop(f"raw_md_url does not point into {repo}"); continue
        rel = m.group(4)
        path, _, fname = rel.rpartition("/")
        manifest.append({
            "skill_id": sid,
            "name": r["name"],
            "repo": repo,
            "ref": m.group(3),
            "path": path,
            "file": fname,
            "category": CATEGORY_SLUGS.get(r["category"], ""),
            "license": r["license"],
        })

    dup = [k for k, v in Counter(s["skill_id"] for s in manifest).items() if v > 1]
    if dup:
        sys.exit(f"duplicate skill_id in source, fix the DB first: {dup[:10]}")
    manifest.sort(key=lambda s: (s["repo"].lower(), s["path"], s["file"]))

    # sources.json: keep existing entries (and their hand-tuned fields), add new repos.
    existing = json.loads(SOURCES.read_text()) if SOURCES.exists() else []
    by_repo = {s["repo"].lower(): s for s in existing}
    taken = {s["slug"] for s in existing}
    authors = defaultdict(Counter)
    for r in rows:
        if r["author_name"]:
            authors[r["install_repo"].strip().lower()][r["author_name"].strip()] += 1
    repo_names = {}
    for s in manifest:
        repo_names.setdefault(s["repo"].lower(), s["repo"])

    sources, added = [], []
    for key, repo in repo_names.items():
        if key in by_repo:
            sources.append(by_repo[key]); continue
        author = authors[key].most_common(1)[0][0] if authors[key] else repo.split("/")[0]
        entry = {"repo": repo, "author": author, "slug": unique_slug(repo.split("/")[0], taken)}
        sources.append(entry); added.append(repo)
    # Repos that were in sources.json but have no redistributable skills in the DB any more.
    dropped = [s["repo"] for s in existing if s["repo"].lower() not in repo_names]
    # Keep the original order for existing repos, then new repos by skill count.
    count = Counter(s["repo"].lower() for s in manifest)
    order = {s["repo"].lower(): i for i, s in enumerate(existing)}
    sources.sort(key=lambda s: (order.get(s["repo"].lower(), len(order)), -count[s["repo"].lower()], s["repo"].lower()))

    reasons = Counter(e["reason"] for e in excluded)
    print(json.dumps({
        "library_total": library_total,
        "skills_to_build": len(manifest),
        "repos": len(sources),
        "new_repos": added,
        "repos_no_longer_in_db": dropped,
        "excluded": dict(reasons),
        "excluded_skills": [f"{e['repo']} {e['skill_id']}" for e in excluded],
        "uncategorized": [s["skill_id"] for s in manifest if not s["category"]],
    }, indent=1))
    if dropped:
        print(f"note: {len(dropped)} repo(s) removed from sources.json, see repos_no_longer_in_db", file=sys.stderr)
    if args.dry_run:
        print("dry run: nothing written", file=sys.stderr); return

    lines = ",\n".join("  " + json.dumps(s, ensure_ascii=False) for s in sources)
    SOURCES.write_text("[\n" + lines + "\n]\n")
    lines = ",\n".join(" " + json.dumps(s, ensure_ascii=False) for s in manifest)
    MANIFEST.write_text("[\n" + lines + "\n]\n")
    build = BUILD.read_text()
    new_build, n = re.subn(r"^LIBRARY_TOTAL = \d+", f"LIBRARY_TOTAL = {library_total}", build, count=1, flags=re.M)
    if n != 1:
        sys.exit("LIBRARY_TOTAL line not found in scripts/build.py")
    BUILD.write_text(new_build)
    print(f"wrote {SOURCES.relative_to(ROOT)}, {MANIFEST.relative_to(ROOT)}, LIBRARY_TOTAL={library_total}", file=sys.stderr)


if __name__ == "__main__":
    main()

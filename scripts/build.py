#!/usr/bin/env python3
"""Build the HackerNoon SKILL.md marketplace (Project Cuttlefish.MD).

Clones each upstream repo listed in scripts/sources.json, keeps only skills whose
license allows redistribution (MIT / Apache-2.0 / BSD / CC-BY), copies each skill
folder with its license and an ATTRIBUTION.md, sorts skills into category
plugins, and writes .claude-plugin/marketplace.json plus catalog.json.

When scripts/skills.json exists (written by scripts/sync_sources.py from the
Cuttlefish DB), only the skills listed there are built, with the DB's category.
Without it, every SKILL.md in each repo is built and categorized by keyword.

Usage:  python3 scripts/build.py [--cache DIR] [--refresh]
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

# Skills in the full library at hackernoon.com. Shown in the README; sync_sources.py updates it.
LIBRARY_TOTAL = 2908

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
OK_LICENSES = [("MIT License", "MIT"), ("Apache License", "Apache-2.0"),
               ("BSD", "BSD"), ("Attribution 4.0", "CC-BY-4.0")]
BLOCK = ["All rights reserved", "Proprietary"]

CATEGORIES = {
    "dev-workflow":      ("Dev Workflow", "Planning, debugging, code review, git, agents and everyday engineering workflow skills."),
    "writing-blogging":  ("Writing & Blogging", "Skills for drafting, structuring and editing blog posts, docs and research writing."),
    "design-ui":         ("Design & UI", "Frontend design, brand, canvas and visual-output skills."),
    "marketing-seo":     ("Marketing & SEO", "Copywriting, SEO audits, pricing, launch and growth skills."),
    "qa-testing":        ("QA & Testing", "TDD, browser automation, QA and test-writing skills."),
    "security":          ("Security", "Security audits, secure coding and vulnerability-review skills."),
    "data-science":      ("Data & Science", "Data analysis, scientific computing and bioinformatics skills (genomics, proteomics, single-cell and more)."),
    "learn-tech":        ("Learn Tech", "Skills that teach: tutorials, exercises and learning loops."),
}
KEYWORDS = {  # whole-word stems; name hits count 3x, description hits 1x
    "security":         ["security", "secure", "vulnerability", "vulnerabilities", "owasp", "pentest", "threat", "exploit", "cve", "vibesec", "secrets"],
    "qa-testing":       ["test", "tests", "testing", "tdd", "qa", "playwright", "e2e", "browser", "coverage", "webapp-testing"],
    "marketing-seo":    ["seo", "marketing", "copywriting", "copy", "pricing", "launch", "growth", "ads", "outreach", "gtm", "sales", "sdr", "leads", "lead", "cro", "icp", "positioning", "retention", "funnel", "email", "newsletter"],
    "writing-blogging": ["writing", "write", "blog", "article", "prose", "essay", "editing", "beats", "fragments", "shape", "comms", "docs", "documentation", "paper"],
    "design-ui":        ["design", "ui", "ux", "frontend", "css", "canvas", "art", "theme", "brand", "icon", "icons", "figma", "gif", "visual", "accessibility"],
    "learn-tech":       ["teach", "learn", "learning", "tutor", "exercise", "exercises", "course", "academy"],
    "data-science":     ["data", "analytics", "sql", "pandas", "notebook", "statistics", "science", "scientific", "dataset"],
}
OVERRIDES = {  # categories as shown on hackernoon.com/skills
    "frontend-design": "design-ui", "skill-creator": "dev-workflow", "mcp-builder": "dev-workflow",
    "brand-guidelines": "design-ui", "writing-plans": "dev-workflow", "executing-plans": "dev-workflow",
    "using-git-worktrees": "dev-workflow", "using-superpowers": "dev-workflow", "dispatching-parallel-agents": "dev-workflow",
    "systematic-debugging": "dev-workflow", "finishing-a-development-branch": "dev-workflow", "diagnosing-superpowers": "dev-workflow",
    "writing-skills": "writing-blogging", "writing-shape": "writing-blogging", "writing-beats": "writing-blogging",
    "writing-fragments": "writing-blogging", "wizard": "dev-workflow", "triage": "dev-workflow", "implement": "dev-workflow",
    "prototype": "dev-workflow", "improve-codebase-architecture": "dev-workflow", "setup-pre-commit": "dev-workflow",
    "migrate-to-shoehorn": "dev-workflow", "to-spec": "dev-workflow", "to-tickets": "dev-workflow", "qa": "qa-testing",
    "tdd": "qa-testing", "test-driven-development": "qa-testing", "learning-opportunities": "learn-tech", "teach": "learn-tech",
    "ai-pricing": "marketing-seo", "web-quality-audit": "dev-workflow", "algorithmic-art": "design-ui",
    "canvas-design": "design-ui", "internal-comms": "writing-blogging", "webapp-testing": "qa-testing",
}


def sh(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def read_license(path: Path):
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "COPYING"):
        f = path / name
        if f.is_file():
            return f, f.read_text(errors="ignore")[:4000]
    return None, ""


def classify_license(text):
    if not text or any(b.lower() in text.lower() for b in BLOCK):
        return None
    for needle, spdx in OK_LICENSES:
        if needle.lower() in text.lower():
            return spdx
    return None


def frontmatter(md: str):
    m = re.match(r"^---\s*\n(.*?)\n---", md, re.S)
    if not m:
        return {}
    try:
        import yaml
        fm = yaml.safe_load(m.group(1)) or {}
        return {k: (" ".join(str(v).split()) if isinstance(v, str) else v) for k, v in fm.items()} if isinstance(fm, dict) else {}
    except Exception:
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm


def categorize(src, name, desc):
    if src.get("category"):
        return src["category"]
    if name in OVERRIDES:
        return OVERRIDES[name]
    name_words = set(re.split(r"[^a-z0-9]+", name.lower()))
    desc_words = re.findall(r"[a-z0-9]+", desc.lower())
    scores = {}
    for cat, words in KEYWORDS.items():
        s = 3 * len(name_words & set(words)) + sum(1 for w in desc_words if w in words)
        if s:
            scores[cat] = s
    if scores:
        best, s = max(scores.items(), key=lambda kv: kv[1])
        if s >= 3:
            return best
    return src.get("default_category", "dev-workflow")


def find_skills(local, src):
    """Every SKILL.md in a repo, for sources without DB manifest entries."""
    out = []
    for skill_md in sorted(local.rglob("SKILL.md")):
        sdir = skill_md.parent
        rel = sdir.relative_to(local).as_posix()
        if any(p.startswith(".") or p in ("node_modules", "test", "tests", "examples", "templates")
               for p in sdir.relative_to(local).parts):
            continue
        if any(rel.startswith(x) for x in src.get("exclude", [])):
            continue
        out.append({"path": "" if rel == "." else rel, "file": "SKILL.md"})
    return out


def clone(repo, local, refresh):
    if local.exists() and refresh:
        print(f"updating {repo}", file=sys.stderr)
        sh("git", "fetch", "-q", "--depth", "1", "origin", "HEAD", cwd=local)
        sh("git", "reset", "-q", "--hard", "FETCH_HEAD", cwd=local)
    elif not local.exists():
        print(f"cloning {repo}", file=sys.stderr)
        sh("git", "clone", "-q", "--depth", "1", f"https://github.com/{repo}.git", str(local))


def find_skill_file(sdir):
    """Actual on-disk name of the skill file (SKILL.md, or SKILL.MD etc. upstream), or None."""
    if not sdir.is_dir():
        return None
    return next((n for n in sorted(os.listdir(sdir)) if n.upper() == "SKILL.MD" and (sdir / n).is_file()), None)


def copy_skill(sdir, dest, nested):
    """Copy a skill folder, leaving out .git/node_modules and any nested folder that is
    its own skill (those are copied separately, so they are not duplicated)."""
    base = shutil.ignore_patterns(".git", "node_modules", "*.pyc", "__pycache__", ".DS_Store")

    def ignore(d, names):
        skip = set(base(d, names))
        skip |= {n for n in names if (Path(d) / n).resolve() in nested}
        return skip

    shutil.copytree(sdir, dest, ignore=ignore)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(ROOT / ".cache"))
    ap.add_argument("--refresh", action="store_true", help="pull the latest commit of repos already in the cache")
    args = ap.parse_args()
    cache = Path(args.cache); cache.mkdir(parents=True, exist_ok=True)
    sources = json.loads((ROOT / "scripts" / "sources.json").read_text())
    manifest_file = ROOT / "scripts" / "skills.json"
    manifest = json.loads(manifest_file.read_text()) if manifest_file.exists() else None
    by_repo = {}
    for s in manifest or []:
        by_repo.setdefault(s["repo"].lower(), []).append(s)

    # wipe generated category plugins (keep hand-written ones like hackernoon-originals)
    for cat in CATEGORIES:
        shutil.rmtree(PLUGINS / cat, ignore_errors=True)

    catalog, skipped, used = [], [], {c: set() for c in CATEGORIES}
    for src in sources:
        repo = src["repo"]; local = cache / repo.replace("/", "__")
        entries = by_repo.get(repo.lower()) if manifest is not None else None
        if manifest is not None and not entries:
            print(f"skipping {repo}: no skills listed for it in scripts/skills.json", file=sys.stderr)
            continue
        try:
            clone(repo, local, args.refresh)
        except subprocess.CalledProcessError as e:
            skipped.append({"repo": repo, "path": "", "reason": f"clone failed: {(e.stderr or '').strip()[:200]}"})
            print(f"clone failed for {repo}, skipping", file=sys.stderr)
            continue
        commit = sh("git", "rev-parse", "HEAD", cwd=local)
        repo_lic_file, repo_lic_text = read_license(local)
        entries = entries if entries is not None else find_skills(local, src)
        skill_dirs = {(local / e["path"]).resolve() for e in entries if e["file"].upper() == "SKILL.MD"}

        for entry in entries:
            rel, fname = entry["path"], entry["file"]
            where = f"{rel}/{fname}" if rel else fname
            sdir = local / rel
            # Only real SKILL.md files. Other .md files in the DB are templates or test fixtures.
            if fname.upper() != "SKILL.MD":
                skipped.append({"repo": repo, "path": where, "skill_id": entry.get("skill_id"),
                                "reason": "not a SKILL.md file"}); continue
            fname = find_skill_file(sdir)
            if not fname and rel:  # moved within the repo? accept a single folder with the same name
                moved = [p.parent for p in local.rglob("*") if p.name.upper() == "SKILL.MD"
                         and p.parent.name == sdir.name and ".git" not in p.parts
                         and p.parent.resolve() not in skill_dirs]  # not already listed as its own skill
                if len(moved) == 1:
                    sdir, rel = moved[0], moved[0].relative_to(local).as_posix()
                    fname = find_skill_file(sdir)
                    print(f"{repo}: {where} moved to {rel}", file=sys.stderr)
            if not fname:
                skipped.append({"repo": repo, "path": where, "skill_id": entry.get("skill_id"),
                                "reason": "missing upstream (moved or deleted)"}); continue
            skill_md = sdir / fname
            lic_file, lic_text = read_license(sdir)
            if not lic_file:
                lic_file, lic_text = repo_lic_file, repo_lic_text
            spdx = classify_license(lic_text)
            fm = frontmatter(skill_md.read_text(errors="ignore"))
            name = re.sub(r"[^a-z0-9-]+", "-", (fm.get("name") or sdir.name).lower()).strip("-")
            if not spdx:
                skipped.append({"repo": repo, "path": where, "skill_id": entry.get("skill_id"),
                                "reason": "license not redistributable"}); continue
            if not fm.get("description"):
                skipped.append({"repo": repo, "path": where, "skill_id": entry.get("skill_id"),
                                "reason": "no description"}); continue
            # A repo-wide "category" in sources.json wins (hand-checked, e.g. bioSkills is all
            # data-science even where the DB's keyword tagging says otherwise), then the DB's.
            cat = src.get("category") or entry.get("category")
            if cat not in CATEGORIES:
                cat = categorize(src, name, fm["description"])
            # Folder = the skill's own name (Agent Skills spec). On a clash use the
            # library's skill_id, which is unique and matches hackernoon.com/skills/{id}.
            slug = name
            if slug in used[cat]:
                slug = entry.get("skill_id") or f"{src['slug']}-{name}"
            i = 2
            while slug in used[cat]:
                slug, i = f"{slug}-{i}", i + 1
            used[cat].add(slug)
            dest = PLUGINS / cat / "skills" / slug
            if sdir.resolve() == local.resolve():
                # Skill at the repo root: copy its top-level files only, not the whole repo.
                dest.mkdir(parents=True)
                for f in sdir.iterdir():
                    if f.is_file() and not f.name.startswith("."):
                        shutil.copy(f, dest / f.name)
            else:
                copy_skill(sdir, dest, skill_dirs - {sdir.resolve()})
            if fname != "SKILL.md":  # e.g. SKILL.MD upstream: agents look for SKILL.md
                tmp = dest / ".skill-rename"
                (dest / fname).rename(tmp); tmp.rename(dest / "SKILL.md")
            if lic_file and not any((dest / n).exists() for n in ("LICENSE", "LICENSE.txt", "LICENSE.md")):
                shutil.copy(lic_file, dest / "LICENSE")
            url = f"https://github.com/{repo}/tree/{commit}/{rel}"
            sid = entry.get("skill_id")
            page = f"https://hackernoon.com/skills/{sid}" if sid else "https://hackernoon.com/skills"
            (dest / "ATTRIBUTION.md").write_text(
                f"# Attribution\n\n- Skill: `{name}`\n- Author: {src['author']}\n- Source: {url}\n"
                f"- License: {spdx} (see LICENSE in this folder)\n- Indexed by HackerNoon's SKILL.md Library: "
                f"{page}\n\nRepublished unmodified apart from this file. All credit to the original author.\n")
            item = {"name": slug, "category": cat, "author": src["author"], "repo": repo,
                    "path": rel, "commit": commit, "license": spdx,
                    "description": fm["description"][:300]}
            if sid:
                item["skill_id"] = sid
            catalog.append(item)

    entries = []
    for cat, (title, desc) in CATEGORIES.items():
        n = len([c for c in catalog if c["category"] == cat])
        if not n:
            continue
        pdir = PLUGINS / cat / ".claude-plugin"; pdir.mkdir(parents=True, exist_ok=True)
        authors = sorted({c["author"] for c in catalog if c["category"] == cat})
        manifest = {"name": cat, "version": "0.1.0",
                    "description": f"{desc} {n} skills from {', '.join(authors[:6])}{' and more' if len(authors) > 6 else ''}.",
                    "author": {"name": "HackerNoon", "url": "https://hackernoon.com/skills"},
                    "homepage": "https://hackernoon.com/skills", "license": "SEE ATTRIBUTION.md IN EACH SKILL",
                    "keywords": ["skills", "hackernoon", cat]}
        (pdir / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
        entries.append({"name": cat, "source": f"./plugins/{cat}", "description": manifest["description"],
                        "version": "0.1.0", "category": title, "keywords": manifest["keywords"]})

    originals = PLUGINS / "hackernoon-originals"
    if originals.exists():
        entries.insert(0, {"name": "hackernoon-originals", "source": "./plugins/hackernoon-originals",
                           "description": "Skills written by HackerNoon: Pixel Icon Library, writing for HackerNoon, tech blogging.",
                           "version": "0.1.0", "category": "HackerNoon Originals",
                           "keywords": ["hackernoon", "pixel-icons", "blogging"]})

    market = {"name": "cuttlefish",
              "owner": {"name": "HackerNoon", "url": "https://hackernoon.com"},
              "metadata": {"description": "Cuttlefish.MD by HackerNoon: license-verified SKILL.md files, installable by category.",
                           "version": "0.1.0"},
              "plugins": entries}
    (ROOT / ".claude-plugin").mkdir(exist_ok=True)
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market, indent=2) + "\n")
    (ROOT / "catalog.json").write_text(json.dumps(sorted(catalog, key=lambda c: (c["category"], c["name"])), indent=1) + "\n")
    (ROOT / "skipped.json").write_text(json.dumps(skipped, indent=1) + "\n")
    counts = {e["name"]: len([c for c in catalog if c["category"] == e["name"]]) for e in entries}
    counts["hackernoon-originals"] = len(list((PLUGINS / "hackernoon-originals" / "skills").glob("*/SKILL.md")))
    update_readme(len(catalog) + counts["hackernoon-originals"], counts, entries, catalog)
    print(json.dumps({"skills": len(catalog), "skipped": len(skipped), "per_plugin": counts}, indent=1))


def update_readme(total, counts, entries, catalog):
    """Rewrite the generated blocks in README.md so the numbers never go stale."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    text = readme.read_text()
    authors = len({c["author"] for c in catalog}) + 1
    rows = ["| Plugin | Skills | Install |", "|---|---:|---|"]
    for e in entries:
        rows.append(f"| **{e['category']}** | {counts.get(e['name'], 0):,} | `/plugin install {e['name']}@cuttlefish` |")
    blocks = {"COUNT": f"{total:,}", "AUTHORS": f"{authors:,}", "LIB": f"{LIBRARY_TOTAL:,}",
              "TABLE": "\n" + "\n".join(rows) + "\n"}
    for key, val in blocks.items():
        text = re.sub(rf"(<!-- {key} -->).*?(<!-- /{key} -->)", lambda m: m.group(1) + val + m.group(2), text, flags=re.S)
    text = re.sub(r"badge/skills-[0-9%2C,]+-", f"badge/skills-{total:,}-".replace(",", "%2C"), text)
    text = re.sub(r"badge/library-[0-9%2C,]+%20skills-", f"badge/library-{LIBRARY_TOTAL:,}%20skills-".replace(",", "%2C"), text)
    readme.write_text(text)


if __name__ == "__main__":
    main()

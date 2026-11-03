<div align="center">

<img src="assets/cuttlefish.svg" alt="Pixel cuttlefish" width="264">

# Project Cuttlefish.MD

### Read all the useful SKILL.md files. Then install them.

**The SKILL.md Library by [HackerNoon](https://hackernoon.com), packaged as an installable Agent Skills marketplace.**

[![Skills in this repo](https://img.shields.io/badge/skills-2%2C806-00ff41?style=flat-square)](catalog.json)
[![Library](https://img.shields.io/badge/library-2%2C908%20skills-black?style=flat-square)](https://hackernoon.com/skills-md-library-project-cuttlefish-md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard-00ff41?style=flat-square)](https://agentskills.io)
[![GitHub stars](https://img.shields.io/github/stars/hackernoon/cuttlefish-agent-skills?style=flat-square)](https://github.com/hackernoon/cuttlefish-agent-skills/stargazers)

**[→ Browse all <!-- LIB -->2,908<!-- /LIB --> skills in full text at hackernoon.com](https://hackernoon.com/skills-md-library-project-cuttlefish-md)**

</div>

---

## What this is

Read the most capable, adaptive, and verified `Skills.md` files in full text — no install commands required (but feel free to install), no scraped snippets, just copy and paste `Skills.md` files. Credited to their original authors, licenses checked one repo at a time, verified by human editors. That's [Project Cuttlefish.MD](https://hackernoon.com/skills-md-library-project-cuttlefish-md).

This repo is the "feel free to install" part. It packages every skill from the library whose license allows redistribution into category plugins, so Claude Code, Codex, Cursor or any agent that supports the [open Agent Skills standard](https://agentskills.io) can load them directly.

## Why a cuttlefish?

A Cuttlefish, like a `Skill.md` file, studies its habitat, then evolves. Project Cuttlefish.MD is for you and your agent to leverage any skill in any ocean.

## Install

**Claude Code:**

```text
/plugin marketplace add hackernoon/cuttlefish-agent-skills
/plugin install dev-workflow@cuttlefish
```

Run `/plugin` to browse the other categories.

**Codex CLI, Cursor, Gemini CLI and other Agent Skills tools:** clone the repo and copy a category's skill folders into your agent's skills directory:

```bash
git clone https://github.com/hackernoon/cuttlefish-agent-skills
cp -r cuttlefish-agent-skills/plugins/writing-blogging/skills/* your-project/.agents/skills/
```

Codex reads `.agents/skills/` in a project or `~/.agents/skills/` for every project. For other tools, use the skills folder named in that tool's docs. The files work unchanged.

**No install at all:** read and copy any skill at [hackernoon.com/skills-md-library-project-cuttlefish-md](https://hackernoon.com/skills-md-library-project-cuttlefish-md).

## What's inside

**<!-- COUNT -->2,806<!-- /COUNT --> skills from <!-- AUTHORS -->29<!-- /AUTHORS --> authors**, sorted into the same categories as the library:

<!-- TABLE -->
| Plugin | Skills | Install |
|---|---:|---|
| **HackerNoon Originals** | 1 | `/plugin install hackernoon-originals@cuttlefish` |
| **Dev Workflow** | 530 | `/plugin install dev-workflow@cuttlefish` |
| **Writing & Blogging** | 706 | `/plugin install writing-blogging@cuttlefish` |
| **Design & UI** | 131 | `/plugin install design-ui@cuttlefish` |
| **Marketing & SEO** | 307 | `/plugin install marketing-seo@cuttlefish` |
| **QA & Testing** | 422 | `/plugin install qa-testing@cuttlefish` |
| **Security** | 102 | `/plugin install security@cuttlefish` |
| **Data & Science** | 599 | `/plugin install data-science@cuttlefish` |
| **Learn Tech** | 8 | `/plugin install learn-tech@cuttlefish` |
<!-- /TABLE -->

Each skill's author, source repo, exact commit and license are listed in [`catalog.json`](catalog.json).

## HackerNoon Originals

| Skill | What it does | Status |
|---|---|---|
| `pixel-icon-library` | Uses the [Pixel Icon Library](https://pixeliconlibrary.com), the icon set HackerNoon is drawn with | ✅ Live |
| `write-for-hackernoon` | Draft, self-edit and submit to the [HackerNoon Editing Protocol](https://hackernoon.com/the-hackernoon-editing-protocol) | 🛠 Shipping soon |
| `tech-blogging` | Headlines and structure drawn from 150K+ HackerNoon stories | 🛠 Shipping soon |

## Why more skills on the site than here?

The library lists every useful skill HackerNoon's editors have verified. This repo republishes only the ones whose licenses allow it: MIT, Apache-2.0, BSD and CC-BY, judged per skill, because a skill's own LICENSE overrides its repo's.

- **Copied in:** licensed skills are copied unchanged, with their license file and an `ATTRIBUTION.md` naming the author and the exact source commit.
- **Link-only:** unlicensed or "all rights reserved" skills stay on the site, linked to their authors. They're never copied here and are logged in [`skipped.json`](skipped.json).

More of the library's source repos are being added. Watch or star the repo to follow along.

## Featured authors

<!-- AUTHOR_LIST -->

[GPTomics](https://github.com/GPTomics/bioSkills) (562) · [Tech Leads Club](https://github.com/tech-leads-club/agent-skills) (94) · [Daniel Agrici](https://github.com/AgriciDaniel/claude-seo) (67) · [Corey Haines](https://github.com/coreyhaines31/marketingskills) (53) · [Matt Pocock (Total TypeScript)](https://github.com/mattpocock/skills) (39) · [Cloudflare](https://github.com/cloudflare/skills) (19) · [Thomas Ricouard](https://github.com/Dimillian/Skills) (16) · [Jesse Vincent (obra)](https://github.com/obra/superpowers) (15) · [Anthropic](https://github.com/anthropics/skills) (14) · [Vercel Labs](https://github.com/vercel-labs/agent-browser) (10) · [lackeyjb](https://github.com/lackeyjb/playwright-skill) (1) · [HackerNoon](https://github.com/hackernoon/pixel-icon-library) (1)

<!-- /AUTHOR_LIST -->

**Are you an author?** To have a skill removed, recategorized or updated, open an issue or email support@hackernoon.com.

## Read more on HackerNoon

- **Tags:** [#agent-skills](https://hackernoon.com/tagged/agent-skills) · [#claude-code](https://hackernoon.com/tagged/claude-code) · [#ai-coding](https://hackernoon.com/tagged/ai-coding) · [#ai-agents](https://hackernoon.com/tagged/ai-agents) · [AI & ML](https://hackernoon.com/c/ai)
- [How to Write an Agent Skill](https://hackernoon.com/how-to-write-an-agent-skill)
- [The Right Way to Write an Agent Skill](https://hackernoon.com/the-right-way-to-write-an-agent-skill)
- [Read This Before You Write Another Agent Skill](https://hackernoon.com/read-this-before-you-write-another-agent-skill)
- [Your Agent Is Writing Its Own Skills. Who Is Reading Them?](https://hackernoon.com/your-agent-is-writing-its-own-skills-who-is-reading-them)
- [The HackerNoon Editing Protocol](https://hackernoon.com/the-hackernoon-editing-protocol): the standard every HackerNoon story is reviewed against

## Build it yourself

```bash
git clone https://github.com/hackernoon/cuttlefish-agent-skills
cd cuttlefish-agent-skills
python3 scripts/build.py        # clones the sources in scripts/sources.json and regenerates plugins/
claude plugin validate .        # checks the marketplace and every plugin
```

The skill counts and the table in this README regenerate on every build.

## ⭐ Star Cuttlefish.MD

Stars help other developers find the library, and they tell us which oceans to explore next.

---

<div align="center">

Built by [HackerNoon](https://hackernoon.com) · [Read every skill in full text](https://hackernoon.com/skills-md-library-project-cuttlefish-md) · Marketplace tooling MIT · Each skill keeps its own license

</div>

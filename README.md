<div align="center">

# 🦑 Cuttlefish.MD

### The license-verified Agent Skills marketplace, by HackerNoon

**<!-- COUNT -->891<!-- /COUNT --> agent skills from <!-- AUTHORS -->12<!-- /AUTHORS --> authors. Install them by category with one command. Every skill keeps its credit.**

[![Skills](https://img.shields.io/badge/skills-891-00ff41?style=flat-square)](catalog.json)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-black?style=flat-square)](https://docs.claude.com/en/docs/claude-code/plugins)
[![License checked](https://img.shields.io/badge/licenses-checked%20per%20skill-00ff41?style=flat-square)](#how-a-skill-gets-in)
[![Browse](https://img.shields.io/badge/browse-hackernoon.com%2Fskills-black?style=flat-square)](https://hackernoon.com/skills)
[![GitHub stars](https://img.shields.io/github/stars/hackernoon/cuttlefish-agent-skills?style=flat-square)](https://github.com/hackernoon/cuttlefish-agent-skills/stargazers)

</div>

---

## Install in 10 seconds

```text
/plugin marketplace add hackernoon/cuttlefish-agent-skills
/plugin install dev-workflow@cuttlefish
```

That's it. No copy-pasting SKILL.md files. Run `/plugin` to browse the other categories.

### Use with any agent

These are standard [Agent Skills](https://agentskills.io), the open SKILL.md format supported by 30+ tools, so they aren't tied to Claude. Each skill lives at `plugins/<category>/skills/<skill>/`. Copy or symlink that folder into your agent's skills directory:

```bash
git clone https://github.com/hackernoon/cuttlefish-agent-skills
# Codex CLI and other .agents-compatible tools, for one repo:
cp -r cuttlefish-agent-skills/plugins/writing-blogging/skills/* your-project/.agents/skills/
# ...or for every project:
cp -r cuttlefish-agent-skills/plugins/dev-workflow/skills/* ~/.agents/skills/
```

For Cursor, Gemini CLI, Copilot and other agents, use the skills folder named in that tool's docs. The files work unchanged.

## What's inside

<!-- TABLE -->
| Plugin | Skills | Install |
|---|---:|---|
| **HackerNoon Originals** | 1 | `/plugin install hackernoon-originals@cuttlefish` |
| **Dev Workflow** | 131 | `/plugin install dev-workflow@cuttlefish` |
| **Writing & Blogging** | 43 | `/plugin install writing-blogging@cuttlefish` |
| **Design & UI** | 18 | `/plugin install design-ui@cuttlefish` |
| **Marketing & SEO** | 108 | `/plugin install marketing-seo@cuttlefish` |
| **QA & Testing** | 19 | `/plugin install qa-testing@cuttlefish` |
| **Security** | 4 | `/plugin install security@cuttlefish` |
| **Data & Science** | 563 | `/plugin install data-science@cuttlefish` |
| **Learn Tech** | 4 | `/plugin install learn-tech@cuttlefish` |
<!-- /TABLE -->

Every skill, with its author, source repo, exact commit and license, is listed in [`catalog.json`](catalog.json).

## Why Cuttlefish?

A cuttlefish can change its skin to match whatever it's doing. Skills do the same for your agent: plan like a staff engineer, debug systematically, audit SEO, write a blog post, parse a genome.

Most skill collections are hand-picked lists or copy-paste dumps. Cuttlefish differs in three ways:

- **Licenses are checked for every skill, not every repo.** A skill's own LICENSE file overrides its repo's. Anthropic's repo, for example, mixes Apache-2.0 skills with proprietary ones, and we only ship the Apache ones.
- **Credit travels with the code.** Every skill folder carries its license plus an `ATTRIBUTION.md` naming the author and the exact source commit.
- **Humans curate it.** These come from [HackerNoon's SKILL.md Library](https://hackernoon.com/skills), where editors review skills before they're listed.

## How a skill gets in

1. Its source repo is added to [`scripts/sources.json`](scripts/sources.json).
2. `scripts/build.py` clones the repo, finds every `SKILL.md`, and reads the nearest LICENSE.
3. **MIT, Apache-2.0, BSD and CC-BY** skills are copied in unchanged, plus an `ATTRIBUTION.md`.
4. **Unlicensed or "all rights reserved"** skills are never copied. They're logged in [`skipped.json`](skipped.json), and the library lists them as link-only pointers to the author's repo.
5. Skills are sorted into category plugins, and this README's numbers regenerate automatically.

## Featured authors

Anthropic · Jesse Vincent ([superpowers](https://github.com/obra/superpowers)) · Matt Pocock · Cloudflare · Vercel Labs · Corey Haines · Tech Leads Club · Daniel Agrici · Thomas Ricouard · GPTomics · and the HackerNoon design team ([Pixel Icon Library](https://pixeliconlibrary.com))

## For skill authors

- **Get listed.** Open an issue with your repo URL, or submit it at [hackernoon.com/skills](https://hackernoon.com/skills). Repos with open licenses get packaged automatically.
- **Change or remove a skill.** Open an issue, or email support@hackernoon.com. We act on author requests quickly.
- **Add your badge:** `[![On Cuttlefish](https://img.shields.io/badge/on-Cuttlefish.MD-00ff41?style=flat-square)](https://github.com/hackernoon/cuttlefish-agent-skills)`

## Build it yourself

```bash
git clone https://github.com/hackernoon/cuttlefish-agent-skills
cd cuttlefish-agent-skills
python3 scripts/build.py        # clones sources into .cache/ and regenerates plugins/
claude plugin validate .        # checks the marketplace and every plugin
```

## ⭐ Star this repo

Stars help other people find the library, and they tell us which categories to grow next. **If one skill here saved you an hour, star the repo.**

---

<div align="center">

Built by [HackerNoon](https://hackernoon.com) · Browse the full library at [hackernoon.com/skills](https://hackernoon.com/skills) · Marketplace tooling MIT · Each skill keeps its own license

</div>

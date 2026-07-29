# Juan David Gomez

**I build agentic dev tooling, and I verify what agents claim.**

Production AI systems at scale during the day — [Postilize](https://www.postilize.com), where I
was one of the first eight engineers. In the open: MCP tooling, Claude Code plugins, and upstream
fixes to the agent stack.

The through-line is verification. A cheap model hands you a wrong answer in a confident sentence.
A migration codemod leaves a green test suite sitting on top of a dead code path. A monkey-patch
bound to a package instead of a module silently stops working and nothing fails. Those are the
bugs I go looking for, because they are the ones that survive CI.

---

## Tools

**[claude-cheap-agents](https://github.com/Kayaba-Attribution/claude-cheap-agents)** ·
Claude Code plugin, MIT

Delegate bulk work to cheap OpenRouter models (DeepSeek, Qwen) through the OpenCode CLI, then
verify the answer by re-running the command the agent says it used. Trust is a verdict, not a vibe.

Ships with the failure modes measured rather than assumed: `opencode run` hangs forever on an
inherited open stdin pipe (3s with stdin closed, still hanging at 6m40s without), parallel runs
race a schema migration on a shared SQLite session db, hybrid models default reasoning **on** at
68s/$0.0164 against 38s/$0.0095 for an identical answer, and a cheap agent will report a confident
"no matches" after `rg` returned `command not found`.

**[claude-code-skill-help](https://github.com/Kayaba-Attribution/claude-code-skill-help)** ·
Claude Code plugin, MIT

See the real usage, flags and arguments of any Claude Code skill, slash command or plugin. The
slash menu truncates a skill's description to one line and there is no `claude skill details`, so
you end up `cat`-ing `SKILL.md` files to remember whether a command takes arguments.

Handles what a naive lookup misses: the two file layouts a command can live in (one plugin reports
11 skills where only 3 exist as `SKILL.md`), the two plugin locations where only the version-pinned
one is authoritative, and the zsh glob that aborts the whole command instead of expanding to nothing.

---

## Upstream

Migrating the open-source MCP ecosystem to protocol revision `2026-07-28`.

| Contribution | What it was |
|---|---|
| [oraios/serena#1777](https://github.com/oraios/serena/pull/1777) | `mcp` 1.28.1 → 2.0.0. Caught two silent regressions no test could: an inert `Settings` assignment that killed every `FASTMCP_*` env var, and a monkey-patch bound to a package instead of a module. Both were green. |
| [makenotion/notion-mcp-server#339](https://github.com/makenotion/notion-mcp-server/pull/339) | Migration to the split SDK v2 packages. 27-line diff, full CI green. |
| [punkpeye/fastmcp#300](https://github.com/punkpeye/fastmcp/issues/300) | Measured the migration instead of guessing at it (codemod: 86 changes, 442/448 tests passing) and isolated the two public-API decisions that actually block it. |
| [sooperset/mcp-atlassian#1541](https://github.com/sooperset/mcp-atlassian/issues/1541) | Dependency blocker, the exact method port required, and a failing GHSA-3r68 regression test on the dispatch path. |

A finding worth repeating from that work: **nothing forces a migration to the new revision.** The
SDK speaks the 2025-era protocol unless a server explicitly opts in, and the spec carries a
twelve-month deprecation window. Most of the coverage said otherwise.

---

## Production

**Postilize** — Senior Software Engineer, one of the first eight engineers · Mar 2025 – present

Architect of the Signals pipeline: agentic prospecting over a multi-region news corpus, async
infrastructure on FastAPI, Celery and Redis, and the LLM cost and throughput work underneath it.
Also built the Signals MCP server and the outreach surfaces analysts use daily. Earlier, took the
agentic outreach platform from prototype to production.

<!-- Add back any scale/cost figures you can defend precisely, including the baseline and what else
     changed at the same time. Numbers that wobble under questioning cost more than they earn. -->

**Forta Foundation** — Blockchain security · 2023 – 2024

Real-time fraud and exploit detectors over 800K–1.2M datapoints/day, containerized as distributed
alerting models. Adversarial pattern-matching at volume, which is where the verification habit
came from.

**BSc Computer Science**, Goldsmiths, University of London — First Class Honours

---

## Elsewhere

[kayaba-attribution.dev](https://www.kayaba-attribution.dev/) ·
[Twitter](https://twitter.com/JuanDavidGV_KA) ·
[Telegram](https://t.me/Kayaba_Attribution)

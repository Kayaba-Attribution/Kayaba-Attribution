# Juan David Gomez

**I build agentic dev tooling, and I verify what agents claim.**

Production AI systems at scale during the day — [Postilize](https://www.postilize.com), where I
was one of the first eight engineers. In the open: MCP tooling, Claude Code plugins, and upstream
fixes to the agent stack.

I take a rough idea to a product people depend on, and I own it end to end: the architecture, the
code, the rollout, and the person using it on Monday morning. Nobody has to hand me a spec.

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

**Postilize** — Senior Software Engineer, one of the first eight engineers · Nov 2024 – present

AI for large US law firms: business-development signals, relationship data and CRM quality.
~400 merged PRs across five services in under two years.

- **Signals pipeline, idea to enterprise product.** Architect and owner of agentic prospecting over
  a multi-region news corpus: search, LLM classification and enrichment, dedup, delivery to
  lawyers. The V2 rebuild on FastAPI, Celery and Redis took it from 70K to 280K articles a day and
  from 1 to 4 regions while cutting LLM cost by about 90%. Coverage grew from a firm's top 100
  companies to 500. Then I built the Signals MCP server on top.
- **Typed AI decisions in production.** Put [Jev](https://typesafe.ai) decision gates into company
  identity resolution: one narrow factual question per call, neutral candidate labels, evidence
  fetched before judging, and an explicit "insufficient evidence" answer. The audit that started
  it found about half the early decisions were low-confidence fallbacks cached as truth. The gate
  now refuses instead of guessing.
- **LLM-as-judge with a human in the loop.** An AI judge reviews suggested CRM changes in shadow
  mode, with a review workbench and per-tenant rollout flags, before anything is auto-suppressed.
- **Identity and data quality at scale.** Guards that stop email signatures, enrichment providers
  and CRM syncs from writing the wrong person or company, plus dry-run-first repairs on live data.
- **LLM cost and throughput.** Per-signal cost attribution, then re-tiering the model that
  dominated the bill onto cheaper reasoning-off models.
- **Agentic outreach.** Took the email-generation platform from a Streamlit prototype to a
  production FastAPI service (CrewAI, then Autogen with Perplexity research), plus the outreach
  surfaces analysts use daily.

**Merakii Seaview Escape** — Forward-deployed engineer, boutique hotel in Curaçao · 2026 – present

Embedded with the owner: learn how the hotel actually runs, then automate as much of it as
possible on Cloudflare Workers.

- **Owner's AI assistant.** A Cloudbeds MCP server, so bookings, arrivals and open rooms can be
  queried in plain language, plus a 7am daily brief for the owner: arrivals, balances to chase, and a
  14-day occupancy outlook with raise-or-promote calls.
- **Pricing data from scratch.** Daily rate and booking rails running unattended, a 3-year pricing
  log backfilled (10,202 price changes), and a replay harness over 131K pricing decisions that
  reproduces the current revenue manager exactly: the baseline any new pricing policy must beat.
- **Menu from real demand.** 20 months of POS data (4,780 bills) showed the best sellers were
  missing from the printed menu. That analysis shaped the new menu and its pricing.
- Also shipped the hotel's website and analytics.

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

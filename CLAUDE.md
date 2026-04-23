# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

board-pta-adapter transforms PTA (Programming Teaching Assistant, pintia.cn) competition data into formats for GPLT and XCPCIO leaderboard display systems. It fetches problem sets, submissions, and rankings from PTA's API and outputs JSON files consumed by these scoreboard frontends.

## Build & Development

**Package manager:** `uv` (Python 3.13, hatchling build backend)

```bash
uv sync                    # Install dependencies
uv run gplt-gen            # Generate static GPLT data (contest, students, teams)
uv run gplt-sync           # Continuously sync GPLT rankings
uv run xcpcio-gen          # Generate static XCPCIO data (config, orgs, teams)
uv run xcpcio-sync         # Continuously sync XCPCIO submissions
uv run xcpcio-cdp          # Generate Contest Data Package (NDJSON event feed)
```

**Linting:**
```bash
uv run ruff check src/     # Lint
uv run ruff format src/    # Format
```

Line length is 120 characters (configured in pyproject.toml).

There are no tests in this project.

## Configuration

Copy `config.template.yaml` to `config.yaml` before running. Key fields:
- `pta.pta_session` — PTA session cookie for API auth
- `pta.problem_set_id` — target problem set on PTA
- `sync_interval` — polling interval in seconds (default 15)
- `gplt`/`xcpcio` sections — output dirs, Excel template paths, contest parameters

## Architecture

```
config.yaml ──────────┐
excel templates ──┐   │
                  ▼   ▼
              cli/gplt.py ──► core/gplt.py ──► output/gplt/*.json
                  │               │
                  │          pta_client.py ◄── pintia.cn (3 retries, 15s timeout)
                  │               │            
              cli/xcpcio.py ─► core/xcpcio.py ──► output/xcpcio/*.json
                                                  output/xcpcio/cdp/event-feed.ndjson
                                                  output/xcpcio/cdp/organizations
```

**Source layout (`src/adapter/`):**
- `cli/gplt.py`, `cli/xcpcio.py` — CLI entry points, each self-contained with its own `_build_runtime()`
- `core/gplt.py`, `core/xcpcio.py` — Adapter classes that transform PTA data → output format
- `models/` — Pydantic v2 models: `config.py` (YAML config), `gplt.py` / `xcpcio.py` (output schemas), `pta.py` (API responses)
- `pta_client.py` — `PTAClient` HTTP client
- `utils.py` — `SheetReader` (Excel input) and time formatting helpers
- `config.py` — YAML config loader

**Error handling:**
- One-shot commands (`generate`, `cdp`): no try/except — failures crash with a natural traceback
- Long-running loops (`synchronize`): catch `PTAClientError` to retry on network/API failures; all other exceptions crash the process

**Data conventions:**
- Organization IDs are the first 8 chars of the MD5 hash of the school name
- Contest times are milliseconds; relative timestamps calculated from contest start
- Frozen scoreboard: submissions after freeze time are marked "FROZEN"; the unfrozen variant omits this
- Team group classification is driven by `xcpcio.official_schools` in config
- PTA language/status codes are mapped to XCPCIO equivalents (e.g., `GXX` → `CPP`, `WRONG_ANSWER` → `WA`)

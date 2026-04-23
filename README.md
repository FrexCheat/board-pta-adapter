# board-pta-adapter

Transform PTA (pintia.cn) competition data into formats for GPLT and XCPCIO leaderboard display systems.

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

## Build & Development

**Package manager:** `uv` (Python 3.13)

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

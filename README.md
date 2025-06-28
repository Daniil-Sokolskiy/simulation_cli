## Finsimco CLI – README

### 1 . Requirements

| tool                          | version  |
| ----------------------------- | -------- |
| Python                        | 3.9 +    |
| PostgreSQL                    | 13 +     |
| Redis                         | 5 +      |
| (dev) Docker / docker-compose | optional |

### 2 . Setup

```bash
git clone <repo> && cd finsimco_cli
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create **.env** in the project root:

```
# Postgres used by the application
PGUSER=postgres
PGPASSWORD=postgres
PGHOST=localhost
PGPORT=5432
PGDATABASE=finsimco
# Redis
REDIS_URL=redis://localhost:6379/0
```

> **Quick start with Docker**

```bash
docker compose up -d        # launches postgres & redis with correct creds
```

Run the DB initialisation script (creates tables and seed parameters):

```bash
psql -h $PGHOST -U $PGUSER -d $PGDATABASE -f docker/init/001_full_schema.sql
```

### 3 . Running simulations

| command                            | description                       |
| ---------------------------------- | --------------------------------- |
| `python -m src.cli.team1 --game 1` | Team 1, Game 1 (single-input)     |
| `python -m src.cli.team2 --game 1` | Team 2, Game 1                    |
| `python -m src.cli.team1 --game 2` | Team 1, Game 2 (both teams input) |
| `python -m src.cli.team2 --game 2` | Team 2, Game 2                    |

Launch two terminal windows (T1 + T2) for the same `--game` number.

* **Game 1** Team 1 enters numbers, Team 2 only approves
  (`Idx to OK (q-quit):`).
* **Game 2** Both teams may enter values.
  Team 2 can type `e <idx> <value>` to edit its figure, or just `<idx>` to approve.

When all parameters are **OK**, both windows show
`Success! Closing in 2 seconds…` and exit.

### 4 . Test suite

```bash
# make sure a *test* Postgres is running (port 5433 by default)
docker run -d --name finsimco-test-db \
  -p 5433:5432 -e POSTGRES_DB=test -e POSTGRES_PASSWORD=postgres postgres:15

export PGTEST_DSN="postgresql+psycopg2://postgres:postgres@localhost:5433/test"
pytest -q          # 4 tests: validators, formulas, session helpers
```

### 5 . Folder guide

```
src/
  core/            DB models, formulas, validators, session logic
  cli/             team1.py & team2.py   ← entry points
  infrastructure/  Redis helper, TUI helpers
  utils/           small prompt helper
docker/            init SQL and compose file
tests/             pytest suite
```


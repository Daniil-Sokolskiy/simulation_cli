DO $$
BEGIN
  CREATE TYPE param_status AS ENUM ('TBD','OK');
EXCEPTION WHEN duplicate_object THEN NULL;
END$$;

CREATE TABLE IF NOT EXISTS parameters (
  id   SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  unit TEXT
);

INSERT INTO parameters(name, unit) VALUES
  ('EBITDA',          '$'),
  ('Interest Rate',   '%'),
  ('Multiple',        'x'),
  ('Factor Score',    '')
ON CONFLICT(name) DO NOTHING;

CREATE TABLE IF NOT EXISTS sessions (
  id          BIGSERIAL PRIMARY KEY,
  game        SMALLINT CHECK (game IN (1,2)),
  started_at  TIMESTAMPTZ DEFAULT NOW(),
  finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS param_state (
  session_id BIGINT REFERENCES sessions(id)    ON DELETE CASCADE,
  param_id   INT    REFERENCES parameters(id)  ON DELETE CASCADE,
  team       SMALLINT CHECK (team IN (1,2)),
  value      NUMERIC,
  status     param_status DEFAULT 'TBD',
  updated_at TIMESTAMPTZ   DEFAULT NOW(),
  PRIMARY KEY (session_id, param_id, team)
);

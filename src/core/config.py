from pathlib import Path
from typing import Final
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

PG_DSN: Final[str] = (
    "postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}".format(
        user=os.getenv("PGUSER", "postgres"),
        pwd=os.getenv("PGPASSWORD", "postgres"),
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        db=os.getenv("PGDATABASE", "finsimco"),
    )
)

REDIS_URL: Final[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
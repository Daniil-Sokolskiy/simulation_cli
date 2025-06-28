import gevent.monkey; gevent.monkey.patch_all()
import psycogreen.gevent; psycogreen.gevent.patch_psycopg()

from sqlalchemy import create_engine, MetaData
from src.core.config import PG_DSN

engine = create_engine(
    PG_DSN,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)
metadata = MetaData()
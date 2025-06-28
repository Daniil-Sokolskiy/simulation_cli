from sqlalchemy import (
    Table, Column, Integer, BigInteger, SmallInteger, Text, Numeric,
    Enum, TIMESTAMP, text, ForeignKey, MetaData, PrimaryKeyConstraint
)

metadata = MetaData()

status_enum = Enum("TBD", "OK", name="param_status")

parameters = Table(
    "parameters", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, unique=True, nullable=False),
    Column("unit", Text),
)

sessions = Table(
    "sessions", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("game", SmallInteger, nullable=False),
    Column("started_at", TIMESTAMP(timezone=True), server_default=text("NOW()")),
    Column("finished_at", TIMESTAMP(timezone=True)),
)

param_state = Table(
    "param_state", metadata,
    Column("session_id", BigInteger,
           ForeignKey("sessions.id", ondelete="CASCADE")),
    Column("param_id", Integer,
           ForeignKey("parameters.id", ondelete="CASCADE")),
    Column("team", SmallInteger),            # 1 или 2
    Column("value", Numeric),
    Column("status", status_enum, server_default="TBD"),
    Column("updated_at", TIMESTAMP(timezone=True),
           server_default=text("NOW()")),
    PrimaryKeyConstraint("session_id", "param_id", "team"),
)

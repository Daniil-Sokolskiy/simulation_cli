from curses import flash
from typing import Optional, List, Tuple

from sqlalchemy import (
    select, update, func, literal, insert          
)
from sqlalchemy.sql import alias, outerjoin
from sqlalchemy.dialects.postgresql import insert as pg_insert  

from src.core.db import engine
from src.core.models import parameters, sessions, param_state


def get_or_create_session(game: int) -> int:
    with engine.begin() as conn:
        sid: Optional[int] = conn.scalar(
            select(sessions.c.id)
            .where(sessions.c.game == game,
                   sessions.c.finished_at.is_(None))
        )
        if sid:
            return sid
        return conn.scalar(
            insert(sessions).values(game=game).returning(sessions.c.id)
        )


def close_session(sid: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            update(sessions)
            .where(sessions.c.id == sid)
            .values(finished_at=func.now())
        )


def fetch_table(sid: int) -> List[Tuple[str, Optional[object],
                                        Optional[object], str]]:

    ps1 = alias(param_state, name="ps1")
    ps2 = alias(param_state, name="ps2")

    j1 = outerjoin(
        parameters,
        ps1,
        (ps1.c.param_id == parameters.c.id) &
        (ps1.c.session_id == sid) &
        (ps1.c.team == 1)
    )
    j2 = outerjoin(
        j1,
        ps2,
        (ps2.c.param_id == parameters.c.id) &
        (ps2.c.session_id == sid) &
        (ps2.c.team == 2)
    )

    sql = (
        select(
            parameters.c.name,
            parameters.c.unit,
            ps1.c.value.label("v1"),
            ps2.c.value.label("v2"),
            func.coalesce(ps2.c.status,
                          literal("TBD")).label("status")
        )
        .select_from(j2)                 
        .order_by(parameters.c.id)
    )

    with engine.connect() as conn:
        return conn.execute(sql).fetchall()


def upsert_value(sid: int, name: str, team: int, value) -> None:
    with engine.begin() as conn:
        pid = conn.scalar(
            select(parameters.c.id).where(parameters.c.name == name)
        )

        conn.execute(
            pg_insert(param_state)
            .values(session_id=sid, param_id=pid, team=team,
                    value=value, status='TBD')
            .on_conflict_do_update(
                index_elements=("session_id", "param_id", "team"),
                set_=dict(value=value,
                          status='TBD',
                          updated_at=func.now())
            )
        )

        if team == 1:
            conn.execute(
                pg_insert(param_state)
                .values(session_id=sid, param_id=pid, team=2,
                        status='TBD')
                .on_conflict_do_update(
                    index_elements=("session_id", "param_id", "team"),
                    set_=dict(status='TBD', updated_at=func.now())
                )
            )


def set_ok(sid: int, name: str) -> None:
    with engine.begin() as conn:
        pid = conn.scalar(
            select(parameters.c.id).where(parameters.c.name == name)
        )
        conn.execute(
            pg_insert(param_state)
            .values(session_id=sid, param_id=pid, team=2, status='OK')
            .on_conflict_do_update(
                index_elements=("session_id", "param_id", "team"),
                set_=dict(status='OK', updated_at=func.now())
            )
        )


# --- В начале файла (раздел импортов) ------------------------------
from sqlalchemy.sql import alias, outerjoin, literal   # ← добавить literal

# -------------------------------------------------------------------
def everyone_ok(sid: int) -> bool:
    ps2 = alias(param_state, name="ps2")

    join_ = outerjoin(
        parameters,
        ps2,
        (ps2.c.param_id == parameters.c.id) &
        (ps2.c.session_id == sid) &
        (ps2.c.team == 2)
    )

    query = (
        select(func.count())
        .select_from(join_)
        .where(func.coalesce(ps2.c.status, literal("TBD")) == literal("TBD"))
    )

    with engine.connect() as conn:
        pending = conn.scalar(query)
        return pending == 0


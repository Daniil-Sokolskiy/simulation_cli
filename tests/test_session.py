import sqlalchemy as sa
from src.core.session import (
    get_or_create_session, upsert_value,
    set_ok, everyone_ok
)
from src.core.models import parameters

def seed_params(conn):
    conn.execute(
        parameters.insert(),
        [{"name": "A", "unit": "#"}, {"name": "B", "unit": "#"}],
    )

def test_workflow(engine):
    with engine.begin() as conn:
        seed_params(conn)

    sid = get_or_create_session(1)
    upsert_value(sid, "A", 1, 10)
    assert not everyone_ok(sid)

    set_ok(sid, "A")
    assert not everyone_ok(sid)

    upsert_value(sid, "B", 1, 20)
    assert not everyone_ok(sid)

    set_ok(sid, "A")
    assert not everyone_ok(sid)

    set_ok(sid, "B")
    assert everyone_ok(sid)

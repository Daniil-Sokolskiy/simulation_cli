import argparse, curses, time
from typing import Optional

from src.core.validators import validate
from src.core.session import (
    get_or_create_session, fetch_table, upsert_value
)
from src.core.formulas import valuation
from src.infrastructure.redis_helper import r, get_message, publish, PUBSUB_CHANNEL
from src.infrastructure.tui import tui, init_curses, draw_table
from src.utils.prompt import prompt

SUCCESS_MSG = "Success! Closing in 2 seconds…"

parser = argparse.ArgumentParser()
parser.add_argument("--game", type=int, choices=(1, 2), default=1)
GAME = parser.parse_args().game
TEAM_ID = 1
SESSION_ID = get_or_create_session(GAME)


def flash(stdscr, row: int, msg: str) -> None:
    stdscr.move(row, 0)
    stdscr.clrtoeol()
    stdscr.addstr(row, 0, msg, curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh()
    time.sleep(1)


def main(stdscr):
    init_curses(stdscr)
    buf = ""
    selected: Optional[str] = None
    pubsub = r.pubsub()
    pubsub.subscribe(PUBSUB_CHANNEL)

    while True:
        if (m := get_message(pubsub)) and m.get("cmd") == "QUIT":
            stdscr.addstr(0, 0, SUCCESS_MSG, curses.color_pair(2))
            stdscr.refresh(); time.sleep(2); break

        rows = fetch_table(SESSION_ID)
        idx_map = {str(i): n for i, (n, *_ ) in enumerate(rows, 1)}
        draw_table(
            stdscr, rows,
            f"Team 1 — Game {GAME}",
            two_teams=(GAME == 2)
        )

        if GAME == 1:
            mapping = {n: v1 for n, _, v1, *_ in rows}
            v = valuation(mapping)
            if v is not None:
                stdscr.addstr(len(rows) + 3, 0, f"Valuation: {v:,.2f}")
        stdscr.refresh()

        pr_row = len(rows) + 5
        if selected is None:
            done, buf = prompt(stdscr, pr_row, "Idx/Name (q-quit): ", buf)
            if not done:              
                continue
            if buf.lower() == "q":
                break
            selected = idx_map.get(buf) or buf
            if selected not in idx_map.values():
                flash(stdscr, pr_row + 1, "Unknown parameter!")
                buf, selected = "", None
            else:
                buf = ""
            continue

        done, buf = prompt(stdscr, pr_row,
                           f"New value for {selected}: ", buf)
        if not done:
            continue
        val, err = validate(selected, buf)
        if err:
            flash(stdscr, pr_row + 1, err)
            buf, selected = "", None
            continue

        upsert_value(SESSION_ID, selected, TEAM_ID, val)
        publish({"param": selected, "team": TEAM_ID, "session": SESSION_ID})

        buf, selected = "", None


if __name__ == "__main__":
    curses.wrapper(main)

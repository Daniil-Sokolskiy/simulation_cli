import argparse, curses, time
from src.core.validators import validate
from src.core.session import (
    get_or_create_session, fetch_table,
    upsert_value, set_ok, everyone_ok, close_session
)
from src.infrastructure.redis_helper import r, get_message, publish, PUBSUB_CHANNEL
from src.infrastructure.tui import tui, init_curses, draw_table
from src.utils.prompt import prompt

SUCCESS_MSG = "Success! Closing in 2 seconds…"

parser = argparse.ArgumentParser()
parser.add_argument("--game", type=int, choices=(1, 2), default=1)
GAME = parser.parse_args().game
TEAM_ID = 2
SESSION_ID = get_or_create_session(GAME)


def flash(stdscr, row: int, msg: str) -> None:
    stdscr.move(row, 0)
    stdscr.clrtoeol()
    stdscr.addstr(row, 0, msg, curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh(); time.sleep(1)


def main(stdscr):
    init_curses(stdscr)
    buf = ""
    pubsub = r.pubsub(); pubsub.subscribe(PUBSUB_CHANNEL)

    while True:
        if (msg := get_message(pubsub)) and msg.get("cmd") == "QUIT":
            stdscr.addstr(0, 0, SUCCESS_MSG, curses.color_pair(2))
            stdscr.refresh(); time.sleep(2); break

        rows = fetch_table(SESSION_ID)              
        idx_map = {str(i): n for i, (n, *_ ) in enumerate(rows, 1)}
        draw_table(
            stdscr, rows,
            f"Team 2 — Game {GAME}",
            two_teams=(GAME == 2)
        )

        if GAME == 1:
            from src.core.formulas import valuation
            mapping = {n: v1 for n, _, v1, *_ in rows}
            v = valuation(mapping)
            if v is not None:
                stdscr.addstr(len(rows) + 3, 0, f"Valuation: {v:,.2f}")
        stdscr.refresh()

        pr_row = len(rows) + 5
        prompt_txt = (
            "[idx] OK | e idx val | q: " if GAME == 2
            else "Idx to OK (q-quit): "
        )
        done, buf = prompt(stdscr, pr_row, prompt_txt, buf)
        if not done:
            continue
        if buf.lower() == "q":
            break

        tokens = buf.split(maxsplit=2)

        if GAME == 2 and tokens and tokens[0] == "e":
            if len(tokens) != 3:
                flash(stdscr, pr_row + 1, "Usage: e idx value")
                buf = ""; continue
            key, val_txt = tokens[1], tokens[2]
            name = idx_map.get(key) or key
            if name not in idx_map.values():
                flash(stdscr, pr_row + 1, "Unknown parameter!")
                buf = ""; continue
            val, err = validate(name, val_txt)
            if err:
                flash(stdscr, pr_row + 1, err)
            else:
                upsert_value(SESSION_ID, name, TEAM_ID, val)
                publish({"param": name, "team": TEAM_ID, "session": SESSION_ID})
            buf = ""; continue

        key = tokens[0]
        name = idx_map.get(key) or key
        if name not in idx_map.values():
            flash(stdscr, pr_row + 1, "Unknown parameter!")
            buf = ""; continue

        row = next(r for r in rows if r[0] == name)  # name, unit, v1, v2, status
        no_value = (
            GAME == 1 and row[2] is None or
            GAME == 2 and row[2] is None )
        if no_value:
            flash(stdscr, pr_row + 1, "No value yet!")
            buf = ""; continue
        if row[4] == "OK":
            flash(stdscr, pr_row + 1, "Already OK!")
            buf = ""; continue

        set_ok(SESSION_ID, name)
        publish({"param": name, "team": TEAM_ID, "session": SESSION_ID})

        if everyone_ok(SESSION_ID):
            rows = fetch_table(SESSION_ID)
            draw_table(stdscr, rows, f"Team 2 — Game {GAME}", two_teams=(GAME == 2))
            stdscr.refresh()

            close_session(SESSION_ID)
            publish({"cmd": "QUIT", "session": SESSION_ID})

            stdscr.addstr(0, 0, SUCCESS_MSG, curses.color_pair(2))
            stdscr.refresh(); time.sleep(2); break

        buf = ""


if __name__ == "__main__":
    curses.wrapper(main)

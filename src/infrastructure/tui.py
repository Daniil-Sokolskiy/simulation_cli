import curses
from contextlib import contextmanager
from typing import Iterable, Tuple, Optional

__all__ = ["tui", "init_curses", "draw_table", "TRow"]

@contextmanager
def tui() -> "curses._CursesWindow":  
    stdscr = curses.initscr()
    try:
        yield stdscr
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


def init_curses(stdscr: "curses._CursesWindow") -> None:  
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW, -1)  # TBD
    curses.init_pair(2, curses.COLOR_GREEN,  -1)  # OK
    curses.init_pair(3, curses.COLOR_RED,    -1)  # error/info
    stdscr.nodelay(True)
    stdscr.timeout(300)

# name, unit, v1, v2, status
TRow = Tuple[str, Optional[str], Optional[object], Optional[object], str]


def draw_table(
    stdscr,
    rows: Iterable[TRow],
    title: str,
    *,
    two_teams: bool = True,
) -> None:
    stdscr.clear()
    stdscr.addstr(0, 0, title.center(70), curses.A_BOLD)

    if two_teams:
        header = f"{'Idx':>3} {'Name':15} {'Unit':>4} {'T1':>10} {'T2':>10} Status"
    else:
        header = f"{'Idx':>3} {'Name':15} {'Unit':>4} {'Value':>10} Status"
    stdscr.addstr(1, 0, header, curses.A_UNDERLINE)

    for i, (name, unit, v1, v2, status) in enumerate(rows, 1):
        v1s = f"{v1}" if v1 is not None else "-"
        v2s = f"{v2}" if v2 is not None else "-"
        status_show = status or "TBD"
        color = curses.color_pair(2) if status_show == "OK" else curses.color_pair(1)

        if two_teams:
            line = f"{i:>3} {name:15} {unit or '':>4} {v1s:>10} {v2s:>10} {status_show}"
        else:
            line = f"{i:>3} {name:15} {unit or '':>4} {v1s:>10} {status_show}"
        stdscr.addstr(1 + i, 0, line, color)

    stdscr.refresh()

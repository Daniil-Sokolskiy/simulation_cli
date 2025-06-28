import curses
from typing import Tuple

def prompt(stdscr, row: int, text: str, buf: str = "") -> Tuple[bool, str]:
    stdscr.move(row, 0); stdscr.clrtoeol(); stdscr.addstr(row, 0, text + buf)
    stdscr.refresh(); ch = stdscr.getch()
    if ch in (10, 13):
        return True, buf.strip()
    if ch in (8, 127):
        return False, buf[:-1]
    if 0 <= ch < 256:
        return False, buf + chr(ch)
    return False, buf
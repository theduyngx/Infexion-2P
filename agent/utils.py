"""
Module:
    ``utils.py``

Purpose:
    Utility functions for program.

Notes:
    Utility functions include printing the referee data, including time and space remaining available
    for a specific game-playing agent (in which it cannot exceed), and applying ansi color to text for
    beautifying printing.
"""

from referee.game import PlayerColor
from referee.log import LogColor


def print_referee(referee: dict):
    """
    Print referee data.
    Args:
        referee: the referee
    """
    bg    = LogColor.BLACK_BG
    txt   = LogColor.CYAN
    escp  = "\033[0m"
    time  = referee["time_remaining"]
    space = referee["space_remaining"]
    time  = round(time, 6) if time is not None else time
    space = round(space, 6) if space is not None else space
    logs  = f"  {bg}--------------------------------------{escp}\n" \
            f"  {txt}Time remaining  (s)  : {time}{escp}\n" \
            f"  {txt}Space remaining (Mb) : {space}{escp}\n" \
            f"  {bg}--------------------------------------{escp}"
    print(logs)


def ansi_color(color: PlayerColor, ansi=True) -> str:
    """
    Apply ansi formatting to player's color.

    Args:
        color: player's color
        ansi : whether to apply ansi

    Returns:
        formatted string
    """
    color_print = color
    if ansi:
        bold_code = "\033[1m"
        color_ansi = ""
        match color:
            case PlayerColor.RED:
                color_ansi = LogColor.RED
            case PlayerColor.BLUE:
                color_ansi = LogColor.BLUE
        color_print = f"  {bold_code}{color_ansi}{color}\033[0m"
    return color_print

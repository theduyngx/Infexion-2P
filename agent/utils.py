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

from .referee.game import PlayerColor


def print_referee(referee: dict):
    """
    Print referee data. Space remaining sometimes works, sometimes doesn't. Though most of the time
    it does work, so I suppose it's fine.
    @param referee : the referee
    """
    print("--------------------------------------")
    print("Time remaining  :", referee["time_remaining"])
    print("Space remaining :", referee["space_remaining"])
    print("--------------------------------------")


def ansi_color(color: PlayerColor, ansi=True) -> str:
    """
    Apply ansi formatting to player's color.
    @param color : player's color
    @param ansi  : whether to apply ansi
    @return      : formatted string
    """
    color_print = color
    if ansi:
        bold_code = "\033[1m"
        match color:
            case PlayerColor.RED:
                color_print = f"{bold_code}\033[31m{color}\033[0m"
            case PlayerColor.BLUE:
                color_print = f"{bold_code}\033[34m{color}\033[0m"
    return color_print

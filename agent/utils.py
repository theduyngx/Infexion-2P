"""
Module:
    ``utils.py``

Purpose:
    Utility functions for program.

Notes:
    Utility functions include printing the referee data, including time and space remaining available
    for a specific game-playing agent (in which it cannot exceed). Ansi-color formatting has now been
    fully delegated to referee.
"""

from referee.game import PlayerColor
from referee.log import LogColor


def print_referee(referee: dict):
    """
    Print referee data.
    Args:
        referee: the referee
    """
    color = LogColor.CYAN
    escp  = LogColor.ESCAPE
    time  = referee["time_remaining"]
    space = referee["space_remaining"]
    time_format  = '{:09.6f}'.format(round(time , 6)) if time is not None else time
    space_format = '{:09.6f}'.format(round(space, 6)) if space is not None else space
    logs  = f"  {color}---------------------------------{escp}\n" \
            f"  {color}Time remaining  (s)  : {time_format}{escp}\n" \
            f"  {color}Space remaining (Mb) : {space_format}{escp}\n" \
            f"  {color}---------------------------------{escp}"
    print(logs)

"""
Module:
    ``utils.py``

Authors:
    The Duy Nguyen (1100548)

Purpose:
    Utility functions for program.

Notes:
    Utility functions include printing the referee data, including time and space remaining available
    for a specific game-playing agent (in which it cannot exceed). Ansi-color formatting has now been
    fully delegated to referee.
"""


def print_referee(referee: dict):
    """
    Print referee data.
    Args:
        referee: the referee
    """
    time  = referee["time_remaining"]
    space = referee["space_remaining"]
    time_format  = '{:09.6f}'.format(round(time , 6)) if time is not None else time
    space_format = '{:09.6f}'.format(round(space, 6)) if space is not None else space
    logs  = f"  ---------------------------------\n" \
            f"  Time remaining  (s)  : {time_format}\n" \
            f"  Space remaining (Mb) : {space_format}\n" \
            f"  ---------------------------------"
    print(logs)

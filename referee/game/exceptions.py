"""
Module:
    ``exceptions.py``

Purpose:
    Exceptions and for elegant exception handling and more useful exception messages.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package.
"""


class PlayerException(Exception):
    """
    Raised when a player does something illegal to result in
    a premature end to the game.
    """


class IllegalActionException(PlayerException):
    """
    Action is illegal based on the current board state.
    """

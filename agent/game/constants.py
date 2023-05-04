"""
    Module  : constants.py
    Purpose : Storing global constants.
"""

from referee.game import PlayerColor

INF             : float = float("inf")
DEPTH           : int = 4
EMPTY_POWER     : int = 0
MIN_MOVE_WIN    : int = 2
MIN_TURN_COUNT  : int = 2
MIN_TOTAL_POWER : int = 10
PLAYER_COLOR    : PlayerColor = PlayerColor.RED
OPPONENT_COLOR  : PlayerColor = PLAYER_COLOR.opponent
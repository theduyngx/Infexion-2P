"""
    Module  : search.py
    Purpose : Search algorithm to find the next best move for agent.

This may use a hybrid of Minimax and Monte Carlo tree search algorithms to produce more quality
results by improving accuracy. So far, it is only using Minimax.
"""

from referee.game import PlayerColor, Action, SpawnAction, HexPos
from agent.game import Board, DEPTH
from .minimax import minimax


def search(board: Board, color: PlayerColor) -> Action:
    """
    Search the best subsequent move for agent. It will be using a hybrid of search algorithms and
    pruning techniques, namely Minimax and Monte Carlo tree search algorithms.
    @param board : the board
    @param color : the agent's color
    @return      : the action to take for agent
    """
    if board.turn_count < 1:
        return SpawnAction(HexPos(3, 3))
    return minimax(board, DEPTH, color, full=False)

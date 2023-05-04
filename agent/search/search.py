"""
    Module  : search.py
    Purpose : Search algorithm to find the next best move for agent.

This may use a hybrid of Minimax and Monte Carlo tree search algorithms to produce more quality
results by improving accuracy. So far, it is only using Minimax.
"""

from referee.game import PlayerColor, Action, SpawnAction, HexPos, HexDir
from agent.game import Board, DEPTH
from .minimax import minimax


def search(board: Board, color: PlayerColor, depth=DEPTH, full=False) -> Action:
    """
    Search the best subsequent move for agent. It will be using a hybrid of search algorithms and
    pruning techniques, namely Minimax and Monte Carlo tree search algorithms.
    @param board : the board
    @param color : the agent's color
    @param depth : temporary debug depth
    @param full  : temporary debug mode for move reduction
    @return      : the action to take for agent
    """
    if board.turn_count < 1:
        return SpawnAction(HexPos(3, 3))
    elif board.turn_count < 2:
        for cell in board.get_cells():
            pos = cell.pos
            if not board.pos_occupied(pos) and all([not board.pos_occupied(pos + dir) for dir in HexDir]):
                return SpawnAction(pos)
    return minimax(board, depth, color, full)
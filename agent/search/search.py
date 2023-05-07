"""
Module:
    ``search.py``

Purpose:
    Search algorithm to find the next best move for agent.

Notes:
    The search approach uses Negamax algorithm with alpha-beta pruning and variety of other
    optimization methods to improve performance without sacrificing too much accuracy.
"""

from referee.game import PlayerColor, Action, SpawnAction, HexPos, HexDir
from ..game import Board, DEPTH
from .minimax import negamax, negascout


def search(board: Board, color: PlayerColor) -> Action:
    """
    Search the best subsequent move for agent. It will be using a pruned and highly optimized
    Negamax search algorithm, which is a Minimax-variant algorithm.
    Args:
        board: the board
        color: the agent's color
    Returns:
        the action to take for agent
    """
    if board.turn_count < 1:
        return SpawnAction(HexPos(3, 3))
    elif board.turn_count < 2:
        for cell in board.get_cells():
            pos = cell.pos
            if not board.pos_occupied(pos) and all([not board.pos_occupied(pos + dir) for dir in HexDir]):
                return SpawnAction(pos)
    return negascout(board, DEPTH, color, full=False)

"""
Module:
    ``search.py``

Authors:
    The Duy Nguyen (1100548)

Purpose:
    Search algorithm to find the next best move for agent.

Notes:
    The search approach uses Negamax algorithm with alpha-beta pruning and variety of other
    optimization methods to improve performance without sacrificing too much accuracy. It is
    important to note that the search algorithm will switch to a simpler agent under time
    pressure, and is able to control allowed time per move before cut-off.
"""

from referee.game import PlayerColor, Action, SpawnAction, HexPos, HexDir
from ..game import Board
from .negamax import negamax, TIME_LIMIT_PER_MOVE

# Depth limit for NegaScout
DEPTH         : int   = 4
REDUCED_DEPTH : int   = 2
MIN_TIME_DIFF : float = 5
TIME_THRESHOLD: float = 15


def search(board: Board, color: PlayerColor, player_time) -> Action:
    """
    Search the best subsequent move for agent. It will be using a pruned and highly optimized
    Negamax search algorithm, which is a Minimax-variant algorithm.

    Args:
        board       : the board
        color       : the agent's color
        player_time : agent's remaining time

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

    # desperation not under time pressure yet, but under allowed move time
    depth = DEPTH
    if player_time is not None:
        if player_time <= TIME_THRESHOLD:
            depth = REDUCED_DEPTH
        if player_time <= TIME_LIMIT_PER_MOVE + MIN_TIME_DIFF:
            return negamax(board, depth, color, full=False, time_lim = TIME_LIMIT_PER_MOVE - MIN_TIME_DIFF)
    return negamax(board, depth, color, full=False)

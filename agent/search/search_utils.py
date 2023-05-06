"""
Module:
    ``search_utils.py``

Purpose:
    Utility functions for search algorithms. For now, it only includes getting all
    legal moves for a given player.

Notes:
"""

from ..game import Board
from referee.game import HexDir, PlayerColor, Action, SpawnAction, SpreadAction, MAX_TOTAL_POWER


def get_legal_moves(board: Board, color: PlayerColor) -> list[Action]:
    """
    Get all possible legal moves of a specified player color from a specific state of the board.
    There are several optimizations made for this function in order reduce the number of legal
    moves had to be generated in the minimax tree. This includes endgame detection and ignoring
    specific moves based on domain knowledge of the game.
    However, in the case when player is overwhelmed, then full will be forcefully set to True.

    Parameters:
        board : specified board
        color : specified player's color
    Returns:
        list of all actions that could be applied to board,
        and boolean indicating whether endgame has been reached
    """

    # if the actual player side is being overwhelmed, forcefully get all legal moves possible
    actions: list[Action] = []

    # for every possible move from a given board state, including SPAWN and SPREAD
    for cell in board.get_cells():

        # append spawn actions - always add when full, otherwise add on condition
        pos = cell.pos
        if not board.pos_occupied(pos):
            if board.total_power() < MAX_TOTAL_POWER:
                actions.append(SpawnAction(pos))

        # append spread actions for every direction
        elif board[pos].color == color:
            actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    assert len(actions) > 0
    return actions

"""
Module:
    ``negamax.py``

Purpose:
    The Negamax search algorithm to find the best next move for the agent, with alpha-beta
    pruning to improve performance.

Notes:
    Negamax algorithm, to reach further depth requires a variety of different optimization methods
    introduced in ``negamax_utils.py``.
"""

from referee.game import PlayerColor, Action
from ...game import Board, assert_action, INF, DEPTH
from .evaluation import evaluate
from .negamax_utils import get_optimized_legal_moves, move_ordering


def negamax(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    Negamax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn. There's no performance difference between negamax
    and minimax, however.

    Args:
        board: the board
        depth: the search depth limit
        color: the agent's color
        full : whether agent uses reduced-moves minimax

    Returns:
        the action to take for agent
    """
    alpha = -INF
    beta  = INF
    assert not board.game_over
    _, action, _ = alphabeta_negamax(board, color, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta_negamax(board  : Board,
                      color  : PlayerColor,
                      depth  : int,
                      action : Action,
                      alpha  : float,
                      beta   : float,
                      full   = False,
                      ) -> (float, Action, bool):
    """
    Alpha-beta pruning for Negamax search algorithm.

    Args:
        board  : the board
        color  : the current turn of player, specified by player's color
        depth  : the current depth in the search tree
        action : most recent action made to reach the current board state
        alpha  : move that improves player's position
        beta   : move that improves opponent's position
        full   : whether agent uses reduced-moves minimax,
                 `True` if in move reduction optimization mode,
                 `False` if requiring all legal moves

    Returns:
        evaluated score of the board and the action to be made
    """
    # reached depth limit, or terminal node
    stop  = False
    ret   = None
    value = 0
    if depth == 0 or board.game_over:
        stop = depth >= DEPTH - 1
        assert_action(action)
        return evaluate(board), action, stop

    # for each child node of board
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves
    for possible_action in ordered_moves:

        # apply action
        board.apply_action(possible_action, concrete=False)
        curr_val, _, stop = alphabeta_negamax(board, color.opponent, depth-1, possible_action,
                                              -beta, -alpha, full)
        curr_val = -curr_val
        # undo after finishing
        board.undo_action()
        if curr_val > value or ret is None:
            value = curr_val
            ret = possible_action
        alpha = max(alpha, value)

        # cutoff / stop prematurely
        if stop or alpha >= beta:
            break

    # return evaluated value and corresponding action
    return value, ret, stop

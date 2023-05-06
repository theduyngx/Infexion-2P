"""
Module:
    ``minimax.py``

Purpose:
    The minimax search algorithm to find the best next move for the agent, with alpha-beta
    pruning to improve performance.

Notes:
    Minimax algorithm, to reach further depth requires a variety of different optimization methods
    introduced in ``minimax_utils.py``.
"""

from referee.game import PlayerColor, Action
from ...game import Board, assert_action, INF, DEPTH
from .evaluation import evaluate
from .minimax_utils import get_optimized_legal_moves, move_ordering


def minimax(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    Minimax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn.
    NOTE: be mindful of the behavior specifically specified in Infexion ver 1.1

    Parameters
    ----------
    board: Board
        the board
    depth: int
        the search depth limit
    color: PlayerColor
        the agent's color
    full: bool
        whether agent uses reduced-moves minimax

    Returns
    -------
    Action
        the action to take for agent
    """
    alpha = -INF
    beta  = INF
    assert not board.game_over
    _, action, _ = alphabeta(board, color, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta(board  : Board,
              color  : PlayerColor,
              depth  : int,
              action : Action,
              alpha  : float,
              beta   : float,
              full   = False,
              ) -> (float, Action, bool):
    """
    Alpha-beta pruning for minimax search algorithm.

    Parameters
    ----------
    board: Board
        the board
    color: PlayerColor
        the current turn of player, specified by player's color
    depth: int
        the current depth in the search tree
    action: Action
        deduced best action
    alpha: float
        move that improves player's position
    beta: float
        move that improves opponent's position
    full: bool
        whether agent uses reduced-moves minimax,
        `True` if in move reduction optimization mode, `False` if requiring all legal moves

    Returns
    -------
    float
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

    # maximize
    if color == PlayerColor.RED:
        legal_moves, endgame = get_optimized_legal_moves(board, color, full)
        ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves

        # for each child node of board
        for possible_action in ordered_moves:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _, stop = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta, full)

            # undo after finishing
            board.undo_action()
            if curr_val > value or ret is None:
                value = curr_val
                ret   = possible_action
            alpha = max(alpha, value)

            # beta cutoff / stop prematurely
            if stop or value >= beta:
                break

    # minimize
    else:
        legal_moves, endgame = get_optimized_legal_moves(board, color, full)
        ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves
        # for each child node of board
        for possible_action in ordered_moves:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _, stop = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta, full)

            # undo action after finishing
            board.undo_action()
            if curr_val < value or ret is None:
                value = curr_val
                ret   = possible_action
            beta = min(beta, value)

            # alpha cutoff / stop prematurely
            if stop or value <= alpha:
                break

    # return evaluated value and corresponding action
    return value, ret, stop

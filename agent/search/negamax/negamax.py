"""
Module:
    ``negamax.py``

Purpose:
    The Negamax (and NegaScout) search algorithm to find the best next move for the agent,
    with alpha-beta pruning.

Notes:
    Negamax (and NegaScout) algorithm, to reach further depth requires a variety of different
    optimization methods introduced in ``minimax_utils.py``.
"""

from referee.game import PlayerColor, Action
from ...game import Board, assert_action, INF
from .evaluation import evaluate, MAXIMIZE_PLAYER
from .minimax_utils import get_optimized_legal_moves, move_ordering

# Constants
NULL_WINDOW: float = 1


def negamax(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    Negamax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn. There's no performance difference between negamax
    and minimax, however.

    Args:
        board: the board
        depth: the search depth limit
        color: the agent's color
        full : * `True` to set move reduction optimization,
               * `False` to get actual all possible legal moves

    Returns:
        the action to take for agent
    """
    alpha = -INF
    beta = INF
    _, action, _ = alphabeta_negamax(board, color, depth, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta_negamax(board  : Board,
                      color  : PlayerColor,
                      depth  : int,
                      ceil   : int,
                      action : Action,
                      alpha  : float,
                      beta   : float,
                      full   = False,
                      ) -> (float, Action, bool):
    """
    Alpha-beta pruning for Negamax search algorithm.

    Note: Unlike Minimax alpha-beta pruning, it will only have to check once for the player's
    color to determine whether to maximize or minimize. At every subsequent backtrack, it only
    has to assign negation to that score. This makes alpha-beta for Negamax more elegant.

    Args:
        board  : the board
        color  : the current turn of player, specified by player's color
        depth  : the current depth in the search tree
        ceil   : top depth level
        action : most recent action made to reach the current board state
        alpha  : move that improves player's position
        beta   : move that improves opponent's position
        full   : * `True` to set move reduction optimization,
                 * `False` to get actual all possible legal moves

    Returns:
        * evaluated score of the board and the action to be made
        * the action to be taken
        * boolean premature stopping condition
    """
    # reached depth limit, or terminal node
    ret   = None
    stop  = False
    score = 0
    if depth == 0 or board.game_over:
        stop = depth >= ceil - 1
        sign = 1 if color == MAXIMIZE_PLAYER else -1
        return sign * evaluate(board), action, stop

    # for each child node of board
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves
    for action in ordered_moves:

        # apply action
        board.apply_action(action, concrete=False)
        curr_val, _, stop = alphabeta_negamax(board, color.opponent, depth - 1, ceil, action,
                                              -beta, -alpha, full)
        curr_val = -curr_val
        # undo after finishing
        board.undo_action()
        if curr_val > score or ret is None:
            score = curr_val
            ret = action
        alpha = max(alpha, score)

        # cutoff / stop prematurely
        if stop or alpha >= beta:
            break

    # return evaluated score and corresponding action
    return score, ret, stop


def negascout(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    NegaScout search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn. It is an enhanced version of Negamax, which makes use
    of good move ordering and narrow search window to more effectively prune unlikely good nodes.

    Args:
        board: the board
        depth: the search depth limit
        color: the agent's color
        full : * `True` to set move reduction optimization,
               * `False` to get actual all possible legal moves

    Returns:
        the action to take for agent
    """
    alpha = -INF
    beta  = INF
    _, action, _ = alphabeta_pvs(board, color, depth, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta_pvs(board  : Board,
                  color  : PlayerColor,
                  depth  : int,
                  ceil   : int,
                  action : Action,
                  alpha  : float,
                  beta   : float,
                  full   = False,
                  ) -> (float, Action, bool):
    """
    Alpha-beta pruning for NegaScout, or Principle Variation Search algorithm.

    Args:
        board  : the board
        color  : the current turn of player, specified by player's color
        depth  : the current depth in the search tree
        ceil   : top depth level
        action : most recent action made to reach the current board state
        alpha  : move that improves player's position
        beta   : move that improves opponent's position
        full   : * `True` to set move reduction optimization,
                 * `False` to get actual all possible legal moves

    Returns:
        * evaluated score of the board and the action to be made
        * the action to be taken
        * boolean premature stopping condition
    """
    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        stop = depth >= ceil - 1
        sign = 1 if color == MAXIMIZE_PLAYER else -1
        return sign * evaluate(board), action, stop

    # for each child node of board
    # debug = depth == ceil
    debug = False
    legal_moves, endgame = get_optimized_legal_moves(board, color, full, debug)
    ordered_moves = move_ordering(board, color, legal_moves, debug) if not endgame else legal_moves

    ret : Action = None
    stop: bool   = False
    b = beta
    score = -INF
    for possible_action in ordered_moves:
        board.apply_action(possible_action, concrete=False)
        curr, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, ceil, possible_action,
                                       -b, -alpha, full)
        curr = -curr

        if curr > score:
            if b == beta or ret is NoneZ:
                score = curr
                ret = possible_action
            else:
                score, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, ceil, possible_action,
                                               -beta, -curr, full)
                score = -score

        # undo after finishing
        board.undo_action()

        # update alpha (maximize score) and return action
        if score > alpha:
            alpha = score
            ret = possible_action

        # cutoff / stop prematurely, and update search window
        if alpha >= beta or stop:
            break
        b = alpha + 1

    # return evaluated score and corresponding action
    return alpha, ret, stop

"""
Module:
    ``negamax.py``

Authors:
    The Duy Nguyen (1100548)

Purpose:
    The Negamax (and NegaScout) search algorithm to find the best next move for the agent,
    with alpha-beta pruning.

Notes:
    Negamax (and NegaScout) algorithm, to reach further depth requires a variety of different
    optimization methods introduced in ``minimax_utils.py``.
|
References:
    Reinefeld, A. (1983). `An Improvement to the Scout Tree-Search Algorithm`
    [Journal of the International Computer Games Association] https://doi.org/10.3233/ICG-1983-6402
"""

from time import time
from referee.game import PlayerColor, Action
from ...game import Board, assert_action, INF
from .evaluation import evaluate, MAXIMIZE_PLAYER
from .minimax_utils import get_optimized_legal_moves, move_ordering

# Constants
NULL_WINDOW: float = 1
TIME_LIMIT_PER_MOVE: float = 18


def negamax(board: Board, depth: int, color: PlayerColor, full=False, time_lim=TIME_LIMIT_PER_MOVE) -> Action:
    """
    Negamax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn. There's no performance difference between negamax
    and minimax, however.

    Args:
        board    : the board
        depth    : the search depth limit
        color    : the agent's color
        full     : * `True` to set move reduction optimization,
                   * `False` to get actual all possible legal moves
        time_lim : the maximum allowed time to return an action

    Returns:
        the action to take for agent
    """
    alpha = -INF
    beta  = INF
    timer = time()
    _, action, _ = alphabeta_negamax(board, color, depth, depth, None, alpha, beta, timer, full, time_lim)
    assert_action(action)
    return action


def alphabeta_negamax(board    : Board,
                      color    : PlayerColor,
                      depth    : int,
                      ceil     : int,
                      action   : Action,
                      alpha    : float,
                      beta     : float,
                      timer    : float,
                      full     = False,
                      time_lim = TIME_LIMIT_PER_MOVE
                      ) -> (float, Action, bool):
    """
    Alpha-beta pruning for Negamax search algorithm.

    Note: Unlike Minimax alpha-beta pruning, it will only have to check once for the player's
    color to determine whether to maximize or minimize. At every subsequent backtrack, it only
    has to assign negation to that score. This makes alpha-beta for Negamax more elegant.

    Args:
        board    : the board
        color    : the current turn of player, specified by player's color
        depth    : the current depth in the search tree
        ceil     : top depth level
        action   : most recent action made to reach the current board state
        alpha    : move that improves player's position
        beta     : move that improves opponent's position
        timer    : the timer, it will end prematurely if it exceeds a specific amount of allowed time
        full     : * `True` to set move reduction optimization,
                   * `False` to get actual all possible legal moves
        time_lim : the maximum allowed time to return an action

    Returns:
        * evaluated score of the board and the action to be made
        * the action to be taken
        * boolean premature stopping condition
    """
    # reached depth limit, or terminal node
    ret   = None
    score = 0           # arbitrary score which will be changed later anyway, as long ret is None
    end   = time()
    stop  = end - timer >= time_lim
    if depth == 0 or board.game_over or stop:
        stop = depth >= ceil - 1 or stop
        sign = 1 if color == MAXIMIZE_PLAYER else -1
        return sign * evaluate(board), action, stop

    # for each child node of board
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves
    for action in ordered_moves:

        # apply action
        board.apply_action(action, concrete=False)
        curr, _, stop = alphabeta_negamax(board, color.opponent, depth - 1, ceil, action,
                                          -beta, -alpha, timer, full)
        curr = -curr
        # undo after finishing
        board.undo_action()

        # update score and, likewise, alpha
        if curr > score or ret is None:
            score = curr
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

    |
    References:
        Reinefeld, A. (1983). `An Improvement to the Scout Tree-Search Algorithm`
        [Journal of the International Computer Games Association] https://doi.org/10.3233/ICG-1983-6402

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
    Alpha-beta pruning for NegaScout, or Principle Variation Search algorithm. As stated above,
    NegaScout will use narrower search window first as an estimate to quickly confirm or reject
    full window search expansions. This gives it a better worst case performance than normal
    alpha-beta pruning.

    |
    References:
        Reinefeld, A. (1983). `An Improvement to the Scout Tree-Search Algorithm`
        [Journal of the International Computer Games Association] https://doi.org/10.3233/ICG-1983-6402

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

    # generating optimized moves and order them
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves

    # for each child node of board
    b    = beta
    ret  : Action = None
    stop : bool   = False
    for action in ordered_moves:

        # search with updated search window a and b
        board.apply_action(action, concrete=False)
        score, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, ceil, action,
                                       -b, -alpha, full)
        score = -score

        # first action - estimated best action
        if action is ordered_moves[0]:
            ret = action

        # subsequent actions - if within range, search full alpha-beta window
        elif alpha < score < beta:
            score, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, ceil, action,
                                           -beta, -alpha, full)
            score = -score

        # undo after finishing
        board.undo_action()

        # update alpha (maximize score) and return action
        if score > alpha:
            alpha = score
            ret   = action

        # cutoff / stop prematurely, and update search window
        if alpha >= beta or stop:
            break
        b = alpha + NULL_WINDOW

    # return evaluated score and corresponding action
    return alpha, ret, stop

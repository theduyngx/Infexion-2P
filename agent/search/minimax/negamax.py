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
from .evaluation import evaluate, MAXIMIZE_PLAYER
from .minimax_utils import get_optimized_legal_moves, move_ordering


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
    beta = INF
    assert not board.game_over
    _, action, _ = alphabeta_negamax(board, color, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta_negamax(board: Board,
                      color: PlayerColor,
                      depth: int,
                      action: Action,
                      alpha: float,
                      beta: float,
                      full=False,
                      ) -> (float, Action, bool):
    """
    Alpha-beta pruning for Negamax search algorithm.

    Note: Unlike Minimax alpha-beta pruning, it will only have to check once for the player's
    color to determine whether to maximize or minimize. At every subsequent backtrack, it only
    has to assign negation to that value. This makes alpha-beta for Negamax more elegant.

    Args:
        board  : the board
        color  : the current turn of player, specified by player's color
        depth  : the current depth in the search tree
        action : most recent action made to reach the current board state
        alpha  : move that improves player's position
        beta   : move that improves opponent's position
        full   : * `True` to set move reduction optimization,
                 * `False` to get actual all possible legal moves

    Returns:
        evaluated score of the board and the action to be made
    """
    # reached depth limit, or terminal node
    stop = False
    ret = None
    value = 0
    if depth == 0 or board.game_over:
        stop = depth >= DEPTH - 1
        sign = 1 if color == MAXIMIZE_PLAYER else -1
        return sign * evaluate(board), action, stop

    # for each child node of board
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves
    for possible_action in ordered_moves:

        # apply action
        board.apply_action(possible_action, concrete=False)
        curr_val, _, stop = alphabeta_negamax(board, color.opponent, depth - 1, possible_action,
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


def negascout(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    NegaScout search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn. It is an enhanced version of Negamax, which uses
    iterative deepening and a good move ordering to produce better performance with no sacrifice
    to accuracy.

    Args:
        board: the board
        depth: the search depth limit
        color: the agent's color
        full : whether agent uses reduced-moves minimax

    Returns:
        the action to take for agent
    """
    alpha = -INF
    beta = INF
    assert not board.game_over
    _, action, _ = alphabeta_pvs(board, color, depth, None, alpha, beta, full)
    assert_action(action)
    return action


def alphabeta_pvs(board: Board,
                  color: PlayerColor,
                  depth: int,
                  action: Action,
                  alpha: float,
                  beta: float,
                  full=False,
                  ) -> (float, Action, bool):
    """
    Alpha-beta pruning for NegaScout, or Principle Variation Search algorithm.

    Note: Unlike Negamax, it will have a narrower search window, and first initially uses iterative
    deepening with the assumption that the first node should be the best node. With this assumption,
    it is possible to make the search a lot faster with actual good move ordering without having to
    explore as many nodes as Negamax alpha-beta pruning would have had to.

    Args:
        board  : the board
        color  : the current turn of player, specified by player's color
        depth  : the current depth in the search tree
        action : most recent action made to reach the current board state
        alpha  : move that improves player's position
        beta   : move that improves opponent's position
        full   : * `True` to set move reduction optimization,
                 * `False` to get actual all possible legal moves

    Returns:
        evaluated score of the board and the action to be made
    """
    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        stop = depth >= DEPTH - 1
        sign = 1 if color == MAXIMIZE_PLAYER else -1
        return sign * evaluate(board), action, stop

    # for each child node of board
    legal_moves, endgame = get_optimized_legal_moves(board, color, full)
    ordered_moves = move_ordering(board, color, legal_moves) if not endgame else legal_moves

    # apply first action
    first_move = ordered_moves[0]
    board.apply_action(first_move, concrete=False)
    value, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, first_move, -beta, -alpha, full)
    value = -value
    # undo after finishing
    board.undo_action()

    ret = first_move
    if alpha < value < beta:
        for possible_action in ordered_moves[1:]:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, possible_action,
                                              -alpha - 1, -alpha, full)
            curr_val = -curr_val
            # undo after finishing
            board.undo_action()

            if alpha < curr_val < beta:
                # apply action
                board.apply_action(possible_action, concrete=False)
                curr_val, _, stop = alphabeta_pvs(board, color.opponent, depth - 1, possible_action,
                                                  -beta, -curr_val, full)
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

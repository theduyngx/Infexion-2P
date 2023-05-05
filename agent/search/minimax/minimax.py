"""
    Module  : minimax.py
    Purpose : The minimax search algorithm to find the best next move for the agent,
              with alpha-beta pruning to improve performance.
"""

from referee.game import PlayerColor, Action
from agent.game import Board, assert_action, INF, DEPTH
from .evaluation import evaluate
from .minimax_utils import get_legal_moves, move_ordering


def minimax(board: Board, depth: int, color: PlayerColor, full=False) -> Action:
    """
    Minimax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn.

    NOTE: be mindful of the behavior specifically specified in Infexion ver 1.1
    @param board : the board
    @param depth : the depth
    @param color : the agent's color
    @param full  : whether agent uses reduced-moves minimax
    @return      : the action to take for agent
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
    @param board  : the board
    @param color  : the current turn of player, specified by player's color
    @param depth  : the current depth in the search tree
    @param action : deduced best action
    @param alpha  : alpha - move that improves player's position
    @param beta   : beta  - move that improves opponent's position
    @param full   : whether agent uses reduced-moves minimax
    @return       : evaluated score of the board and the action to be made
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
        legal_moves, endgame = get_legal_moves(board, color, full)
        ordered_map = move_ordering(board, color, legal_moves) if not endgame else legal_moves
        # for each child node of board
        for possible_action in ordered_map:

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
        legal_moves, endgame = get_legal_moves(board, color, full)
        ordered_map = move_ordering(board, color, legal_moves) if not endgame else legal_moves
        # for each child node of board
        for possible_action in ordered_map:

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

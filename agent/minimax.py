"""
    Module  : minimax.py
    Purpose : The minimax search algorithm to find the best next move for the agent,
              with alpha-beta pruning to improve performance.
"""

from referee.game import PlayerColor, Action, SpawnAction, SpreadAction
from .board import Board
from .evaluation import evaluate
from .constants import INF
from .search_utils import get_legal_moves


def minimax(board: Board, depth: int, color: PlayerColor) -> Action:
    """
    Minimax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn.

    NOTE: be mindful of the behavior specifically specified in Infexion ver 1.1
    @param board : the board
    @param depth : the depth
    @param color : the agent's color
    @return      : the action to take for agent
    """
    alpha = -INF
    beta  = INF
    assert not board.game_over
    _, action = alphabeta(board, color, depth, None, alpha, beta)
    match action:
        case SpawnAction(_) | SpreadAction(_, _):
            pass
        case _:
            raise Exception()
    return action


def alphabeta(board  : Board,
              color  : PlayerColor,
              depth  : int,
              action : Action,
              alpha  : float,
              beta   : float
              ) -> (float, Action):
    """
    Alpha-beta pruning for minimax search algorithm.
    @param board  : the board
    @param color  : the current turn of player, specified by player's color
    @param depth  : the current depth in the search tree
    @param action : deduced best action
    @param alpha  : alpha - move that improves player's position
    @param beta   : beta  - move that improves opponent's position
    @return       : evaluated score of the board and the action to be made
    """

    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        return evaluate(board), action

    # maximize
    if color == PlayerColor.RED:
        value = -INF
        ret   = None
        legal_moves = get_legal_moves(board, color, full=False)
        ordered_map = move_ordering(board, color, legal_moves)
        # for each child node of board
        for possible_action in ordered_map:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _ = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta)

            # undo after finishing
            board.undo_action()
            if curr_val > value:
                value = curr_val
                ret   = possible_action
            alpha = max(alpha, value)

            # beta cutoff
            if value >= beta:
                break

    # minimize
    else:
        value = INF
        ret   = None
        legal_moves = get_legal_moves(board, color, full=False)
        ordered_map = move_ordering(board, color, legal_moves)
        # for each child node of board
        for possible_action in ordered_map:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _ = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta)

            # undo action after finishing
            board.undo_action()
            if curr_val < value:
                value = curr_val
                ret   = possible_action
            beta = min(beta, value)

            # alpha cutoff
            if value <= alpha:
                break

    # return evaluated value and corresponding action
    return value, ret


def move_ordering(board: Board, color: PlayerColor, actions: list[Action]) -> map:
    """
    Move ordering for speed-up pruning. Using domain knowledge of the game, this will more likely
    to choose a better move first in order to prune more branches before expanding them.
    @param board   : the board
    @param color   : player's color to have their legal moves ordered by probabilistic desirability
    @param actions : the list of legal actions for player
    @return        : the ordered list of actions, in map format (to reduce list conversion overhead)
    """
    # for each action of the player's list of legal moves
    action_values: list[tuple[Action, int]] = [(None, 0)] * len(actions)
    index = 0
    for action in actions:
        match action:
            # spawn means adding their power by 1
            case SpawnAction(_):
                action_values[index] = (action, 1)
            # spread can either be a power-1 spread, or higher, which is possibly more desirable
            case SpreadAction(pos, dir):
                power = board[action.cell].power
                if power > 1:
                    action_values[index] = (action, power)
                else:
                    adj = pos + dir
                    adj_cell = board[adj]
                    if adj_cell.color == color.opponent:
                        action_values[index] = (action, adj_cell.power)
                    else:
                        action_values[index] = (action, 0)
            # error case
            case _:
                raise Exception()
        index += 1

    # sort the actions by their desirability, in decreasing order
    action_values.sort(key=lambda tup: tup[1], reverse=True)
    return map(lambda tup: tup[0], action_values)

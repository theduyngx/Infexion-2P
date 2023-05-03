"""
    Module  : search_utils.py
    Purpose : Utility functions for search algorithms, mainly for getting information of a specific
              position as well as getting all legal moves for a specific agent and move ordering
              for general searching algorithms.

Get all legal moves is optimized for the Minimax algorithm. It allows agent to choose full, if agent
would like to get every possible legal move that's available for it, or reduced, if agent would like
to ignore specific actions that are considered 'quiet', viz. not having significant effects.
"""

from agent.board import Board
from agent.constants import MIN_TOTAL_POWER
from referee.game import HexPos, HexDir, PlayerColor, Action, SpawnAction, MAX_TOTAL_POWER, SpreadAction


def assert_action(action):
    """
    Asserting that a given object is indeed a proper Action.
    @param action : the given supposed action
    """
    match action:
        case SpawnAction(_):
            pass
        case SpreadAction(_, _):
            pass
        case _:
            print(type(action))
            print(action)
            raise Exception("Action not matched with any pattern")


def adjacent_positions(pos: HexPos) -> list[HexPos]:
    """
    Get all adjacent positions to the specified one.
    @param pos : the specified position
    @return    : list of 6 of its adjacent positions
    """
    return [pos + dir for dir in HexDir]


def get_legal_moves(board: Board, color: PlayerColor, full=True) -> list[Action]:
    """
    Get all possible legal moves of a specified player color from a specific state of the board.

    NOTE: add endgame detection here
    Pseudocode:
    if player_power > MAX_TOTAL_POWER / 2 and num_opponent <= 2:
        if there exists an opponent power == 1 (meaning at most 1 opponent with power above 1):
            if opponent_power > 2:
                for all red pieces:
                    if red.action can eat opponent:
                        actions.append(action)
            else:
                for both power-1 blue pieces:
                    if red.action can eat opponent:
                        actions.append(action)

    @param board : specified board
    @param color : specified player's color
    @param full  : to get the full list of legal moves if true, or reduced list if otherwise
    @return      : list of all actions that could be applied to board
    """
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: list[Action] = []
    player_power   = board.color_power(color)
    opponent_power = board.color_power(color.opponent)
    for cell in board.get_cells():

        # append spawn actions - if full then always append (if power < 49), otherwise append on condition
        pos = cell.pos
        if not board.pos_occupied(pos):
            if board.total_power() < MAX_TOTAL_POWER:
                if full:
                    actions.append(SpawnAction(pos))

                # append on condition: board power < 10, player power >= opponent's, has adjacent pieces
                elif board.total_power() < MIN_TOTAL_POWER and player_power >= opponent_power:
                    adj_list = adjacent_positions(pos)
                    # and that if only the spawn action is not quiet - viz. has adjacent piece
                    if any([board.pos_occupied(adj) for adj in adj_list]):
                        actions.append(SpawnAction(pos))

        # append spread actions for every direction
        elif board[pos].color == color:

            # add if total power exceeds acceptable limit for reduction, and that spread is non-quiet
            if not full and board[pos].power == 1 and board.total_power() > MIN_TOTAL_POWER:
                for dir in HexDir:
                    adj = pos + dir
                    if board.pos_occupied(adj):
                        actions.append(SpreadAction(pos, dir))
            # otherwise, full list requested, or position has power exceeding 1
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    return actions


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

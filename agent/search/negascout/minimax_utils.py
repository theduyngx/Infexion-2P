"""
Module:
    ``minimax_utils.py``

Purpose:
    Utility functions for Minimax-variant algorithms, including Negamax and NegaScout. This includes
    optimization for getting all legal moves for a specific agent and other search optimization
    functionalities such as move ordering and dynamic move reductions.

Notes:
    Get all legal moves is optimized for Negamax, and NegaScout algorithms. It allows agent to choose
    ``full``, if agent requires every possible legal move that's available, or otherwise (a reduced
    version) if agent wants to ignore specific actions that are considered `quiet`, viz. not having
    significant effects.

    Move reduction also entails endgame detection, where the desirable moves become more apparent;
    hence any moves that may not seem desirable can simply be filtered out.
"""

from collections import defaultdict

from referee.game import HexPos, HexDir, PlayerColor, \
                         Action, SpawnAction, SpreadAction, \
                         MAX_TOTAL_POWER, BOARD_N
from ...game import Board, adjacent_positions, \
                    Clusters, create_clusters_color, \
                    MIN_TOTAL_POWER, EMPTY_POWER
from ..search_utils import get_legal_moves

# Constant
MAX_ENDGAME_NUM_OPPONENT: int = 2


def check_endgame(board: Board, color: PlayerColor) -> list[Action]:
    """
    Endgame detection - the optimization function for getting all legal nodes on the condition
    that the game is reaching its end.

    Args:
        board: the board
        color: player's color

    Returns:
        the list of actions for endgame (if list is empty then not endgame)
    """
    # list of actions on the condition that it has reached endgame
    actions: list[Action] = []
    player_num, player_power = board.color_number_and_power(color)
    opponent_num, opponent_power = board.color_number_and_power(color.opponent)

    # dictionary for piece and actions, and their capture potential -> greedy
    action_capture : dict[(HexPos, HexDir), int] = defaultdict()
    stacked_capture: dict[(HexPos, HexDir), int] = defaultdict()
    final          : dict[(HexPos, HexDir), int]

    # endgame conditions: minimal player power requirement
    if player_power >= MAX_TOTAL_POWER // 4:
        opponents = board.player_cells(color.opponent)
        bool_single_power = [opponent.power == 1 for opponent in opponents]
        single_power = list(map(lambda x: x, bool_single_power))

        # endgame: if number of opponents less than a third of player's with mostly single-power
        endgame = opponent_num <= player_num // 3 and len(single_power) >= len(bool_single_power)-1
        if not endgame:
            return []

        # make sure that all clusters of opponent must be of size 2 or lower
        opponent_clusters: Clusters = create_clusters_color(board, color.opponent)
        for cluster in opponent_clusters:
            if len(cluster) > 2:
                return []
            for opponent in cluster:
                # if piece is stacked, then it must be cleared out, otherwise not endgame
                stacked = opponent.power > 1
                cleared = not stacked

                # for each direction, get the same direction ranges
                for dir in HexDir:
                    ranges = [range(1, BOARD_N//2 + 1), range(-1, -(BOARD_N//2+1), -1)]
                    for r in ranges:

                        # for each cell in said direction
                        for s in r:
                            curr_pos = opponent.pos - dir * s
                            cell = board[curr_pos]
                            # make sure that it has to be the player's cell
                            if cell.color != color:
                                continue
                            # append to actions if cell can reach the opponent and its power
                            # at least is equal to the opponent's cluster size
                            if cell.power >= abs(s) and cell.power >= len(cluster):
                                cleared = True
                                key = (curr_pos, dir)
                                if key in action_capture:
                                    action_capture[key] += 1
                                else:
                                    action_capture[key] = 1
                                if stacked:
                                    stacked_capture[key] = 1
                # if stacked opponent cannot be cleared, then it isn't endgame
                if not cleared:
                    return []

        # if there is a stacked opponent, then we update number of captures in captured dict
        if stacked_capture:
            final = stacked_capture
            for key in stacked_capture.keys():
                stacked_capture[key] += action_capture[key]
        # otherwise, either no stacked opponent or not endgame (no opponent can be captured)
        elif action_capture:
            final = action_capture
        else:
            return []

        # sort the actions by following priorities
        action_sorted = sorted(
            final.items(),
            key = lambda item: (
                item[1],                # 1. number of captures
                board[item[0][0]].power # 2. piece power
            ),
            reverse=True
        )
        for (pos, dir), _ in action_sorted:
            actions.append(SpreadAction(pos, dir))
    return actions


def get_optimized_legal_moves(board: Board, color: PlayerColor, full=True) -> (list[Action], bool):
    """
    Get optimized legal moves of a specified player color from a specific state of the board.
    Optimizations made are to reduce the number of legal moves had to be generated in Minimax
    tree.

    Args:
        board : specified board
        color : specified player's color
        full  : `True` to get the full list of legal moves, or `False` to get the reduced list
                of all possible legal actions

    Returns:
        * list of all actions that could be applied to board,
        * boolean indicating whether endgame has been reached
    """
    # if the actual player side is being overwhelmed, forcefully get all legal moves possible
    actions: list[Action] = []
    player_power   = board.color_power(color)
    opponent_power = board.color_power(color.opponent)
    total_power    = player_power + opponent_power
    if not full:
        if player_power == EMPTY_POWER:
            full = True
        elif color == board.true_turn:
            player_overwhelmed = player_power <= opponent_power // 3 and \
                                 total_power >= MIN_TOTAL_POWER
            full = player_overwhelmed

    # endgame check
    if not full:
        actions = check_endgame(board, color)
        if len(actions) > 0:
            return actions, True

    # getting all legal moves
    if full:
        return get_legal_moves(board, color), False

    for cell in board.get_cells():
        pos = cell.pos
        # check for spread cells
        if cell.color == color:
            # add if total power exceeds acceptable limit for reduction, and that spread is non-quiet
            if board[pos].power == 1:
                for dir in HexDir:
                    adj = pos + dir
                    if board[adj].color == color.opponent:
                        actions.append(SpreadAction(pos, dir))
            # otherwise, full list requested, or position has power exceeding 1
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])

        # check for every spawn cells
        elif board.total_power() < MAX_TOTAL_POWER and not board.pos_occupied(pos):
            # spawn is skipped if the spawn is not adjacent to any of player's cell
            adj_list = adjacent_positions(pos)
            if any([board[adj].color == color for adj in adj_list]):
                actions.append(SpawnAction(pos))
    return actions, False


def move_ordering(board: Board, color: PlayerColor, actions: list[Action]) -> list[Action]:
    """
    Move ordering for speed-up pruning. Using domain knowledge of the game, this will more likely
    to choose a better move first in order to prune more branches before expanding them.

    Args:
        board   : the board
        color   : player's color to have their legal moves ordered by probabilistic desirability
        actions : the list of legal actions for player

    Returns:
        the ordered list of actions
    """
    action_values: list[tuple[Action, int, int, int]] = [(None, # action
                                                          0,    # total power captured
                                                          0,    # total number of captured
                                                          0     # player's piece power
                                                          )] * len(actions)
    # for each action of the player's list of legal moves
    index = 0
    for action in actions:
        match action:
            # spawn means adding their power by 1
            case SpawnAction(_):
                action_values[index] = (action, 0, 0, 1)
            # spread can either be a power-1 spread, or higher, which is possibly more desirable
            case SpreadAction(pos, dir):
                power = board[action.cell].power
                total_blue_power  = 0
                total_blue_pieces = 0
                for s in range(1, power + 1):
                    curr_pos = pos + dir * s
                    if board[curr_pos].color == color.opponent:
                        total_blue_power  += board[curr_pos].power
                        total_blue_pieces += 1
                # Now add these values into the tuple to sort
                action_values[index] = (action, total_blue_power, total_blue_pieces, power)
            # error case
            case _:
                raise "move_ordering: Action not of any type"
        index += 1

    # sort the actions by their desirability, in decreasing order, in following priorities
    action_values.sort(
        key=lambda tup: (
            tup[1],    # 1. total power captured
            -tup[2],   # 2. reverse number of pieces captured (viz. more stacked captures)
            tup[3]     # 3. player's piece power
        ),
        reverse=True
    )
    return list(map(lambda tup: tup[0], action_values))

"""
    Module  : search_utils.py
    Purpose : Utility functions for search algorithms, mainly for getting information of a specific
              position as well as getting all legal moves for a specific agent and other search
              optimization functionalities including move ordering and dynamic move reductions.

Get all legal moves is optimized for the Minimax algorithm. It allows agent to choose full, if agent
would like to get every possible legal move that's available for it, or reduced, if agent would like
to ignore specific actions that are considered 'quiet', viz. not having significant effects. Move
reduction also entails endgame detection, where the desirable moves become more apparent; hence any
moves that may not seem desirable can simply be filtered out.
"""
from collections import defaultdict

from agent.game import Board, MIN_TOTAL_POWER, EMPTY_POWER
from referee.game import HexPos, HexDir, PlayerColor, \
                         Action, SpawnAction, SpreadAction, \
                         MAX_TOTAL_POWER, BOARD_N

# Constant
MAX_ENDGAME_NUM_OPPONENT: int = 2


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
            raise "Action not matched with any pattern"


def adjacent_positions(pos: HexPos) -> list[HexPos]:
    """
    Get all adjacent positions to the specified one.
    @param pos : the specified position
    @return    : list of 6 of its adjacent positions
    """
    return [pos + dir for dir in HexDir]


def check_endgame(board: Board, color: PlayerColor) -> (list[Action], int, int):
    """
    Endgame detection - the optimization function for getting all legal nodes on the condition
    that the game is reaching its end.

    Another possible improvement: Endgame detection can also depend on the number of opponent's
    clusters compared to their number of pieces. If it's the same, then it is highly clustered,
    and it is most definitely endgame as well.
    @param board : the board
    @param color : player's color
    @return      : the list of actions for endgame (if list is empty then not endgame),
                   the player's total power (for reusing),
                   the opponent's total power (for reusing)
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
        if endgame:
            for opponent in opponents:
                # if piece is stacked, then it must be cleared out, otherwise this isn't endgame
                stacked = opponent.power > 1
                cleared = not stacked

                # for each direction, get the same direction ranges
                for dir in HexDir:
                    ranges = [range(1, BOARD_N//2 + 1), range(-1, -BOARD_N//2 - 1, -1)]
                    for r in ranges:

                        # for each cell in said direction
                        for s in r:
                            curr_pos = opponent.pos - (dir * s)
                            cell = board[curr_pos]
                            # make sure that it is not an empty cell or opponent's cell
                            if cell.power == EMPTY_POWER or cell.color == color.opponent:
                                continue
                            # append to actions if cell can reach the opponent
                            if cell.power >= abs(s):
                                cleared  = True
                                key = (curr_pos, dir)
                                if key in action_capture:
                                    action_capture[key] += 1
                                else:
                                    action_capture[key] = 1
                                if stacked:
                                    stacked_capture[key] = 1
                # if stacked opponent cannot be cleared, then it isn't endgame
                if not cleared:
                    return [], player_power, opponent_power

        # if there is a stacked opponent, then we update number of captures in captured dict
        if stacked_capture:
            final = stacked_capture
            for key in stacked_capture.keys():
                stacked_capture[key] += action_capture[key]
        # otherwise, either no stacked opponent or not endgame (no opponent can be captured)
        elif action_capture:
            final = action_capture
        else:
            return [], player_power, opponent_power

        # sort the actions by priority 1 - number of captures, and 2 - piece power
        action_sorted = sorted(final.items(),
                               key=lambda item: (item[1], board[item[0][0]].power),
                               reverse=True)
        (pos, dir), max_capture = action_sorted[0]
        max_power = board[pos].power

        # return only the list of actions that are most desirable (equal highest number of
        # captures and equal highest power given the number of captures)
        for (pos, dir), value in action_sorted:
            if value < max_capture or board[pos].power < max_power:
                break
            actions.append(SpreadAction(pos, dir))
        assert actions
    return actions, player_power, opponent_power


def get_legal_moves(board: Board, color: PlayerColor, full=True) -> (list[Action], bool):
    """
    Get all possible legal moves of a specified player color from a specific state of the board.
    There are several optimizations made for this function in order reduce the number of legal
    moves had to be generated in the minimax tree. This includes endgame detection and ignoring
    specific moves based on domain knowledge of the game.
    However, in the case when player is overwhelmed, then full will be forcefully set to True.
    @param board  : specified board
    @param color  : specified player's color
    @param full   : to get the full list of legal moves if true, or reduced list if otherwise
    @return       : list of all actions that could be applied to board, and
                    boolean indicating whether endgame has been reached
    """

    # endgame check
    get_all = full
    actions, player_power, opponent_power = check_endgame(board, color)
    total_power = player_power + opponent_power
    if len(actions) > 0:
        return actions, True

    # if the actual player side is being overwhelmed, forcefully get all legal moves possible
    player = board.turn_color
    if color == player:
        player_overwhelmed = player_power <= opponent_power // 3 and \
                             total_power >= MIN_TOTAL_POWER
        if player_overwhelmed:
            get_all = True

    # for every possible move from a given board state, including SPAWN and SPREAD
    for cell in board.get_cells():

        # append spawn actions - always add when full, otherwise add on condition
        pos = cell.pos
        if not board.pos_occupied(pos):
            if board.total_power() < MAX_TOTAL_POWER:
                if get_all:
                    actions.append(SpawnAction(pos))

                # append on condition: within an acceptable range, spawn can be skipped
                elif player_power < MIN_TOTAL_POWER or player_power <= opponent_power:
                    adj_list = adjacent_positions(pos)
                    # and the skipped ones are those not adjacent to player's pieces
                    if any([board[adj].color == color for adj in adj_list]):
                        actions.append(SpawnAction(pos))

        # append spread actions for every direction
        elif board[pos].color == color:

            # add if total power exceeds acceptable limit for reduction, and that spread is non-quiet
            if not get_all and board[pos].power == 1 and board.total_power() > MIN_TOTAL_POWER:
                for dir in HexDir:
                    adj = pos + dir
                    if board[adj].color == color.opponent:
                        actions.append(SpreadAction(pos, dir))
            # otherwise, full list requested, or position has power exceeding 1
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    if get_all:
        assert len(actions) > 0
    return actions, False


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
                        action_values[index] = (action, adj_cell.power + 1)
                    else:
                        action_values[index] = (action, 0)
            # error case
            case _:
                raise "move_ordering: Action not of any type"
        index += 1

    # sort the actions by their desirability, in decreasing order
    action_values.sort(key=lambda tup: tup[1], reverse=True)
    return map(lambda tup: tup[0], action_values)

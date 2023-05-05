"""
    Module  : minimax_utils.py
    Purpose : Utility functions for minimax algorithm, which includes optimization for getting all
              legal moves for a specific agent and other search optimization functionalities such
              as move ordering and dynamic move reductions.

Get all legal moves is optimized for the Minimax algorithm. It allows agent to choose full, if agent
would like to get every possible legal move that's available for it, or reduced, if agent would like
to ignore specific actions that are considered 'quiet', viz. not having significant effects. Move
reduction also entails endgame detection, where the desirable moves become more apparent; hence any
moves that may not seem desirable can simply be filtered out.
"""

from collections import defaultdict, deque

from agent.game import Board, adjacent_positions, MIN_TOTAL_POWER, EMPTY_POWER, assert_action
from ..search_utils import get_legal_moves
from referee.game import HexPos, HexDir, PlayerColor, \
                         Action, SpawnAction, SpreadAction, \
                         MAX_TOTAL_POWER, BOARD_N

# Constant
MAX_ENDGAME_NUM_OPPONENT: int = 2


def check_endgame(board: Board, color: PlayerColor) -> list[Action]:
    """
    Endgame detection - the optimization function for getting all legal nodes on the condition
    that the game is reaching its end.
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
    return actions


def get_optimized_legal_moves(board: Board, color: PlayerColor, full=True) -> (list[Action], bool):
    """
    Get optimized legal moves of a specified player color from a specific state of the board.
    Optimizations made are to reduce the number of legal moves had to be generated in minimax
    tree. This includes endgame detection and ignoring specific moves based on domain knowledge.
    However, in the case when player is overwhelmed, then no optimization is set.
    @param board  : specified board
    @param color  : specified player's color
    @param full   : to get the full list of legal moves if true, or reduced list if otherwise
    @return       : list of all actions that could be applied to board, and
                    boolean indicating whether endgame has been reached
    """
    # if the actual player side is being overwhelmed, forcefully get all legal moves possible
    actions: list[Action] = []
    player_power   = board.color_power(color)
    opponent_power = board.color_power(color.opponent)
    total_power    = player_power + opponent_power
    if not full:
        if color == board.true_turn:
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

    # for every possible move from a given board state, including SPAWN and SPREAD
    for cell in board.get_cells():

        # append spawn actions - always add when full, otherwise add on condition
        pos = cell.pos
        if not board.pos_occupied(pos):
            if board.total_power() < MAX_TOTAL_POWER:

                # append on condition: within an acceptable range, spawn can be skipped
                if player_power < MIN_TOTAL_POWER or player_power <= opponent_power:
                    adj_list = adjacent_positions(pos)
                    # and the skipped ones are those not adjacent to player's pieces
                    if any([board[adj].color == color for adj in adj_list]):
                        actions.append(SpawnAction(pos))

        # append spread actions for every direction
        elif board[pos].color == color:

            # add if total power exceeds acceptable limit for reduction, and that spread is non-quiet
            if board[pos].power == 1 and board.total_power() > MIN_TOTAL_POWER:
                for dir in HexDir:
                    adj = pos + dir
                    if board[adj].color == color.opponent:
                        actions.append(SpreadAction(pos, dir))
            # otherwise, full list requested, or position has power exceeding 1
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    return actions, False


def move_ordering(board: Board, color: PlayerColor, actions: list[Action]) -> list[Action]:
    """
    Move ordering for speed-up pruning. Using domain knowledge of the game, this will more likely
    to choose a better move first in order to prune more branches before expanding them.

    Another possible optimization: return a heap queue for move ordering instead. This will make
    it only logarithmic in complexity at any given point.
    @param board   : the board
    @param color   : player's color to have their legal moves ordered by probabilistic desirability
    @param actions : the list of legal actions for player
    @return        : the ordered list of actions, in map format (to reduce list conversion overhead)
    """
    # action_num: number of captures ; action_pow: total power captured
    # the first will be reversed ordered, the latter will be orderly sorted
    action_num : dict[(HexPos, HexDir), float] = defaultdict()
    action_pow : dict[(HexPos, HexDir), float] = defaultdict()
    spread_all : dict[(HexPos, HexDir), float] = defaultdict()  # number value represents piece's power
    spawn_all  : deque[(Action, float)] = deque()
    capture_sorted: list[((HexPos, HexDir), float)] = []
    for action in actions:
        match action:
            case SpawnAction(pos):
                # spawn add 1.5 points if next to another of its own kind
                if any([board[pos + dir].color == color for dir in HexDir]):
                    spawn_all.appendleft((action, 1.5))
                # note that left is higher score, and right is lower
                else:
                    spawn_all.append((action, 1))
            case SpreadAction(pos, dir):
                spread_all[(pos, dir)] = board[pos].power - 1
            case _:
                raise "move_ordering: Action not of any type"

    ###
    # for action, _ in spawn_all:
    #     assert_action(action)
    init_spread_len = len(spread_all)
    ###

    if spread_all:
        opponents = board.player_cells(color.opponent)
        for opponent in opponents:
            # for each direction, get the same direction ranges
            for dir in HexDir:
                ranges = [range(1, BOARD_N // 2 + 1), range(-1, -BOARD_N // 2 - 1, -1)]
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
                            key = (curr_pos, dir)
                            if key in spread_all:
                                del spread_all[key]
                                action_num[key] = 1
                                action_pow[key] = opponent.power
                            if key in action_num:
                                action_num[key] += 1
                            if key in action_pow:
                                action_pow[key] += opponent.power

        # sorting the actions (in decreasing order) by the following 3 priorities
        capture_sorted = sorted(
            action_pow.items(),
            key=lambda item: (
                item[1],                 # 1. total power that was captured
                -action_num[item[0]],    # 2. least number of captured (viz. more stacked captures)
                board[item[0][0]].power  # 3. higher power of player's piece
            ),
            reverse=True
        )
        ###
        assert len(action_pow) == len(action_num)
        if init_spread_len != len(capture_sorted) + len(spread_all):
            print(init_spread_len)
            print(len(capture_sorted))
            print(len(spread_all))
            assert init_spread_len == len(capture_sorted) + len(spread_all)
        ###

    # for each action of the player's list of legal moves
    first = 0
    last  = len(spread_all) + len(spawn_all) - 1

    ###
    if len(actions) - len(capture_sorted) != len(spread_all) + len(spawn_all):
        print(len(spread_all), len(spawn_all))    # length of spread remaining and spawn all
        print(len(actions), len(capture_sorted))  # length of total number of actions and captured list

        print(len(spread_all) + len(spawn_all))   # supposed length of uncaptured list
        print(len(actions) - len(capture_sorted)) # true length of uncaptured list
    ###

    captured_actions  : list[Action] = list(map(lambda tup: SpreadAction(tup[0][0], tup[0][1]), capture_sorted))
    uncaptured_actions: list[Action] = [None] * (last + 1)
    # sort spread_all by the piece's power
    spread_remaining = list(spread_all.items())
    spread_remaining.sort(key=lambda tup: tup[1], reverse=True)

    if last >= 0:
        for entry in spread_remaining:
            (pos, dir), val = entry
            if val < 1:
                uncaptured_actions[last] = SpreadAction(pos, dir)
                if spawn_all:
                    action, _ = spawn_all.popleft()
                    uncaptured_actions[first] = action
                    first += 1
                last -= 1
            else:
                uncaptured_actions[first] = SpreadAction(pos, dir)
                first += 1
        for action, val in spawn_all:
            if val > 1:
                uncaptured_actions[first] = action
                first += 1
            else:
                uncaptured_actions[last] = action
                last -= 1
    ###
    # for action in uncaptured_actions:
    #     assert_action(action)
    # for action in captured_actions:
    #     assert_action(action)
    ###

    # add it all up
    captured_actions.extend(uncaptured_actions)
    actions_sorted = captured_actions
    assert len(actions_sorted) == len(actions)
    return actions_sorted

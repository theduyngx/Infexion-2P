# evaluation function
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexDir
from .board import Board, CellState

INF   : float = 9999
DEPTH : int   = 3


def evaluate(board: Board, color: PlayerColor) -> float:
    # for now let's only consider Material
    power_diff = board.num_players(color) - board.num_players(color.opponent)
    return power_diff


def minimax(board: Board, color: PlayerColor) -> Action:
    alpha = -INF
    beta  = INF
    _, action = alphabeta(board, color, DEPTH, alpha, beta)
    # should assert here that agent's board == referee's board,
    # viz. our undo actions works as expected
    return action


def alphabeta(board : Board,
              color : PlayerColor,
              depth : int,
              alpha : float,
              beta  : float
              ) -> (float, Action):
    """
    Alpha-beta pruning for minimax search algorithm.
    @param board : the board
    @param color : the current turn of player, specified by player's color
    @param depth : the current depth in the search tree
    @param alpha : alpha - move that improves player's position
    @param beta  : beta  - move that improves opponent's position
    @return      : evaluated score of the board and the action to be made
    """

    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        print("")
        print("depth =", depth)
        print("")
        return evaluate(board, color), None

    # maximize
    if color == PlayerColor.RED:
        value  = -INF
        action = None
        # for each child node of board
        for possible_action in get_child_nodes(board, color):
            # apply action
            board.apply_action(possible_action)
            curr_val, curr_action = alphabeta(board, color.opponent, depth-1, alpha, beta)
            # undo after finishing
            board.undo_action()
            if curr_val > value:
                value  = curr_val
                action = possible_action
            alpha = max(alpha, value)
            # beta cutoff
            if value >= beta:
                break
        return value, action

    # minimize
    else:
        value  = INF
        action = None
        # for each child node of board
        for possible_action in get_child_nodes(board, color):
            # apply action
            board.apply_action(possible_action)
            curr_val, curr_action = alphabeta(board, color.opponent, depth-1, alpha, beta)
            # undo action after finishing
            board.undo_action()
            if curr_val < value:
                value  = curr_val
                action = possible_action
            beta = min(beta, value)
            # alpha cutoff
            if value <= alpha:
                break
        return value, action


def get_child_nodes(board: Board, color: PlayerColor) -> list[Action]:
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: list[Action] = []
    movable_dict: list[CellState] = board.player_movable_cells(color)
    for state in movable_dict:
        # append spawn actions
        pos = state.pos
        if board.empty_cell(pos):
            actions.append(SpawnAction(pos))
        # append spread actions for each direction
        else:
            dirs = [hex_dir for hex_dir in HexDir]
            for dir in dirs:
                actions.append(SpreadAction(pos, dir))

    # for action in actions:
        ###
        # hp = HexPos(3, 4)
        # print(type(hp))
        # print(hp.r, hp.q)
        # print(type(action))
        # print(type(action.cell))
        # print(action.cell.r, action.cell.q, action.direction)
        ###
    return actions

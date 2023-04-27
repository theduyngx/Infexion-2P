# evaluation function
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexDir
from .board import Board

INF: float = 9999


def evaluate(board: Board, color: PlayerColor) -> float:
    # for now let's only consider Material
    power_diff = board.num_players(color) - board.num_players(color.opponent)
    return power_diff


def minimax(board: Board, color: PlayerColor) -> Action:
    depth: int = 4
    alpha = -INF
    beta  = INF
    _, action = alphabeta(board, color, depth, alpha, beta)
    # should assert here that agent's board == referee's board,
    # viz. our undo actions works as expected
    return action


def alphabeta(board        : Board,
              color : PlayerColor,
              depth        : int,
              alpha        : float,
              beta         : float
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
        return evaluate(board, color), None

    # maximize
    if color == PlayerColor.RED:
        value  = -INF
        action = None
        # for each child node of board
        for possible_action in get_child_nodes(board, color):
            # apply action
            board.apply_action(possible_action, color)
            curr_val, curr_action = alphabeta(board, color.opponent, depth-1, alpha, beta)
            # undo after finishing
            board.undo_action()
            if curr_val > value:
                value  = curr_val
                action = curr_action
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
            board.apply_action(possible_action, color)
            curr_val, curr_action = alphabeta(board, color.opponent, depth-1, alpha, beta)
            # undo action after finishing
            board.undo_action()
            if curr_val < value:
                value  = curr_val
                action = curr_action
            beta = min(beta, value)
            # alpha cutoff
            if value <= alpha:
                break
        return value, action


def get_child_nodes(board: Board, color: PlayerColor) -> [Action]:
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: [Action] = []
    movable_dict = board.player_movable_cells(color)
    for pos, cell in movable_dict:
        # append spawn actions
        if board.empty_cell(cell):
            actions.append(SpawnAction(cell))
        # append spread actions for each direction
        else:
            dirs = [hex_dir for hex_dir in HexDir]
            for dir in dirs:
                actions.append(SpreadAction(cell, dir))
    return actions

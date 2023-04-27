# evaluation function
from referee.game import PlayerColor, Action
from .board import Board

INF: float = 9999


def evaluate(board: Board, player_color: PlayerColor) -> float:
    # for now let's only consider Material
    power_diff = board.num_players(player_color) - board.num_players(player_color.opponent)
    return power_diff


def minimax(board: Board, player_color: PlayerColor) -> Action:
    depth: int = 4
    alpha = -INF
    beta  = INF
    _, action = alphabeta(board, player_color, depth, alpha, beta)
    return action


def alphabeta(board        : Board,
              player_color : PlayerColor,
              depth        : int,
              alpha        : float,
              beta         : float
              ) -> (float, Action):
    """
    Alpha-beta pruning for minimax search algorithm.
    @param board        : the board
    @param player_color : the current turn of player, specified by player's color
    @param depth        : the current depth in the search tree
    @param alpha        : alpha - move that improves player's position
    @param beta         : beta  - move that improves opponent's position
    @return             : evaluated score of the board and the action to be made
    """

    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        return evaluate(board, player_color), None

    # maximize
    if player_color == PlayerColor.RED:
        value  = -INF
        action = None
        # for each child node of board
        for child in get_child_nodes(board):
            curr_val, curr_action = alphabeta(child, player_color.opponent, depth-1, alpha, beta)
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
        for child in get_child_nodes(board):
            curr_val, curr_action = alphabeta(child, player_color.opponent, depth-1)
            if curr_val < value:
                value  = curr_val
                action = curr_action
            beta = min(beta, value)
            # alpha cutoff
            if value <= alpha:
                break
        return value, action


def get_child_nodes(board: Board) -> [(Board, Action)]:
    # for every possible move from a given board state, including SPAWN and SPREAD
    return [(board, None)]

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
    _, action = minimax_search(board, player_color, depth)
    return action


def minimax_search(board: Board, player_color: PlayerColor, depth: int) -> (float, Action):
    if depth == 0 or board.game_over:
        return evaluate(board, player_color), None

    # maximize
    if player_color == PlayerColor.RED:
        value  = -INF
        action = None
        for child in get_child_nodes(board):
            curr_val, curr_action = minimax_search(child, player_color.opponent, depth-1)
            if curr_val > value:
                value  = curr_val
                action = curr_action
        return value, action

    # minimize
    else:
        value  = INF
        action = None
        for child in get_child_nodes(board):
            curr_val, curr_action = minimax_search(child, player_color.opponent, depth-1)
            if curr_val < value:
                value  = curr_val
                action = curr_action
        return value, action


def get_child_nodes(board: Board) -> [(Board, Action)]:
    # for every possible move from a given board state, including SPAWN and SPREAD
    return [(board, None)]

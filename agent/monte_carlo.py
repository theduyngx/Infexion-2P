from agent.board import Board
from referee.game import Action
from .search import get_legal_moves


# Constants
INF   : int = 9999
LIMIT : int = 600


def monte_carlo(board: Board, limit=LIMIT) -> Action:
    operation = 0
    while operation < limit:
        operation += 1

    return None

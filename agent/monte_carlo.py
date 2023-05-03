from agent.board import Board
from referee.game import Action, PlayerColor
from .mc_node import MonteCarloNode
import queue
from .search import get_legal_moves
import heapq


# Constants
INF   : int = 9999
LIMIT : int = 600


def monte_carlo(board: Board, limit=LIMIT) -> Action:
    operation = 0

    open_min = queue.PriorityQueue()
    discovered = {}

    initial_node = MonteCarloNode(board, None)
    hash_curr = initial_node.__hash__()
    discovered[hash_curr] = 1
    open_min.put(initial_node)
    initial_copy = initial_node

    if board.turn_color == PlayerColor.RED:
        multiplier = 1
    else:
        multiplier = -1

    while operation < limit and not open_min.empty():
        curr_state = open_min.get()
        del discovered[hash_curr]

        if curr_state.board.game_over():
            pass

        for neighbor in get_legal_moves(curr_state.board, curr_state.board.turn_color):
            

    return None

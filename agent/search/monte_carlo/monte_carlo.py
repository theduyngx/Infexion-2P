"""
Module:
    ``monte_carlo.py``

Purpose:
    The Monte Carlo Tree search algorithm to find the next move for agent.

Notes:
"""

import time

from referee.game import Action
from ...game import Board
from ...search import get_legal_moves
from ..minimax import move_ordering
from .mutable_heapq import MutableHeap
from .mc_node import MonteCarloNode, TIME_LIMIT


def monte_carlo(board: Board, limit=TIME_LIMIT) -> Action:
    """
    Monte Carlo Tree search algorithm returning the next action to be taken by agent.

    Args:
        board      : the board
        limit      : the number of operations limit to stop the search

    Returns:
        the action to be taken by agent
    """

    operation    = 0
    open_min     = MutableHeap()
    discovered   = {}
    initial_node = MonteCarloNode(None, board)
    discovered[initial_node.hash_val] = 1
    open_min.add_task(initial_node)
    st = time.time()
    et = st

    # loop until it reached time limit or has explored all nodes
    while et-st <= limit and open_min.pq:
        curr_state = open_min.pop_task()
        del discovered[curr_state.hash_val]

        # No need to explore the node if game is already over
        if board.game_over:
            continue
        num_moves = 0
        all_moves = []

        # First get the board to the current state
        backtrack_start = curr_state
        while backtrack_start.parent is not None:
            all_moves.append(backtrack_start.action)
            backtrack_start = backtrack_start.parent
            num_moves += 1
        for i in range(num_moves-1, -1, -1):
            board.apply_action(all_moves[i], concrete=False)

        # Then get all the neighbors associated with the current node
        legal_moves   = get_legal_moves(board, board.turn_color)
        ordered_moves = move_ordering(board, board.turn_color, legal_moves)
        for neighbor in ordered_moves:
            curr_neighbor: MonteCarloNode = MonteCarloNode(neighbor, board, curr_state)

            # Only add to the node if the board has not yet been discovered
            if curr_neighbor.hash_val not in discovered:
                curr_neighbor.evaluate_node(board)
                new_evaluation = curr_neighbor.evaluation
                open_min.add_task(curr_neighbor, new_evaluation)
                discovered[curr_neighbor.hash_val] = 1
            board.undo_action()

        # simulations and backpropagation (only when this isn't the first node)
        if operation > 0:
            curr_state.hard_simulate(board, st, limit)
            curr_state.back_propagate(board)

        # Undo the actions for the board
        for i in range(num_moves):
            board.undo_action()
        operation += 1
        et = time.time()

    # go back to the initial node and get the child node with the highest UCT
    picked_action = sorted(initial_node.children, key=lambda x: x.uct, reverse=True)[0].action
    return picked_action

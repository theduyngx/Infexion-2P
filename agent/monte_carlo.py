from agent.board import Board
from referee.game import Action, PlayerColor
from .mc_node import MonteCarloNode
from .mutable_heapq import MutableHeap

# Constants
INF: int = 9999
LIMIT: int = 600


def monte_carlo(board: Board, limit=LIMIT) -> Action:
    operation = 0

    if board.turn_color == PlayerColor.RED:
        multiplier = -1
    else:
        multiplier = 1

    # open_min = queue.PriorityQueue()
    open_min = MutableHeap()
    discovered = {}

    initial_node = MonteCarloNode(None, None)
    hash_curr = initial_node.__hash__(board)
    discovered[hash_curr] = 1
    open_min.add_task(initial_node)

    while operation < limit and open_min.pq:
        num_actions = 0
        curr_state = open_min.pop_task()
        del discovered[hash_curr]

        # No need to explore the node if the game
        # is already over
        if curr_state.board.game_over():
            pass

        # First get the board to the current state
        while backtrack_start.parent is not None:
            all_moves.append(backtrack_start.action)
            backtrack_start = backtrack_start.parent
            num_moves += 1
        for i in range(num_moves - 1, -1, -1):
            board.apply_action(all_moves[i], concrete=False)

        # Then get all the neighbors associated with the current node
        for neighbor in board.get_legal_moves(board.turn_color):
            curr_neighbor: MonteCarloNode = MonteCarloNode(neighbor, curr_state)
            board = board.apply_action(neighbor, concrete=False)
            # Only add to the node if the board has not yet been discovered
            new_hash = curr_neighbor.__hash__(board)
            if new_hash not in discovered:
                new_evaluation = curr_neighbor.evaluate_node(board)
                open_min.put(curr_neighbor, new_evaluation)
                discovered[new_hash] = 1
            board = board.undo_action()

        # Now we do the simulations and the backpropagation,
        # but only if this is not the first node
        if operation > 0:
            # First collect all the possible moves
            all_moves = []
            num_moves = 0
            backtrack_start = curr_state

            # Now you want to do the SIMULATION


            # Then we do BACKPROPAGATION


        # Undo the actions for the board
        for i in range(num_moves):
            board = board.undo_action()

        operation += 1
    return None
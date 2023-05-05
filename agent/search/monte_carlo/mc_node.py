import copy
import time
from math import sqrt, log

from referee.game import PlayerColor, Action
from agent.game import Board
from .evaluation import mc_evaluate
from ..minimax import minimax
from ..agent_test import random_move

# Constants
UCT_CONSTANT     : float = sqrt(2)
RED_VICTORY      : int = 1
BLUE_VICTORY     : int = -1
SIMULATION_LIMIT : int = 4


class MonteCarloNode:
    __slots__ = [
        "evaluation",
        "victory",
        "value",
        "uct",
        "visited",
        "action",
        "parent",
        "children",
        "sim_score",
        "hash_val",
    ]

    def __init__(self, action: Action, board: Board, parent=None):
        self.value: int = 0
        self.victory: int = 0
        self.uct: float = 0
        self.visited: int = 0
        self.action: Action = action
        # Need to evaluate the board first so that it can be pushed into priority queue
        self.evaluation: int = 0
        self.parent: MonteCarloNode = parent
        # Make sure to add a child to children list of the parent
        if parent is not None:
            self.parent.children.append(self)
        # Need this when recalculating UCT
        # TODO: better data structure to store children (LinkedList?)
        self.children: list[MonteCarloNode] = []
        self.hash_val = self.__hash__(board)
        self.sim_score: float = 0
        return

    # Use this to calculate the evaluation value of the node
    def evaluate_node(self, board: Board):
        self.evaluation = mc_evaluate(board)
        return

    def evaluate_simulation(self, board: Board):
        self.sim_score = mc_evaluate(board)
        return

    # Formula for UCT Calculation, tries to find a balance between exploitation and exploration
    def calculate_uct(self):
        try:
            self.uct = self.sim_score + \
                       UCT_CONSTANT*sqrt(log(self.visited)/self.parent.visited)
        # Cases where there is division or log of 0
        except ValueError:
            self.uct = self.sim_score
        return

    # Modified uct_value that does not need to simulate?
    def calculate_new_uct(self):
        # mcts evaluation value is already normalized
        self.uct = self.evaluation + \
            UCT_CONSTANT*sqrt((log(self.visited)/log(self.parent.visited)))
        return

    # Each node should have a back propagation function that updates the value of each parent
    def back_propagate(self, board: Board):
        curr_node: MonteCarloNode = self
        added_value: int = self.victory
        while curr_node is not None:
            # undo action after applied
            board.undo_action()
            curr_node.value += added_value
            # Need to update the UCTs of the children
            for child in curr_node.children:
                child.calculate_uct()
            curr_node = curr_node.parent

    def quick_back_propagate(self, board: Board):
        curr_node: MonteCarloNode = self
        added_value: int = self.victory
        while curr_node is not None:
            # Since we're only referring to one board,
            # need to undo the action of the board each time
            board.undo_action()
            curr_node.value += added_value
            curr_node.visited += 1
            # Need to update the UCTs of the children
            for child in curr_node.children:
                child.calculate_new_uct()
            curr_node = curr_node.parent

    # LIGHT-SIMULATION: Randomly pick moves until a goal state is reached -> REALLY SLOW
    # TODO: Try achieve a sub-goal instead of a real goal
    def light_simulate(self, board: Board):
        test_board: Board = copy.deepcopy(board)
        while not test_board.game_over:
            new_action = random_move(test_board, test_board.turn_color)
            test_board.apply_action(new_action)
        # Now you have to check which player won
        if test_board.player_wins(PlayerColor.RED):
            self.victory = RED_VICTORY
        elif test_board.player_wins(PlayerColor.BLUE):
            self.victory = BLUE_VICTORY
        else:
            return

    # HARD-SIMULATION: Use heuristics instead to keep implementing moves until a goal state is reached
    def hard_simulate(self, board: Board):
        # TODO: Implement the game playing function
        #  using the evaluation function
        num_moves: int = 0
        st = time.time()
        while not board.game_over:
            new_action: Action = minimax(board, 2, board.turn_color)
            board.apply_action(new_action, concrete=False)
            num_moves += 1
            et = time.time()
            print(f'Current Time for Simulation: {et - st}, num_moves: {num_moves}')

        # Make sure to revert the board back
        for i in range(num_moves, 1, -1):
            board.undo_action()

        if board.player_wins(PlayerColor.RED):
            self.victory = RED_VICTORY
        elif board.player_wins(PlayerColor.BLUE):
            self.victory = BLUE_VICTORY
        else:
            return

    # This simulation really only returns the new value, although normalized to be in range [0, 1]
    def quick_simulate(self, board: Board, turn_color: PlayerColor):
        num_moves: int = 0
        while num_moves < SIMULATION_LIMIT and not board.game_over:
            new_action: Action = random_move(board, turn_color)
            board.apply_action(new_action, concrete=False)
            num_moves += 1

        # Evaluate the simulation
        self.evaluate_simulation(board)

        # Then we undo the changes made to the board
        for i in range(num_moves, 1, -1):
            board.undo_action()
        return

    # When picking a node to go to, always pick the node with the lower evaluation value
    def __lt__(self, other):
        return self.evaluation < other.evaluation

    def __eq__(self, other):
        return self.evaluation == other.evaluation

    def __hash__(self, board):
        return hash(frozenset(board.get_cells()))

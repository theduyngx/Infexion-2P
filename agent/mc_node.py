from math import sqrt, log
import copy
from .board import Board
from .evaluation import evaluate
from .agent_test import random_move
from referee.game import PlayerColor, Action
from .minimax import minimax


class MonteCarloNode:
    __slots__ = [
        "evaluation",
        "victory",
        "value",
        "uct",
        "visited",
        "board",
        "parent",
        "children"
    ]

    UCT_CONSTANT: int = sqrt(2)
    RED_VICTORY: int = 1
    BLUE_VICTORY: int = -1

    def __init__(self, board: Board, parent=None):
        self.value: int = 0
        self.victory: int = 0
        self.uct: float = 0
        self.visited: int = 0
        self.board: Board = board
        # Need to evaluate the board first so that it
        # can be pushed into priority queue
        self.evaluation: int = evaluate(board)
        self.parent: MonteCarloNode = parent
        # Make sure to add a child to children list
        # of the parent
        if parent is not None:
            self.parent.children.append(self)
        # Need this when recalculating UCT
        # TODO: better data structure to store children (LinkedList?)
        self.children: list[MonteCarloNode] = []
        return

    # Formula for UCT Calculation, tries to find a
    # balance between exploitation and exploration
    def calculate_uct(self):
        self.uct = self.value + \
                   MonteCarloNode.UCT_CONSTANT*sqrt((log(self.visited)/log(self.parent.visited)))
        return

    # Each node should also do a simulation if it was still unexplored
    # Will put multiple functions under this
    def simulate(self):
        # Most important thing is to make a deep copy
        # of the board we want to use for simulation
        test_board: Board = copy.deepcopy(self.board)
        return

    # Each node should have a back propagation function
    # that updates the value of each parent
    def back_propagate(self):
        curr_node: MonteCarloNode = self
        added_value: int = self.victory
        while curr_node is not None:
            curr_node.value += added_value
            # Need to update the UCTs of the children
            for child in curr_node.children:
                child.calculate_uct()
            curr_node = self.parent

    # LIGHT-SIMULATION: Randomly pick moves until
    # a goal state is reached -> REALLY SLOW
    # TODO: Try achieve a sub-goal instead of a real goal
    def light_simulate(self):
        test_board: Board = copy.deepcopy(self.board)
        while not test_board.game_over():
            new_action = random_move(test_board, test_board.turn_color)
            test_board = test_board.apply_action(new_action)
        # Now you have to check which player won
        if test_board.winner_color is None:
            return
        elif test_board.winner_color == PlayerColor.RED:
            self.victory = MonteCarloNode.RED_VICTORY
        else:
            self.victory = MonteCarloNode.BLUE_VICTORY

    # HARD-SIMULATION: Use heuristics instead to keep
    # implementing moves until a goal state is reached
    def hard_simulate(self):
        test_board: Board = copy.deepcopy(self.board)
        # TODO: Implement the game playing function
        #  using the evaluation function
        while not test_board.game_over():
            new_action: Action = minimax(test_board, test_board.turn_color)
            test_board = test_board.apply_action(new_action)
        if test_board.winner_color is None:
            return
        elif test_board.winner_color == PlayerColor.RED:
            self.victory = MonteCarloNode.RED_VICTORY
        else:
            self.victory = MonteCarloNode.BLUE_VICTORY

    # When picking a node to go to, always
    # pick the node with the lower evaluation value
    def __lt__(self, other):
        return self.evaluation < other.evaluation

    def __eq__(self, other):
        return self.evaluation == other.evaluation

    def __hash__(self):
        return hash(frozenset(self.board.get_cells()))

    def __iter__(self):
        yield

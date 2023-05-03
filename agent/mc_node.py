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
        "action",
        "parent",
        "children"
    ]

    UCT_CONSTANT: int = sqrt(2)
    RED_VICTORY: int = 1
    BLUE_VICTORY: int = -1

    def __init__(self, action: Action, parent=None):
        self.value: int = 0
        self.victory: int = 0
        self.uct: float = 0
        self.visited: int = 0
        self.action: Action = action
        # Need to evaluate the board first so that it
        # can be pushed into priority queue
        self.evaluation: int = 0
        self.parent: MonteCarloNode = parent
        # Make sure to add a child to children list
        # of the parent
        if parent is not None:
            self.parent.children.append(self)
        # Need this when recalculating UCT
        # TODO: better data structure to store children (LinkedList?)
        self.children: list[MonteCarloNode] = []
        return

    # Use this to calculate the evaluation value
    # of the node
    def evaluate_node(self, board: Board):
        self.evaluation = evaluate(board)
        return

    # Formula for UCT Calculation, tries to find a
    # balance between exploitation and exploration
    def calculate_uct(self):
        self.uct = self.value + \
                   MonteCarloNode.UCT_CONSTANT*sqrt((log(self.visited)/log(self.parent.visited)))
        return

    # Each node should have a back propagation function
    # that updates the value of each parent
    def back_propagate(self, board: Board):
        curr_node: MonteCarloNode = self
        added_value: int = self.victory
        while curr_node is not None:
            # Since we're only referring to one board,
            # need to undo the action of the board each time
            board = board.undo_action()
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
    def hard_simulate(self, board: Board):
        # TODO: Implement the game playing function
        #  using the evaluation function
        num_moves: int = 0
        while not board.game_over():
            new_action: Action = minimax(board, board.turn_color)
            board = board.apply_action(new_action)
            num_moves += 1

        # Make sure to revert the board back
        for i in range(num_moves, 1, -1):
            board.undo_action()

        if board.winner_color is None:
            return
        elif board.winner_color == PlayerColor.RED:
            self.victory = MonteCarloNode.RED_VICTORY
        else:
            self.victory = MonteCarloNode.BLUE_VICTORY

    # When picking a node to go to, always
    # pick the node with the lower evaluation value
    def __lt__(self, other):
        return self.evaluation < other.evaluation

    def __eq__(self, other):
        return self.evaluation == other.evaluation

    def __hash__(self, board):
        return hash(frozenset(board.get_cells()))

    def __iter__(self):
        yield

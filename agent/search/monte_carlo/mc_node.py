"""
Module:
    ``mc_node.py``

Purpose:
    Monte Carlo Tree's node representation.

Notes:
"""

import copy
import time
from math import sqrt, log

from referee.game import PlayerColor, Action
from ...game import Board
from ..agent_test import random_move, greedy_move, minimax_shallow
from .evaluation import mc_evaluate

# Constants
RED_VICTORY      : int   = 1
BLUE_VICTORY     : int   = -1
CHILD_LIMIT      : int   = 20
SIMULATION_LIMIT : int   = 1000
UCT_CONSTANT     : float = sqrt(2)
TIME_LIMIT       : float = 3


class MonteCarloNode:
    """
    The Monte Carlo Tree search node representation.
    Attributes:
        evaluation
        victory
        value
        uct
        visited
        action
        parent
        children
        sim_score
        hash_val
    """
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
        "depth",
        "hash_val",
    ]

    def __init__(self, action: Action, board: Board, parent: 'MonteCarloNode' = None):
        """
        Monte Carlo Tree node constructor.

        Args:
            action : the action that initiates the node
            board  : the given state of board
            parent : the parent node, default being None
        """
        self.value   : int = 0
        self.victory : int = 0
        self.visited : int = 0
        self.uct     : float = 0
        self.action  : Action = action

        # Need to evaluate the board first so that it can be pushed into priority queue
        self.evaluation: int = 0
        self.parent: MonteCarloNode = parent

        # Make sure to add a child to children list of the parent
        if parent is not None:
            self.parent.children.append(self)

        # Need this when recalculating UCT
        self.children  : list[MonteCarloNode] = []
        self.hash_val  : int = board.__hash__()
        self.depth     : int = board.turn_count
        self.sim_score : float = 0

    def evaluate_node(self, board: Board):
        """
        Method to evaluate the board at the node

        Args:
            board: the given board at the node
        """
        self.evaluation = mc_evaluate(board)

    def evaluate_simulation(self, board: Board):
        """
        Method to evaluate the simulation at the node.

        Args:
            board: the given board
        """
        self.sim_score = mc_evaluate(board)

    def calculate_uct(self):
        """
        Formula for UCT Calculation, tries to find a balance between exploitation and exploration.
        """
        try:
            self.uct = self.sim_score + \
                       UCT_CONSTANT*sqrt(log(self.visited)/self.parent.visited)
        # Cases where there is division or log of 0
        except ValueError:
            self.uct = self.sim_score

    def calculate_new_uct(self):
        """
        Modify UCT value of node.
        """
        # mcts evaluation value is already normalized
        self.uct = self.evaluation + \
            UCT_CONSTANT*sqrt((log(self.visited)/log(self.parent.visited)))

    def back_propagate(self, board: Board):
        """
        Each node should have a back propagation function that updates the value of each parent.

        Args:
            board: the state of board at the node
        """
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

    def light_simulate(self, board: Board):
        """
        Light simulation - randomly pick moves until a goal state is reached
        Args:
            board: the state of the board at the node
        """
        test_board: Board = copy.deepcopy(board)
        while not test_board.game_over:
            new_action = random_move(test_board, test_board.turn_color)
            test_board.apply_action(new_action)
        # Now you have to check which player won
        if test_board.player_wins(PlayerColor.RED):
            self.victory = RED_VICTORY
        elif test_board.player_wins(PlayerColor.BLUE):
            self.victory = BLUE_VICTORY

    def hard_simulate(self, board: Board, start: float, limit=TIME_LIMIT, debug=False):
        """
        Hard simulation - use heuristics instead to keep implementing moves until a goal state is
        reached.
        Args:
            board: the board
            start: start time
            limit: resource limit (in this case is time)
            debug: debug mode
        """
        num_moves: int = 0
        end = time.time()
        while end - start < limit and not board.game_over:
            new_action: Action = minimax_shallow(board, board.turn_color)
            board.apply_action(new_action, concrete=False)
            num_moves += 1
            end = time.time()
            if debug:
                print(f'Current Time for Simulation: {end - start}, num_moves: {num_moves}')

        # Make sure to revert the board back
        for i in range(num_moves):
            board.undo_action()

        if board.player_wins(PlayerColor.RED):
            self.victory = RED_VICTORY
        elif board.player_wins(PlayerColor.BLUE):
            self.victory = BLUE_VICTORY

    def quick_simulate(self, board: Board, start: float, limit=TIME_LIMIT):
        """
        This simulation really only returns the new value, although normalized to be in
        range ``[0, 1]``

        Args:
            board: the board
            start: start time
            limit: resource limit (in this case is time)
        """
        num_moves: int = 0
        curr_color: PlayerColor = board.turn_color
        end = time.time()
        while num_moves < SIMULATION_LIMIT and end - start < limit and not board.game_over:
            new_action: Action = greedy_move(board, curr_color)
            board.apply_action(new_action, concrete=False)
            curr_color = board.turn_color
            num_moves += 1
            end = time.time()

        # Evaluate the simulation, the undo changes made to board
        self.evaluate_simulation(board)
        for i in range(num_moves):
            board.undo_action()

    # When picking a node to go to, always pick the node with the lower evaluation value
    def __lt__(self, other):
        return self.evaluation < other.evaluation

    def __eq__(self, other):
        return self.evaluation == other.evaluation

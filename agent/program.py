"""
Module:
    ``program.py``

Authors:
    The Duy Nguyen (1100548) and Ramon Javier L. Felipe VI (1233281)

Purpose:
    The agent program for the game. This will be used by the ``referee`` and will act under
    the rules exacted by referee.

Notes:
    COMP30024 Artificial Intelligence, Semester 1 2023 - Project Part B: Game Playing Agent. When
    mentioning the rules by referee, it is important to note the following functions:
        * ``action`` to return an action that the agent decides to perform, and
        * ``turn`` which will be called as a signal for agent that it is their turn.
"""

from referee.game import Action, PlayerColor
from .search import search, random_move, greedy_move,\
                    minimax_shallow, mcts_move, negascout_move
from .game import Board
from .utils import *


class Agent:
    """
    Agent class representing the agent player.
    Attributes:
        _color: agent's color, indicating their side
        _board: the board representation that agent uses to keep track of game's state
    """
    __slots__ = [
        "_color",
        "_board"
    ]

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.

        Args:
            color     : the player's color
            **referee : the referee containing specific important information of the game
        """
        assert referee
        self._color = color
        self._board = Board()

    def get_color(self) -> PlayerColor:
        """
        Non-property getter to keep the color of the ``Agent`` final.
        Returns:
            player's color
        """
        return self._color

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take by the agent. Used by referee to apply the action to
        the game's board. The search algorithm for the action is NegaScout. For more specific
        information, see ``search`` and ``negascout`` packages.

        Args:
            referee: the referee
        Returns:
            the action to be taken next
        """
        print_referee(referee)
        return search(self._board, self._color, referee["time_remaining"])

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action. Called by referee to signal the
        turn of an agent (both when it is not, and it is their turn).

        Args:
            color   : the player's color
            action  : the action taken by agent
            referee : the referee
        """
        assert(color and referee)
        self._board.apply_action(action)


class RandomAgent(Agent):
    """
    The Random agent which does not use the primary search algorithm.
    """
    def action(self, **referee: dict) -> Action:
        print_referee(referee)
        return random_move(self._board, self._color)


class GreedyAgent(Agent):
    """
    The Greedy agent which does not use the primary search algorithm.
    """
    def action(self, **referee: dict) -> Action:
        print_referee(referee)
        return greedy_move(self._board, self._color)


class MinimaxShallowAgent(Agent):
    """
    The Shallow Minimax agent which does not use the primary search algorithm.
    """
    def action(self, **referee: dict) -> Action:
        print_referee(referee)
        return minimax_shallow(self._board, self._color)


class MonteCarloAgent(Agent):
    """
    The Monte Carlo agent which does not use the primary search algorithm.
    """
    def action(self, **referee: dict) -> Action:
        print_referee(referee)
        return mcts_move(self._board)


class NegaScoutAgent(Agent):
    """
    The NegaScout agent which does not use the primary search algorithm.
    """
    def action(self, **referee: dict) -> Action:
        print_referee(referee)
        return negascout_move(self._board, self._color)

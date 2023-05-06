"""
Module:
    ``program.py``

Purpose:
    The agent program for the game. This will be used by the ``referee`` and will act under
    the rules exacted by referee.

Notes:
    COMP30024 Artificial Intelligence, Semester 1 2023 - Project Part B: Game Playing Agent. When
    mentioning the rules by referee, it is important to note the following functions:
    ``action`` to return an action that the agent decides to perform, and
    ``turn`` which will be called as a signal for agent that it is their turn.
"""

from .search import search
from .search.agent_test import *
from .game import Board
from .utils import *


class Agent:
    """
    Agent class representing the agent player.
    """
    __slots__ = [
        "_color",
        "_board"
    ]

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        @param color   : the player's color
        @param referee : the referee
        """
        print_referee(referee)
        self._color = color
        self._board = Board()

    def get_color(self) -> PlayerColor:
        """
        Non-property getter to keep the color of the Agent final.
        @return: player's color
        """
        return self._color

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take by the agent. Used by referee to apply the action to
        the game's board.
        @param referee : the referee
        @return        : the action to be taken next
        """
        board = self._board
        color = self._color
        color_print = ansi_color(color)
        print(f"{color_print} TURN:")
        # return search(board, color)
        match color:
            case PlayerColor.RED:
                print_referee(referee)
                # return search(board, color)
                return mcts_move(board, color)
            case PlayerColor.BLUE:
                # return mcts_move(board, color)
                return search(board, color)
                # return minimax_shallow(board, color)
                # return random_move(board, color)
                # return greedy_move(board, color)
            case _:
                raise Exception(f"{color} is not of proper PlayerColor type")

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action. Called by referee to signal the
        turn of an agent (both when it is not, and it is their turn).
        @param color   : the player's color
        @param action  : action taken by agent
        @param referee : the referee
        """
        assert referee
        self._board.apply_action(action)
        color_print = ansi_color(color)

        match action:
            case SpawnAction(cell):
                print(f"{color_print} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"{color_print} SPREAD from {cell} - {direction}")
                pass

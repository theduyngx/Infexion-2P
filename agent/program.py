"""
    Module  : program.py
    Purpose : The agent program for the game.

COMP30024 Artificial Intelligence, Semester 1 2023 - Project Part B: Game Playing Agent.
"""

from referee.game import PlayerColor, Action, SpawnAction, SpreadAction
from .utils import *

from agent.search import minimax, search
from agent.agent_test import greedy_move, random_move
from agent.board import Board


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
        Return the next action to take by the agent.
        @param referee : the referee
        @return        : the action to be taken next
        """
        board = self._board
        color = self._color
        color_print = ansi_color(color)
        print(f"{color_print} TURN:")
        match color:
            case PlayerColor.RED:
                print_referee(referee)
                return search(board, color)
            case PlayerColor.BLUE:
                # return greedy_move(board, color)
                return minimax(board, 2, color, full=True)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        @param color   : the player's color
        @param action  : action taken by agent
        @param referee : the referee
        """
        self._board.apply_action(action)
        color_print = ansi_color(color)

        match action:
            case SpawnAction(cell):
                print(f"{color_print} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"{color_print} SPREAD from {cell} - {direction}")
                pass

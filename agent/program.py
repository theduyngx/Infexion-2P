"""
    Module  : program.py
    Purpose : The agent program for the game.

COMP30024 Artificial Intelligence, Semester 1 2023 - Project Part B: Game Playing Agent.
"""

from agent.search import minimax
from agent.agent_test import greedy_move, random_move
from agent.board import Board
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexPos, MAX_TOTAL_POWER

# NOTE: Should find a better way to store this, seems like it belongs to __init__.py
board: Board = Board()


def print_referee(referee: dict):
    """
    Print referee data. Space remaining sometimes works, sometimes doesn't. Though most of the time
    it does work, so I suppose it's fine.
    @param referee : the referee
    """
    print("---------------------------------------")
    print("Time remaining  :", referee["time_remaining"])
    print("Space remaining :", referee["space_remaining"])
    print("---------------------------------------")


class Agent:
    """
    Agent class representing the agent player.
    """
    __slots__ = [
        "_color"
    ]

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        @param color   : the player's color
        @param referee : the referee
        """
        print_referee(referee)
        self._color = color

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
        if board.total_power() < MAX_TOTAL_POWER:
            match self._color:
                case PlayerColor.RED:
                    if board.turn_count < 1:
                        return SpawnAction(HexPos(3, 3))
                    return minimax(board, self._color)
                case PlayerColor.BLUE:
                    return minimax(board, self._color)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        @param color   : the player's color
        @param action  : action taken by agent
        @param referee : the referee
        """
        assert self
        print_referee(referee)
        board.apply_action(action)

        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass
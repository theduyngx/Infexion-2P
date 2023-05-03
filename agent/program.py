"""
    Module  : program.py
    Purpose : The agent program for the game.

COMP30024 Artificial Intelligence, Semester 1 2023 - Project Part B: Game Playing Agent.
"""

from agent.search import minimax
from agent.agent_test import greedy_move, random_move
from agent.board import Board
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexPos, MAX_TOTAL_POWER, HexDir

# NOTE: Should find a better way to store this, seems like it belongs to __init__.py
board: Board = Board()

# hard-coded moves to test
queue: list[Action] = [SpawnAction (HexPos(5, 4)), SpawnAction(HexPos(6, 6)), SpawnAction(HexPos(0, 1)),
                       SpawnAction (HexPos(1, 4)), SpawnAction(HexPos(6, 5)), SpawnAction(HexPos(5, 6)),
                       SpawnAction (HexPos(5, 3)), SpreadAction(HexPos(5, 4), HexDir.UpLeft),
                       SpawnAction (HexPos(0, 4)), SpreadAction(HexPos(6, 5), HexDir.Down),
                       SpreadAction(HexPos(6, 6) , HexDir.DownLeft), SpreadAction(HexPos(5, 6), HexDir.DownRight),
                       SpreadAction(HexPos(5, 1) , HexDir.DownRight), SpreadAction(HexPos(5, 0), HexDir.DownLeft),
                       SpreadAction(HexPos(5, 2) , HexDir.Up), SpreadAction(HexPos(1, 4), HexDir.DownLeft),
                       SpreadAction(HexPos(0, 0) , HexDir.UpRight), SpreadAction(HexPos(5, 3), HexDir.DownRight),
                       SpreadAction(HexPos(2, 5) , HexDir.Up), SpawnAction(HexPos(5, 1)),
                       SpreadAction(HexPos(5, 1) , HexDir.UpRight), SpawnAction(HexPos(1, 2)),
                       SpawnAction (HexPos(3, 1)), SpreadAction(HexPos(1, 2), HexDir.Up),
                       SpreadAction(HexPos(2, 0) , HexDir.DownRight), SpreadAction(HexPos(2, 1), HexDir.UpRight),
                       SpreadAction(HexPos(1, 6) , HexDir.Up), SpreadAction(HexPos(2, 2), HexDir.Down),
                       SpreadAction(HexPos(0, 4) , HexDir.Up), SpreadAction(HexPos(4, 1), HexDir.UpRight),
                       SpreadAction(HexPos(1, 3) , HexDir.UpRight), SpreadAction(HexPos(4, 3), HexDir.DownRight),
                       SpreadAction(HexPos(4, 5) , HexDir.UpLeft), SpreadAction(HexPos(1, 0), HexDir.Up),
                       SpreadAction(HexPos(4, 4) , HexDir.Down), SpreadAction(HexPos(2, 6), HexDir.DownLeft),
                       SpreadAction(HexPos(0, 6) , HexDir.Down), SpreadAction(HexPos(5, 6), HexDir.DownLeft),
                       SpawnAction (HexPos(2, 6)), SpawnAction(HexPos(4, 0)), SpreadAction(HexPos(1, 6), HexDir.Up),
                       SpreadAction(HexPos(2, 3) , HexDir.DownLeft), SpreadAction(HexPos(1, 3), HexDir.DownRight),
                       SpreadAction(HexPos(1, 4) , HexDir.DownLeft), SpreadAction(HexPos(0, 4), HexDir.UpLeft),
                       SpreadAction(HexPos(0, 2) , HexDir.DownRight), SpreadAction(HexPos(6, 4), HexDir.Up),
                       SpreadAction(HexPos(2, 5) , HexDir.UpLeft)]


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
                    # action = queue.pop(0)
                    return greedy_move(board, self._color)

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

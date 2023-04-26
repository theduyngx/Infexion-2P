# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
from agent.board import Board
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir


board: Board = Board()


def print_referee(referee: dict):
    print("-------------------------------")
    print("Time remaining  :", referee["time_remaining"])
    print("Space remaining :", referee["space_remaining"])
    # print("Space limit     :", referee["space_limit"])


class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                return SpawnAction(HexPos(3, 3))
            case PlayerColor.BLUE:
                return SpawnAction(HexPos(4, 3))
                # return SpreadAction(HexPos(4, 3), HexDir.Up)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        assert self
        print_referee(referee)
        board.apply_action(action, concrete=True)

        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

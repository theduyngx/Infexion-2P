# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
from agent.board import Board
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, WIN_POWER_DIFF

board: Board = Board()


def print_referee(referee: dict):
    print("-------------------------------")
    print("Time remaining  :", referee["time_remaining"])
    print("Space remaining :", referee["space_remaining"])
    # print("Space limit     :", referee["space_limit"])


class Agent:
    __slots__ = [
        "_color"
    ]

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

    def get_color(self):
        """
        Non-property getter to keep the color of the Agent final.
        """
        return self._color

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        if board.total_power() < WIN_POWER_DIFF:
            # bad hard-coded stuffs
            return SpawnAction(HexPos(5, 3)) \
                if board.cell_occupied(HexPos(3, 3)) else SpawnAction(HexPos(3, 3))

        match self._color:
            case PlayerColor.RED:
                return SpreadAction(HexPos(3, 3), HexDir.UpRight)
            case PlayerColor.BLUE:
                return SpreadAction(HexPos(5, 3), HexDir.DownLeft)

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

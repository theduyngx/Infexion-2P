"""
    Module  : game_utils.py
    Purpose : Utility functions for the game, which is directly related to the game's board.
              This includes asserting an action to be applied to board, and getting adjacent
              positions from a given specified position on the board.
"""

from ..referee.game import HexPos, HexDir, SpawnAction, SpreadAction


def assert_action(action):
    """
    Asserting that a given object is indeed a proper Action.
    @param action : the given supposed action
    """
    match action:
        case SpawnAction(_):
            pass
        case SpreadAction(_, _):
            pass
        case _:
            print(type(action))
            print(action)
            raise "Action not matched with any pattern"


def adjacent_positions(pos: HexPos) -> list[HexPos]:
    """
    Get all adjacent positions to the specified one.
    @param pos : the specified position
    @return    : list of 6 of its adjacent positions
    """
    return [pos + dir for dir in HexDir]

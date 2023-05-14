"""
Module:
    ``player.py``

Purpose:
    Module related to representing player in the game.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. Slight modifications were made by The Duy Nguyen (1100548).
"""

from enum import Enum
from abc import abstractmethod
from .actions import Action
from ..log import LogColor


class PlayerColor(Enum):
    """
    ``PlayerColor`` is an enum used by the referee to identify the two players on the game board
    as per the game rules (**red** and **blue**).

    The referee will pass this to your agent when it
    is initialized in order to signal which player it should be playing as, and is also used to
    distinguish between the two players in the ``turn()`` method (i.e. whose action has been played).

    Attributes:
        RED  : player color **red**
        BLUE : player color **blue**
    """
    RED  = 0
    BLUE = 1

    def __str__(self) -> str:
        """
        String representation of a player colour identifier.
        """
        return {
            PlayerColor.RED: "RED",
            PlayerColor.BLUE: "BLUE"
        }[self]

    def log_format(self, ansi=False) -> str:
        """
        Return ansi-formatted string for the player. Written to improve visualization,
        by The Duy Nguyen (1100548).

        Args:
            ansi: `True` if ansi-applied, `False` if otherwise

        Returns:
            the ansi string format
        """
        color = ""
        width = ""
        if ansi:
            color = LogColor.RED if self.value == 0 else LogColor.BLUE
            width = LogColor.BOLD
        return f"{width}{color}{self.__str__()}{LogColor.RESET_ALL}"

    def __index__(self) -> int:
        """
        Return the index of the player (0 or 1).
        """
        return self.value

    def __int__(self) -> int:
        """
        Player value in zero-sum form (+1 RED, -1 BLUE). 
        """
        return 1 - 2 * self.value

    @property
    def opponent(self) -> "PlayerColor":
        """
        Return the other player colour (there are only two!).
        """
        match self:
            case PlayerColor.RED:
                return PlayerColor.BLUE
            case PlayerColor.BLUE:
                return PlayerColor.RED


class Player:
    """
    Player is an abstract base class for actual players of the game.
    It's used internally by the referee to wrap your agent and/or other virtual players.
    """
    def __init__(self, color: PlayerColor, ansi):
        """
        Player constructor. Modified by The Duy Nguyen (1100548) to add the option of
        displaying the player with ansi format.
        Args:
            color : player's color
            ansi  : optional ansi color to apply
        """
        self._color = color
        self._ansi  = ansi

    @property
    def color(self) -> PlayerColor:
        """
        Player's color - a property.
        """
        return self._color

    def __str__(self) -> str:
        """
        String representation of player.
        """
        return str(self._color.log_format(self._ansi))

    @abstractmethod
    async def action(self) -> Action:
        """
        Get the next action for the player.
        """
        raise NotImplementedError

    @abstractmethod
    async def turn(self, color: PlayerColor, action: Action):
        """
        Notify the player that an action has been played.
        """
        raise NotImplementedError

    async def __aenter__(self) -> 'Player':
        """
        Context manager: Any resource allocation should be done here.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager: Any resource cleanup should be done here.
        """
        pass

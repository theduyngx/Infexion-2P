"""
Module:
    ``actions.py``

Purpose:
    The valid actions that a player could make in Infexion.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. The actions include spawn in unoccupied cells and spread from
    an already occupied by player position. Original documentation:

    Here we define dataclasses for the two possible actions that a player can make. See the
    ``hex.py`` file for the definition of the ``HexPos`` and ``HexDir``. If you are unfamiliar with
    dataclasses, see the relevant Python docs here: https://docs.python.org/3/library/dataclasses.html
"""

from dataclasses import dataclass
from .hex import HexPos, HexDir


@dataclass(frozen=True, slots=True)
class SpawnAction:
    """
    Spawn action. Only requires a position where player would spawn.
    Attributes:
        cell: the cell to spawn at
    """
    cell: HexPos

    def __str__(self) -> str:
        return f"SPAWN({self.cell.r}, {self.cell.q})"


@dataclass(frozen=True, slots=True)
class SpreadAction:
    """
    Spread action. Requires a position where player already occupied to spread, and the direction
    that the piece would spread to.
    Attributes:
        cell: the cell to spread
        direction: spread direction
    """
    cell: HexPos
    direction: HexDir

    def __str__(self) -> str:
        return f"SPREAD({self.cell.r}, {self.cell.q} - " + \
               f"{self.direction})"


Action = SpawnAction | SpreadAction

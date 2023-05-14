"""
Module:
    ``board.py``

Purpose:
    The `Infexion` board representation, and mutation applied to board.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. The actions include spawn in unoccupied cells and spread from
    an already occupied by player position. The script is modified by `The Duy Nguyen (1100548)`.
    Original documentation:

    The Board class encapsulates the state of the game board, and provides methods for applying
    actions to the board and querying/inspecting the state of the game (i.e. which player has won,
    if any).

    This board representation is designed to be used internally by the referee for the purposes of
    validating actions and determining the result of the game.
"""

from collections import defaultdict
from dataclasses import dataclass

from .hex import HexPos, HexDir
from .player import PlayerColor
from .actions import Action, SpawnAction, SpreadAction
from .exceptions import IllegalActionException
from .constants import *


@dataclass(frozen=True, slots=True)
class CellState:
    """
    The CellState class is used to represent the state of a single cell on the game board.
    Attributes:
        player: the player's color occupying the cell, if any
        power : the player's power occupying the cell, if any
    """
    player: PlayerColor | None = None
    power: int = 0

    def __post_init__(self):
        if self.player is None or self.power > MAX_CELL_POWER:
            object.__setattr__(self, "power", 0)
            object.__setattr__(self, "player", None)

    def __str__(self):
        return f"CellState({self.player}, {self.power})"

    def __iter__(self):
        yield self.player
        yield self.power


@dataclass(frozen=True, slots=True)
class CellMutation:
    """
    Class representing a single cell mutation.
    Attributes:
        cell: the mutated cell
        prev: the previous state of the cell
        next: the to-be-mutated state of the cell
    """
    cell: HexPos
    prev: CellState
    next: CellState

    def __str__(self):
        return f"CellMutation({self.cell}, {self.prev}, {self.next})"


@dataclass(frozen=True, slots=True)
class BoardMutation:
    """
    The BoardMutation class is used to represent the *minimal* set of changes in
    the state of the board as a result of an action.
    Attributes:
        action: action which leads to board mutation
        cell_mutations: list of cell mutations as a result of action
    """
    action: Action
    cell_mutations: set[CellMutation]

    def __str__(self):
        return f"BoardMutation({self.cell_mutations})"


def _within_bounds(coord: HexPos) -> bool:
    """
    Check whether a coordinate is within the board's bound.

    Args:
        coord: specified coordinate
    Returns:
        `True` if within bounds, `False` if otherwise
    """
    r, q = coord
    return 0 <= r < BOARD_N and 0 <= q < BOARD_N


class Board:
    """
    Game's board representation. This is the board used by referee.
    """
    __slots__ = [
        "_mutable",
        "_state",
        "_turn_color",
        "_history"
    ]

    def __init__(self, initial_state=None):
        """
        Referee's Board constructor.
        Args:
            initial_state: the initial state of the board.
        """
        if initial_state is None:
            initial_state = {}
        self._state: dict[HexPos, CellState] = defaultdict(lambda: CellState(None, 0))
        self._state.update(initial_state)
        self._turn_color: PlayerColor = PlayerColor.RED
        self._history: list[BoardMutation] = []

    def __getitem__(self, pos: HexPos) -> CellState:
        """
        Get the state of a cell on the board given a position.
        Args:
            pos: the cell's position
        Returns:
            the cell
        """
        if not _within_bounds(pos):
            raise IndexError(f"Cell position '{pos}' is invalid.")
        return self._state[pos]

    def apply_action(self, action: Action):
        """
        Apply an action to a board, mutating the board state. Throws an
        IllegalActionException if the action is invalid.

        Args:
            action: the to be applied action
        """
        match action:
            case SpawnAction():
                res_action = self._resolve_spawn_action(action)
            case SpreadAction():
                res_action = self._resolve_spread_action(action)
            case _:
                raise IllegalActionException(
                    f"Unknown action {action}", self._turn_color)
        for mutation in res_action.cell_mutations:
            self._state[mutation.cell] = mutation.next
        self._history.append(res_action)
        self._turn_color = self._turn_color.opponent

    def undo_action(self):
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        if len(self._history) == 0:
            raise IndexError("No actions to undo.")

        action: BoardMutation = self._history.pop()
        for mutation in action.cell_mutations:
            self._state[mutation.cell] = mutation.prev
        self._turn_color = self._turn_color.opponent

    def render(self, use_color=False, use_unicode=False) -> str:
        """
        Return a visualisation of the game board via a multiline string. The layout corresponds
        to the axial coordinate system as described in the game specification document.
        The method is modified by The Duy Nguyen (1100548).

        Args:
            use_color   : if ansi color is to be applied
            use_unicode : if unicode is to be applied

        Returns:
            The string visualisation of the board
        """
        """
        Return a visualisation of the game board via a multiline string. The
        layout corresponds to the axial coordinate system as described in the
        game specification document.
        """
        def apply_ansi(string, ansi_color=None, bold=False, mutated=False) -> str:
            """
            Apply ansi-format to string. Helper function.

            Args:
                string     : given string
                ansi_color : ansi color to be formatted
                bold       : if string is bold or not
                mutated    : apply ansi if only cell is mutated

            Returns:
                The formatted string
            """
            from ..log import LogColor

            bold_code  = LogColor.BOLD if bold else ""
            color_code = ""
            string = "[".strip() + string.strip() + "]".strip() if mutated else string
            if ansi_color == "r":
                color_code = LogColor.RED
            if ansi_color == "b":
                color_code = LogColor.BLUE
            return f"{bold_code}{color_code}{string}{LogColor.RESET_ALL}"

        def is_mutated(cells_mutated: set[CellMutation], position: HexPos) -> bool:
            """
            Helper method (written by The Duy Nguyen - 1100548) for checking if cell is just
            mutated. This helps to mark positions that are just mutated to make it clearer.

            Args:
                cells_mutated:
                position:

            Returns:
                if cell has been mutated
            """
            if cells_mutated is None:
                return False
            return any([mutated.cell == position for mutated in cells_mutated])

        mutation = self._history[len(self._history) - 1]
        cell_mutations = None if mutation is None else mutation.cell_mutations
        dim = BOARD_N
        output = ""
        for row in range(dim * 2 - 1):
            output += "    " * abs((dim - 1) - row)
            for col in range(dim - abs(row - (dim - 1))):
                # Map row, col to r, q
                r = max((dim - 1) - row, 0) + col
                q = max(row - (dim - 1), 0) + col
                pos = HexPos(r, q)
                if self._cell_occupied(pos):
                    player, power = self._state[pos]
                    color = "r" if player == PlayerColor.RED else "b"
                    text  = f"{color}{power}".center(4)
                    output += apply_ansi(text, ansi_color=color, bold=use_unicode,
                                         mutated=is_mutated(cell_mutations, pos)) \
                        if use_color else text
                else:
                    output += "[__]" if is_mutated(cell_mutations, pos) else " .. "
                output += "    "
            output += "\n"
        return output

    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        """
        return len(self._history)

    @property
    def turn_color(self) -> PlayerColor:
        """
        The player (color) whose turn it is.
        """
        return self._turn_color

    @property
    def game_over(self) -> bool:
        """
        True iff the game is over.
        """
        if self.turn_count < 2:
            return False
        return any([
            self.turn_count >= MAX_TURNS,
            self._color_power(PlayerColor.RED)  == 0,
            self._color_power(PlayerColor.BLUE) == 0
        ])

    @property
    def winner_color(self) -> PlayerColor | None:
        """
        The player (color) who won the game, or None if no player has won.
        """
        if not self.game_over:
            return None

        red_power  = self._color_power(PlayerColor.RED)
        blue_power = self._color_power(PlayerColor.BLUE)
        if abs(red_power - blue_power) < WIN_POWER_DIFF:
            return None
        return (PlayerColor.RED, PlayerColor.BLUE)[red_power < blue_power]

    @property
    def _total_power(self) -> int:
        """
        The total power of all cells on the board.
        """
        return sum(map(lambda cell: cell.power, self._state.values()))

    def _player_cells(self, color: PlayerColor) -> list[CellState]:
        """
        Return all the cells that the player currently occupies.

        Args:
            color: player's color
        Returns:
            list of cells where the player occupies
        """
        return list(filter(
            lambda cell: cell.player == color,
            self._state.values()
        ))

    def _color_power(self, color: PlayerColor) -> int:
        """
        Get the total power of a specific player.

        Args:
            color: player's color
        Returns:
            their total power
        """
        return sum(map(lambda cell: cell.power, self._player_cells(color)))

    def _cell_occupied(self, pos: HexPos) -> bool:
        """
        Check whether the cell is occupied or not by specified position.

        Args:
            pos: specified position
        Returns:
            `True` if occupied, `False` if not
        """
        return self._state[pos].power > 0

    def _validate_action_pos_input(self, pos: HexPos):
        """
        Validating the position is of correct type.
        Args:
            pos: specified position
        """
        if type(pos) != HexPos or not _within_bounds(pos):
            raise IllegalActionException(
                f"'{pos}' is not a valid position.", self._turn_color)

    def _validate_action_dir_input(self, dir: HexDir):
        """
        Validating the direction is of correct type.
        Args:
            dir: specified direction
        """
        if type(dir) != HexDir:
            raise IllegalActionException(
                f"'{dir}' is not a valid direction.", self._turn_color)

    def _validate_spawn_action_input(self, action: SpawnAction):
        """
        Validate the spawn action input by checking its type (has to be of correct spawn
        action type), and all of its information, including the cell has to be of correct
        type as well.

        Args:
            action: the spawn action
        """
        if type(action) != SpawnAction:
            raise IllegalActionException(
                f"Action '{action}' is not a SPAWN action.", self._turn_color)
        self._validate_action_pos_input(action.cell)

    def _validate_spread_action_input(self, action: SpreadAction):
        """
        Validate the spread action input by checking its type (has to be of correct spread
        action type), and all of its information, including cell and direction have to be
        of correct type as well.

        Args:
            action: the spread action
        """
        if type(action) != SpreadAction:
            raise IllegalActionException(
                f"Action '{action}' is not a SPREAD action.", self._turn_color)
        self._validate_action_pos_input(action.cell)
        self._validate_action_dir_input(action.direction)

    def _resolve_spawn_action(self, action: SpawnAction) -> BoardMutation:
        """
        Method to resolve the spawn action before applying on board. It checks whether the
        spawn action is valid, and what mutations will be a result of such spawn action.

        Args:
            action: the spawn action
        Returns:
            the board mutation
        """
        self._validate_spawn_action_input(action)
        cell = action.cell

        # confirm that the spawn action is legal
        if self._total_power >= MAX_TOTAL_POWER:
            raise IllegalActionException(
                f"Total board power max reached ({MAX_TOTAL_POWER})",
                self._turn_color)
        if self._cell_occupied(cell):
            raise IllegalActionException(
                f"Cell {cell} is occupied.", self._turn_color)

        # return the board mutation as a result of spawn action
        return BoardMutation(
            action,
            cell_mutations={CellMutation(
                cell, self._state[cell],
                CellState(self._turn_color, 1)
            )},
        )

    def _resolve_spread_action(self, action: SpreadAction) -> BoardMutation:
        """
        Method to resolve the spread action before applying on board. It checks whether the
        spread action is valid, and what mutations will be a result of such spread action.

        Args:
            action: the spread action
        Returns:
            the board mutation
        """
        self._validate_spread_action_input(action)
        from_cell, dir = action.cell, action.direction
        action_player: PlayerColor = self._turn_color

        # confirm that the spread action is legal
        if self[from_cell].player != action_player:
            raise IllegalActionException(
                f"SPREAD cell {from_cell} not occupied by {action_player}",
                self._turn_color)

        # Compute destination cell coordinates.
        to_cells = [
            from_cell + dir * (i + 1) for i in range(self[from_cell].power)
        ]

        # return the board mutation as a result of the spread action
        return BoardMutation(
            action,
            cell_mutations={
               # Remove token stack from source cell.
               CellMutation(from_cell, self[from_cell], CellState()),
            } | {
               # Add token stack to destination cells.
               CellMutation(to_cell, self[to_cell], CellState(action_player, self[to_cell].power + 1)
                            ) for to_cell in to_cells
            }
        )

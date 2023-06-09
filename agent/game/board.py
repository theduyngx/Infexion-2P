"""
Module:
    ``board.py``

Authors:
    The Duy Nguyen (1100548)

Purpose:
    Includes the representation of the board, and deals with anything 'statically' and directly
    related to the board.

Notes:
    Based on The University of Melbourne COMP30024 Project B skeleton code. The board uses a single
    dense board representation, and makes use of action apply and action undo from skeleton code in
    order to be as space efficient as possible. The time performance tradeoff is minuscule, and in
    fact does provide benefits for the majority of cases.
"""

from collections import defaultdict
from dataclasses import dataclass

from referee.game import HexPos, Action, SpawnAction, SpreadAction, PlayerColor, \
    MAX_CELL_POWER, BOARD_N, MAX_TURNS, MAX_TOTAL_POWER, WIN_POWER_DIFF
from .constants import *


@dataclass(frozen=True, slots=True)
class CellState:
    """
    The ``CellState`` class is used to represent the state of a single cell on the game board.
    Based on The University of Melbourne COMP30024 Project B skeleton code for class CellState.
    Attributes:
        pos   : the position of the cell
        color : the color of player currently occupied in cell, if there's any
        power : the stack power of the piece (if any) on cell
    """
    pos   : HexPos
    color : PlayerColor | None = None
    power : int = EMPTY_POWER

    def __post_init__(self):
        if self.color is None or self.power > MAX_CELL_POWER:
            object.__setattr__(self, "power" , EMPTY_POWER)
            object.__setattr__(self, "color", None)

    def __str__(self):
        return f"CellState({self.pos.r}, {self.pos.q}, {self.color}, {self.power})"

    def __iter__(self):
        yield self.color
        yield self.power


@dataclass(frozen=True, slots=True)
class CellMutation:
    """
    Class ``CellMutation`` represents the mutated state (before and after) of the cell.
    Based on The University of Melbourne COMP30024 Project B skeleton code for class CellState.
    Attributes:
        pos  : the position of the cell
        prev : the previous state of the cell
        next : the subsequent state after mutation
    """
    pos : HexPos
    prev: CellState
    next: CellState


@dataclass(frozen=True, slots=True)
class BoardMutation:
    """
    The ``BoardMutation`` class is used to represent the *minimal* set of changes in the state
    of the board as a result of an action. In other words, it is designed to be well-optimized.
    Based on The University of Melbourne COMP30024 Project B skeleton code for class CellState.
    Attributes:
        action         : the action applied onto board
        cell_mutations : the set of cell mutations as a result of action
    """
    action: Action
    cell_mutations: set[CellMutation]


class Board:
    """
    The ``Board`` class encapsulates the state of the game board, and provides methods for applying
    actions and querying/inspecting the state of the game (i.e. which player has won, if any).

    Attributes:
        _state      : the board's state
        _turn_color : the color for the turn, applicable to play-testing
        _true_turn  : the true turn, not applicable to play-testing
        _turn_count : the number of plays already made to the board, applicable to play-testing
    """
    __slots__ = [
        "_mutable",
        "_state",
        "_turn_color",
        "_true_turn",
        "_non_concrete_history",
        "_turn_count"
    ]

    def __init__(self, initial_state: dict[HexPos, CellState] = None):
        """
        Board constructor. The attribute state has key being the hashed value of the hex position of
        the cell, and the value being the cell and its state.

        Args:
            initial_state:
                * board's state, default being an empty dictionary;
                * the key is the hashed value of the position,
                * the value is the state of the cell at specified position
        """
        # the state uses dense representation, which also stores the empty cells
        self._state: dict[HexPos, CellState] = defaultdict()
        if initial_state is None:
            initial_state = {}
        for r in range(BOARD_N):
            for q in range(BOARD_N):
                pos = HexPos(r, q)
                if pos not in initial_state:
                    initial_state[pos] = CellState(pos)
                else:
                    assert initial_state[pos].power > EMPTY_POWER and initial_state[pos].color

        # other properties initialized
        self._state.update(initial_state)
        self._turn_count: int = 0
        self._turn_color: PlayerColor = PlayerColor.RED
        self._true_turn : PlayerColor = PlayerColor.RED
        self._non_concrete_history: list[BoardMutation] = []

    def __getitem__(self, pos: HexPos) -> CellState:
        """
        Return the state of a cell on the board.
        Args:
            pos: specified position
        """
        return self._state[pos]

    def __setitem__(self, pos: HexPos, cell: CellState):
        """
        Add a new entry to state.

        Args:
            pos  : the cell position
            cell : the state of the cell
        """
        self._state[pos] = cell

    def __contains__(self, pos: HexPos) -> bool:
        """
        Check if a position is occupied by a piece within the board or not.
        Args:
            pos: specified position
        """
        return pos in self._state and self[pos].power > EMPTY_POWER

    def __hash__(self) -> int:
        """
        State hashed value.
        """
        return hash(frozenset(self.get_cells()))

    def get_cells(self):
        """
        Get the board's cells.
        """
        return self._state.values()

    def non_concrete_history_empty(self) -> bool:
        """
        Assertion method - making sure that the non-concrete history is empty.
        """
        return not self._non_concrete_history

    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        """
        return self._turn_count

    @property
    def turn_color(self) -> PlayerColor:
        """
        The player (color) whose turn it is.
        """
        return self._turn_color

    @property
    def true_turn(self) -> PlayerColor:
        """
        Get which player's turn is it truly.
        """
        return self._true_turn

    @property
    def game_over(self) -> bool:
        """
        Check if the game is over or not, meaning if a player has won the game.
        Returns:
            true if game is over
        """
        return self.turn_count >= MIN_MOVE_WIN and (
                   self.turn_count >= MAX_TURNS or
                   self.color_power(PlayerColor.RED)  == EMPTY_POWER or
                   self.color_power(PlayerColor.BLUE) == EMPTY_POWER
               )

    def player_wins(self, player: PlayerColor) -> bool:
        """
        Check if specified player has won the game.

        Args:
            player: specified player, denoted by their color
        Returns:
            `True` if won, `False` if not
        """
        return self.game_over and (
                   self.color_power(player.opponent) == EMPTY_POWER or
                   self.color_power(player) - self.color_power(player.opponent) > WIN_POWER_DIFF
               )

    def total_power(self) -> int:
        """
        The total power of all cells on the board.
        """
        return sum(map(lambda cell: cell.power, self.get_cells()))

    def player_cells(self, color: PlayerColor) -> list[CellState]:
        """
        Get the list of cells of specified player's

        Args:
            color: the player's color
        Returns:
            the list of cells that specified player occupies
        """
        return list(filter(
            lambda cell: cell.color == color,
            self.get_cells()
        ))

    def num_players(self, color: PlayerColor) -> int:
        """
        Get the number of player pieces currently on the board

        Args:
            color: the player's color
        Returns:
            number of player pieces
        """
        return len(self.player_cells(color))

    def color_power(self, color: PlayerColor) -> int:
        """
        Method getting the current total power of a specified player.

        Args:
            color: the player's color
        Returns:
            their power
        """
        return sum(map(lambda cell: cell.power, self.player_cells(color)))

    def color_number_and_power(self, color: PlayerColor) -> (int, int):
        """
        Method getting the current total power of a specified player and the number of pieces.

        Args:
            color: the player's color
        Returns:
            * player's number of pieces on board
            * player's total power
        """
        color_cells = list(map(lambda cell: cell.power, self.player_cells(color)))
        return len(color_cells), sum(color_cells)

    def pos_occupied(self, pos: HexPos) -> bool:
        """
        Check if a specified cell is occupied in the board or not.

        Args:
            pos: specified cell's coordinates
        Returns:
            `True` if cell is occupied, `False` if not
        """
        return self[pos].power > EMPTY_POWER

    def spawn(self, action: SpawnAction) -> BoardMutation:
        """
        Spawn action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.

        Args:
            action: the specified spawn action applied to board
        Returns:
            the board mutation
        """
        pos = action.cell

        # exception handling
        if self.total_power() >= MAX_TOTAL_POWER:
            raise Exception("SPAWN: total power exceeded")
        if self.pos_occupied(pos):
            raise Exception("SPAWN: cell occupied")

        # minimal, efficient board mutation
        return BoardMutation(
            action,
            cell_mutations={
                CellMutation(
                    pos,
                    self[pos],
                    CellState(pos, self.turn_color, 1)
                )
            },
        )

    def spread(self, action: SpreadAction) -> BoardMutation:
        """
        Spread action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.

        Args:
            action: the specified spread action applied to board
        Returns:
            board mutation
        """
        from_cell, dir = action.cell, action.direction
        player_color: PlayerColor = self.turn_color

        # exception handling
        if self[from_cell].power == 0:
            raise Exception("SPREAD: cell is empty")
        if self[from_cell].color != player_color:
            raise Exception("SPREAD: cell " + str(from_cell) + " has color " + str(self[from_cell].color) +
                            " which differs " + str(player_color))

        # Compute destination cell coordinates.
        to_cells = [
            from_cell + dir * (i + 1) for i in range(self[from_cell].power)
        ]

        # minimal, efficient board mutation
        return BoardMutation(
            action,
            cell_mutations = {
                # Remove the piece that is currently in the position of action
                CellMutation(from_cell, self[from_cell], CellState(from_cell)),
            } | {
                # Cells that get spread to will now be occupied by player
                CellMutation(
                    to_cell, self[to_cell], CellState(to_cell, player_color, self[to_cell].power + 1)
                ) for to_cell in to_cells
            }
        )

    def apply_action(self, action: Action, concrete=True):
        """
        Apply an action to a board, mutating the board state.

        Args:
            action   : the specified action applied to board
            concrete :
                * `True` if action is non-concrete (an applied action within search)
                * `False` if otherwise
        """
        match action:
            case SpawnAction():
                board_mutation = self.spawn(action)
            case SpreadAction():
                board_mutation = self.spread(action)
            case _:
                raise Exception("apply_action: action not of valid type")

        for mutation in board_mutation.cell_mutations:
            self[mutation.pos] = mutation.next

        # only add to history in the case where it is going down the search tree
        self._turn_color = self.turn_color.opponent
        self._turn_count += 1
        if not concrete:
            self._non_concrete_history.append(board_mutation)
        else:
            self._true_turn = self._turn_color

    def undo_action(self):
        """
        Undo the last action played, mutating the board state. This is a method specifically
        used for undoing non-concrete actions, or in other words, actions that are simply
        play-testing. Any concrete action is absolute, as the referee exacted.
        """
        if not self._non_concrete_history:
            return
        board_mutation: BoardMutation = self._non_concrete_history.pop()
        for mutation in board_mutation.cell_mutations:
            self[mutation.pos] = mutation.prev
        self._turn_color = self.turn_color.opponent
        self._turn_count -= 1

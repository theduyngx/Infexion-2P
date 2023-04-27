# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from collections import defaultdict
from dataclasses import dataclass

from referee.game import HexPos, PlayerColor, Action, SpawnAction, SpreadAction
from referee.game.constants import *


# The CellState class is used to represent the state of a single cell on the game board.

@dataclass(frozen=True, slots=True)
class CellState:
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
    cell: HexPos
    prev: CellState
    next: CellState


# The BoardMutation class is used to represent the *minimal* set of changes in
# the state of the board as a result of an action.

@dataclass(frozen=True, slots=True)
class BoardMutation:
    action: Action
    cell_mutations: set[CellMutation]


# The Board class encapsulates the state of the game board, and provides
# methods for applying actions to the board and querying/inspecting the state
# of the game (i.e. which player has won, if any).
#
# NOTE: This board representation is designed to be used internally by the
# referee for the purposes of validating actions and determining the result of
# the game. Don't assume this class is an "ideal" board representation for your
# own agent; you should think carefully about how to design data structures for
# representing the state of a game with respect to your chosen strategy.


class Board:
    __slots__ = [
        "_mutable",
        "_state",
        "_empty",
        "_turn_color",
        "_history"
    ]

    def __init__(self, initial_state: dict[HexPos, CellState] = None):
        """
        Board constructor.
        @param initial_state: board's state, if just initialized then it will be an empty dictionary
        """
        if initial_state is None:
            initial_state = {}
        self._state: dict[HexPos, CellState] = defaultdict(lambda: CellState(None, 0))
        self._empty: dict[HexPos, CellState] = defaultdict(lambda: CellState(None, 0))

        ### INELEGANT EMPTY CELL INIT
        initial_empty = {}
        for r in range(BOARD_N):
            for q in range(BOARD_N):
                pos = HexPos(r, q)
                if pos not in initial_state:
                    initial_empty[pos] = CellState(None, 0)
        ###

        self._state.update(initial_state)
        self._empty.update(initial_empty)
        self._turn_color: PlayerColor = PlayerColor.RED
        self._history: list[BoardMutation] = []

    def __getitem__(self, cell: HexPos) -> CellState:
        """
        Return the state of a cell on the board.
        @param cell: specified cell;
        @return    : cell's state
        """
        # if cell in self._state:
        #     pass
        return self._state[cell]

    def empty_cell(self, cell: HexPos) -> bool:
        """
        Check if a cell is empty or not.
        @param cell : specified cell
        @return     : boolean whether cell is empty or not
        """
        return cell in self._empty

    def apply_action(self, action: Action, concrete=True):
        """
        Apply an action to a board, mutating the board state.
        @param action   : specified action to be applied
        @param concrete : whether the action is only an evaluation (non-concrete) or an actual move (concrete)
        """
        match action:
            case SpawnAction():
                res_action = self.spawn(action)
            case SpreadAction():
                res_action = self.spread(action)
            case _:
                return

        for mutation in res_action.cell_mutations:
            self._state[mutation.cell] = mutation.next
            ### UPDATE EMPTY CELLS - not entirely sure if this is correct just yet
            del self._empty[mutation.cell]
            ###
        if not concrete:
            self._history.append(res_action)
        self._turn_color = self._turn_color.opponent

    def undo_action(self):
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        if len(self._history) == 0:
            return
        action: BoardMutation = self._history.pop()
        for mutation in action.cell_mutations:
            self._state[mutation.cell] = mutation.prev
        self._turn_color = self._turn_color.opponent

    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        @return: number of performed actions thus far
        """
        return len(self._history)

    @property
    def turn_color(self) -> PlayerColor:
        """
        The player (color) whose turn it is.
        @return: color of player who is at their turn
        """
        return self._turn_color

    @property
    def game_over(self) -> bool:
        """
        Check if the game is over or not, meaning if a player has won the game.
        @return: true if game is over
        """
        if self.turn_count < 2:
            return False

        return any([
            self.turn_count >= MAX_TURNS,
            self._color_power(PlayerColor.RED) == 0,
            self._color_power(PlayerColor.BLUE) == 0
        ])

    def total_power(self) -> int:
        """
        The total power of all cells on the board.
        @return: total power
        """
        return sum(map(lambda cell: cell.power, self._state.values()))

    def _player_cells(self, color: PlayerColor) -> list[CellState]:
        """
        Get the list of cells of specified player's
        @param color: the player's color
        @return     : the list of cells that specified player occupies
        """
        return list(filter(
            lambda cell: cell.player == color,
            self._state.values()
        ))

    def num_players(self, color: PlayerColor) -> int:
        """
        Get the number of player pieces currently on the board
        @param color: the player's color
        @return     : number of player pieces
        """
        return len(self._player_cells(color))

    def _color_power(self, color: PlayerColor) -> int:
        """
        Protected method getting the current total power of a specified player.
        @param color: player's color
        @return     : their power
        """
        return sum(map(lambda cell: cell.power, self._player_cells(color)))

    def player_movable_cells(self, color: PlayerColor) -> dict[HexPos, CellState]:
        """
        Get all movable cells of the specified player.
        @param color : player's color
        @return      : a dictionary of movable cells, where the key is the cell's position
        """
        empty_cells  = self._empty
        player_cells = dict((pos, cell) for pos, cell in self._state.items() if cell.player == color)
        if self.total_power() < MAX_TOTAL_POWER:
            player_cells.update(empty_cells)
        return player_cells

    def cell_occupied(self, coord: HexPos) -> bool:
        """
        Check if a specified cell is occupied in the board or not.
        @param coord: specified cell's coordinates
        @return     : boolean denoting whether cell is occupied or not
        """
        return self._state[coord].power > 0

    def spawn(self, action: SpawnAction) -> BoardMutation:
        """
        Spawn action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.
        @param action: the specified spawn action applied to board
        @return      : the board mutation
        """
        cell = action.cell
        return BoardMutation(
            action,
            cell_mutations={
                CellMutation(
                    cell,
                    self._state[cell],
                    CellState(self._turn_color, 1)
                )
            },
        )

    def spread(self, action: SpreadAction) -> BoardMutation:
        """
        Spread action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.
        @param action: specified spread action
        @return      : board mutation
        """
        from_cell, dir = action.cell, action.direction
        action_player: PlayerColor = self._turn_color

        # Compute destination cell coords.
        to_cells = [
            from_cell + dir * (i + 1) for i in range(self[from_cell].power)
        ]

        return BoardMutation(
            action,
            cell_mutations = {
                # Remove token stack from source cell.
                CellMutation(from_cell, self[from_cell], CellState()),
            } | {
                # Add token stack to destination cells.
                CellMutation(
                    to_cell, self[to_cell], CellState(action_player, self[to_cell].power + 1)
                ) for to_cell in to_cells
            }
        )

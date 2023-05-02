from collections import defaultdict
from dataclasses import dataclass

from referee.game import HexPos, PlayerColor, Action, SpawnAction, SpreadAction, HexDir
from referee.game.constants import *


# Constants
EMPTY_POWER    : int = 0
MIN_MOVE_WIN   : int = 2
PLAYER_COLOR   : PlayerColor = PlayerColor.RED
OPPONENT_COLOR : PlayerColor = PLAYER_COLOR.opponent


@dataclass(frozen=True, slots=True)
class CellState:
    """
    The CellState class is used to represent the state of a single cell on the game board.
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
    Class CellMutation represents the mutated state (before and after) of the cell.
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
    The BoardMutation class is used to represent the *minimal* set of changes in the state of the
    board as a result of an action. In other words, it is designed to be well-optimized.
    Based on The University of Melbourne COMP30024 Project B skeleton code for class CellState.
    Attributes:
        action         : the action applied onto board
        cell_mutations : the set of cell mutations as a result of action
    """
    action: Action
    cell_mutations: set[CellMutation]


def adjacent_positions(pos: HexPos) -> list[HexPos]:
    """
    Get all adjacent positions to the specified one.
    @param pos : the specified position
    @return    : list of 6 of its adjacent positions
    """
    adjacent_list = []
    for dir in HexDir:
        r_coord = pos.r + dir.value.r
        q_coord = pos.q + dir.value.q
        if r_coord < 0:
            r_coord += BOARD_N
        elif r_coord >= BOARD_N:
            r_coord -= BOARD_N
        if q_coord < 0:
            q_coord += BOARD_N
        elif q_coord >= BOARD_N:
            q_coord -= BOARD_N
        adjacent_list.append(HexPos(r_coord, q_coord))
    return adjacent_list


class Board:
    """
    The Board class encapsulates the state of the game board, and provides methods for applying actions
    to the board and querying/inspecting the state of the game (i.e. which player has won, if any).
    <p></p>
    NOTE: This board representation is designed to be used internally by the referee, as stated in the
    skeleton code. It might not be ideal, so we probably have to think of something better. For now,
    this is very space efficient. It is however not the most time-efficient board representation.
    <p></p>
    Based on The University of Melbourne COMP30024 Project B skeleton code for class CellState.
    """
    __slots__ = [
        "_mutable",
        "_state",
        "_turn_color",
        "_non_concrete_history",
        "_turn_count"
    ]

    def __init__(self, initial_state: dict[int, CellState] = None):
        """
        Board constructor. The attribute state has key being the hashed value of the hex position of
        the cell, and the value being the cell and its state.
        @param initial_state: board's state, if just initialized then it will be an empty dictionary
        """
        self._state: dict[int, CellState] = defaultdict()

        ### INELEGANT EMPTY CELL INIT
        if initial_state is None:
            initial_state = {}
        for r in range(BOARD_N):
            for q in range(BOARD_N):
                pos = HexPos(r, q)
                hash_pos = pos.__hash__()
                if hash_pos not in initial_state:
                    initial_state[hash_pos] = CellState(pos)

        self._state.update(initial_state)
        self._turn_color: PlayerColor = PLAYER_COLOR
        self._turn_count: int = 0
        self._non_concrete_history: list[BoardMutation] = []

    def __getitem__(self, pos: HexPos) -> CellState:
        """
        Return the state of a cell on the board.
        @param pos : specified cell;
        @return    : cell's state
        """
        return self._state[pos.__hash__()]

    def __setitem__(self, pos: HexPos, state: CellState):
        """
        Add a new entry to state.
        @param pos   : the cell position
        @param state : the state of the cell
        """
        self._state[pos.__hash__()] = state

    def __contains__(self, pos: HexPos) -> bool:
        """
        Check if a position is occupied by a piece within the board or not.
        @param pos : the specified position
        @return    : boolean indicating whether the position is occupied or not
        """
        return self._state[pos.__hash__()].power > EMPTY_POWER

    def get_cells(self):
        """
        Get the board's cells.
        @return: the board's cells.
        """
        return self._state.values()

    def apply_action(self, action: Action, concrete=True):
        """
        Apply an action to a board, mutating the board state.
        @param action   : specified action to be applied
        @param concrete : whether action is non-concrete (an applied action within search), or otherwise
        """
        match action:
            case SpawnAction():
                res_action = self.spawn(action)
            case SpreadAction():
                res_action = self.spread(action)
            case _:
                return

        for mutation in res_action.cell_mutations:
            self[mutation.pos] = mutation.next

        # only add to history in the case where it is going down the search tree
        if not concrete:
            self._non_concrete_history.append(res_action)
        self._turn_color = self._turn_color.opponent
        self._turn_count += 1

    def undo_action(self):
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        if not self._non_concrete_history:
            return
        action: BoardMutation = self._non_concrete_history.pop()
        for mutation in action.cell_mutations:
            self[mutation.pos] = mutation.prev
        self._turn_color = self._turn_color.opponent
        self._turn_count -= 1

    def non_concrete_history_empty(self) -> bool:
        """
        Assertion method - making sure that the non-concrete history is empty.
        @return: true if non-concrete history is empty
        """
        return not self._non_concrete_history

    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        @return: number of performed actions thus far
        """
        return self._turn_count

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
        if self.turn_count < MIN_MOVE_WIN:
            return False

        return any([
            self.turn_count >= MAX_TURNS,
            self.color_power(PLAYER_COLOR)   == EMPTY_POWER,
            self.color_power(OPPONENT_COLOR) == EMPTY_POWER
        ])

    def total_power(self) -> int:
        """
        The total power of all cells on the board.
        @return: total power
        """
        return sum(map(lambda cell: cell.power, self._state.values()))

    def player_cells(self, color: PlayerColor) -> list[CellState]:
        """
        Get the list of cells of specified player's
        @param color : the player's color
        @return      : the list of cells that specified player occupies
        """
        return list(filter(
            lambda cell: cell.color == color,
            self._state.values()
        ))

    def num_players(self, color: PlayerColor) -> int:
        """
        Get the number of player pieces currently on the board
        @param color : the player's color
        @return      : number of player pieces
        """
        return len(self.player_cells(color))

    def color_power(self, color: PlayerColor) -> int:
        """
        Protected method getting the current total power of a specified player.
        @param color : player's color
        @return      : their power
        """
        return sum(map(lambda cell: cell.power, self.player_cells(color)))

    def player_movable_cells(self, color: PlayerColor) -> list[CellState]:
        """
        Get all movable cells of the specified player.
        @param color : player's color
        @return      : a dictionary of movable cells, where the key is the cell's position
        """
        return [cell for hash_pos, cell in self._state.items()
                if cell.color == color or (self.total_power() < MAX_TOTAL_POWER and cell.power == EMPTY_POWER)]

    def cell_occupied(self, pos: HexPos) -> bool:
        """
        Check if a specified cell is occupied in the board or not.
        @param pos : specified cell's coordinates
        @return    : boolean denoting whether cell is occupied or not
        """
        return self[pos].power > EMPTY_POWER

    def spawn(self, action: SpawnAction) -> BoardMutation:
        """
        Spawn action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.
        @param action : the specified spawn action applied to board
        @return       : the board mutation
        """
        pos = action.cell
        return BoardMutation(
            action,
            cell_mutations={
                CellMutation(
                    pos,
                    self[pos],
                    CellState(pos, self._turn_color, 1)
                )
            },
        )

    def spread(self, action: SpreadAction) -> BoardMutation:
        """
        Spread action applied to the board. It shouldn't check for illegal moves so far to allow for
        possibility of trial and error when testing with agent's board.
        @param action : specified spread action
        @return       : board mutation
        """
        from_cell, dir = action.cell, action.direction
        action_player: PlayerColor = self._turn_color

        # Compute destination cell coords.
        to_cells = [
            from_cell + dir * (i + 1) for i in range(self[from_cell].power)
        ]

        for to_cell in to_cells:
            if not self.cell_occupied(to_cell):
                self[to_cell] = CellState(to_cell)

        return BoardMutation(
            action,
            cell_mutations = {
                # Remove token stack from source cell.
                CellMutation(from_cell, self[from_cell], CellState(action.cell)),
            } | {
                # Add token stack to destination cells.
                CellMutation(
                    to_cell, self[to_cell], CellState(action.cell, action_player, self[to_cell].power + 1)
                ) for to_cell in to_cells
            }
        )

    def get_legal_moves(self, color: PlayerColor) -> list[Action]:
        """
        Get all possible legal moves of a specified player color from a specific state of the board.
        @param color : specified player's color
        @return      : list of all actions that could be applied to board
        """
        # for every possible move from a given board state, including SPAWN and SPREAD
        actions: list[Action] = []
        movable_dict: list[CellState] = self.player_movable_cells(color)
        for state in movable_dict:
            # append spawn actions
            pos = state.pos
            if not self.cell_occupied(pos):
                actions.append(SpawnAction(pos))
            # append spread actions for each direction
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])
        return actions

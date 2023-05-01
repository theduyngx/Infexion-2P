from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexDir
from .board import Board, CellState
from .minimax import minimax


def search(board: Board, color: PlayerColor) -> Action:
    """
    Search the best subsequent move for agent. It will be using a hybrid of search algorithms and
    pruning techniques, namely Minimax and Monte Carlo tree search algorithms.
    @param board : the board
    @param color : the agent's color
    @return      : the action to take for agent
    """
    return minimax(board, color)


def get_legal_moves(board: Board, color: PlayerColor) -> list[Action]:
    """
    Get all possible legal moves of a specified player color from a specific state of the board.
    @param board : the board
    @param color : specified player's color
    @return      : list of all actions that could be applied to board
    """
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: list[Action] = []
    movable_dict: list[CellState] = board.player_movable_cells(color)
    for state in movable_dict:
        # append spawn actions
        pos = state.pos
        if not board.cell_occupied(pos):
            actions.append(SpawnAction(pos))
        # append spread actions for each direction
        else:
            actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    return actions

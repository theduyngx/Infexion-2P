from referee.game import PlayerColor, Action
from .board import Board
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

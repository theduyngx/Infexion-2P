from random import randint

from agent.board import Board
from agent.action import get_child_nodes
from referee.game import Action, PlayerColor


def random_move(board: Board, color: PlayerColor) -> Action:
    """
    Agent's move approach where it picks any random move from all of its possible move set.
    @param board : the current state of the board
    @param color : the agent's color (it is its turn)
    @return      : the random action to be taken by agent
    """
    actions: list[Action] = get_child_nodes(board, color)
    random_index: int = randint(0, len(actions)-1)
    return actions[random_index]

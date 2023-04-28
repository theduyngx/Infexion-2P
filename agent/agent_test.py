from random import randint

from agent.board import Board
from agent.action import get_child_nodes
from referee.game import Action, PlayerColor


def random_move(board: Board, color: PlayerColor) -> Action:
    actions: list[Action] = get_child_nodes(board, color)
    random_index: int = randint(0, len(actions)-1)
    return actions[random_index]

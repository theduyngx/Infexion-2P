# evaluation function
from agent import Agent
from referee.game import PlayerColor
from .board import Board


def evaluate(board: Board, agent: Agent) -> float:
    # for now let's only consider Material
    player_color: PlayerColor = agent.get_color()
    power_diff = board.num_players(player_color) - board.num_players(player_color.opponent)
    return power_diff

"""
    Module  : evaluation.py
    Purpose : Includes the evaluation function to evaluate the desirability of a given state of
              the board.

The evaluation function will make use of information such as the number of pieces of a given side
currently on the board, the total power, as well as their clusters.
"""

from .cluster import create_clusters
from referee.game import PlayerColor
from .board import Board, PLAYER_COLOR
from .constants import INF

# weighting factors
NUM_PIECE_FACTOR       : float = 1.8
POWER_PIECE_FACTOR     : float = 1.7
NUM_CLUSTER_FACTOR     : float = 1.2
SIZE_CLUSTER_FACTOR    : float = 1.4
SIZE_DOMINANCE_FACTOR  : float = 1.55
POWER_DOMINANCE_FACTOR : float = 0.45


def evaluate(board: Board) -> (float, float):
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # player power evaluation
    num_blue, pow_blue = board.color_number_and_power(PlayerColor.BLUE)
    num_red , pow_red  = board.color_number_and_power(PlayerColor.RED)
    value  = (num_red - num_blue) * NUM_PIECE_FACTOR
    value += (pow_red - pow_blue) * POWER_PIECE_FACTOR

    # monte-carlo evaluation value
    monte_carlo_val = 0

    if num_blue == 0:
        return INF, INF
    if num_red == 0:
        return -INF, -INF

    # clusters and dominance evaluation
    clusters = create_clusters(board)
    num_player_clusters    = 0
    num_player_dominates   = 0
    pow_player_dominates   = 0
    num_opponent_clusters  = 0
    num_opponent_dominates = 0
    pow_opponent_dominates = 0
    for cluster in clusters.values():
        sign = 1 if cluster.color == PlayerColor.RED else -1

        # player's cluster
        if cluster.color == PLAYER_COLOR:
            num_player_clusters += 1
            # dominance factor is checked solely via player pieces
            for opponent in cluster.get_opponents():
                opponent_cluster = clusters[opponent]

                # cluster size dominance
                if len(cluster) < len(opponent_cluster):
                    num_opponent_dominates += sign
                elif len(cluster) > len(opponent_cluster):
                    num_player_dominates += sign

                # cluster power dominance
                if cluster.get_power() < opponent_cluster.get_power():
                    pow_opponent_dominates += sign
                elif cluster.get_power() > opponent_cluster.get_power():
                    pow_player_dominates += sign

        # opponent's cluster
        else:
            num_opponent_clusters += 1

        # cluster and dominance factor add-on, respectively
        value += sign * len(cluster) * SIZE_CLUSTER_FACTOR
        value += (num_player_dominates - num_opponent_dominates) * SIZE_DOMINANCE_FACTOR
        value += (pow_player_dominates - pow_opponent_dominates) * POWER_DOMINANCE_FACTOR
    value += (num_player_clusters - num_opponent_clusters) * NUM_CLUSTER_FACTOR

    # RAJA: Adding another return value specifically for ordering
    # the heapq for MonteCarlo
    monte_carlo_val += (num_player_clusters + num_player_dominates + pow_player_dominates)
    monte_carlo_val /= (num_opponent_clusters + num_opponent_dominates + pow_opponent_dominates)

    return value, monte_carlo_val

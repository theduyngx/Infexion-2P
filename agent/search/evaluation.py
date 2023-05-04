"""
    Module  : evaluation.py
    Purpose : Includes the evaluation function to evaluate the desirability of a given state of
              the board.

The evaluation function will make use of information such as the number of pieces of a given side
currently on the board, the total power, as well as their clusters.
"""

from referee.game import PlayerColor
from agent.game import Board, PLAYER_COLOR, INF
from .cluster import create_clusters

# weighting factors
NUM_PIECE_FACTOR     : float = 1.8
POW_PIECE_FACTOR     : float = 1.7
NUM_CLUSTER_FACTOR   : float = 1.2
SIZE_CLUSTER_FACTOR  : float = 1.4
NUM_DOMINANCE_FACTOR : float = 1.55
POW_DOMINANCE_FACTOR : float = 0.45


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the
    more 'negative' the evaluated value, the worse it is for the RED player and, conversely,
    the better it is for the BLUE player. In other words, it is a zero-sum evaluation function,
    suitably applied to the zero-sum Infexion game.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # player power evaluation
    num_blue, pow_blue = board.color_number_and_power(PlayerColor.BLUE)
    num_red , pow_red  = board.color_number_and_power(PlayerColor.RED)
    value  = (num_red - num_blue) * NUM_PIECE_FACTOR
    value += (pow_red - pow_blue) * POW_PIECE_FACTOR

    if num_blue == 0:
        return INF
    if num_red == 0:
        return -INF

    # clusters and dominance evaluation
    clusters = create_clusters(board)
    num_player_clusters    = 0
    num_player_dominates   = 0
    pow_player_dominates   = 0
    size_player_clusters   = 0
    num_opponent_clusters  = 0
    num_opponent_dominates = 0
    pow_opponent_dominates = 0
    size_opponent_clusters = 0
    for cluster in clusters.values():

        # player's cluster
        if cluster.color == PLAYER_COLOR:
            num_player_clusters  += 1
            size_player_clusters += len(cluster)
            # dominance factor is checked solely via player pieces
            for opponent in cluster.get_opponents():
                opponent_cluster = clusters[opponent]

                # cluster size dominance
                if len(cluster) < len(opponent_cluster):
                    num_opponent_dominates += 1
                elif len(cluster) > len(opponent_cluster):
                    num_player_dominates += 1

                # cluster power dominance
                if cluster.get_power() < opponent_cluster.get_power():
                    pow_opponent_dominates += 1
                elif cluster.get_power() > opponent_cluster.get_power():
                    pow_player_dominates += 1

        # opponent's cluster
        else:
            num_opponent_clusters  += 1
            size_opponent_clusters += len(cluster)

    # cluster and dominance factor add-on, respectively
    sign = 1 if PLAYER_COLOR == PlayerColor.RED else -1
    value += (size_player_clusters - size_opponent_clusters) * SIZE_CLUSTER_FACTOR
    value += (num_player_dominates - num_opponent_dominates) * NUM_DOMINANCE_FACTOR
    value += (pow_player_dominates - pow_opponent_dominates) * POW_DOMINANCE_FACTOR
    value += (num_player_clusters  - num_opponent_clusters ) * NUM_CLUSTER_FACTOR
    return value * sign


def mc_evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the state of the board after a monte carlo simulation.
    This is not a zero-sum evaluation function, but an evaluation function for the simulation.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # player power evaluation
    num_blue, pow_blue = board.color_number_and_power(PlayerColor.BLUE)
    num_red , pow_red  = board.color_number_and_power(PlayerColor.RED)
    value  = (num_red - num_blue) * NUM_PIECE_FACTOR
    value += (pow_red - pow_blue) * POW_PIECE_FACTOR

    if num_blue == 0:
        return INF
    if num_red == 0:
        return -INF

    # clusters and dominance evaluation
    clusters = create_clusters(board)
    num_player_clusters    = 0
    num_player_dominates   = 0
    pow_player_dominates   = 0
    size_player_clusters   = 0
    num_opponent_clusters  = 0
    num_opponent_dominates = 0
    pow_opponent_dominates = 0
    size_opponent_clusters = 0
    for cluster in clusters.values():

        # player's cluster
        if cluster.color == PLAYER_COLOR:
            num_player_clusters  += 1
            size_player_clusters += len(cluster)
            # dominance factor is checked solely via player pieces
            for opponent in cluster.get_opponents():
                opponent_cluster = clusters[opponent]

                # cluster size dominance
                if len(cluster) < len(opponent_cluster):
                    num_opponent_dominates += 1
                elif len(cluster) > len(opponent_cluster):
                    num_player_dominates += 1

                # cluster power dominance
                if cluster.get_power() < opponent_cluster.get_power():
                    pow_opponent_dominates += 1
                elif cluster.get_power() > opponent_cluster.get_power():
                    pow_player_dominates += 1

        # opponent's cluster
        else:
            num_opponent_clusters  += 1
            size_opponent_clusters += len(cluster)

    # adding another return value specifically for ordering the heapq for MonteCarlo
    player_val   = num_player_clusters    * NUM_CLUSTER_FACTOR   + \
                   size_player_clusters   * SIZE_CLUSTER_FACTOR  + \
                   num_player_dominates   * NUM_DOMINANCE_FACTOR + \
                   pow_player_dominates   * POW_DOMINANCE_FACTOR
    opponent_val = num_opponent_clusters  * NUM_CLUSTER_FACTOR   + \
                   size_opponent_clusters * SIZE_CLUSTER_FACTOR  + \
                   num_opponent_dominates * NUM_DOMINANCE_FACTOR + \
                   pow_opponent_dominates * POW_DOMINANCE_FACTOR
    return player_val / (player_val + opponent_val)

from .cluster import create_clusters
from referee.game import PlayerColor
from .board import Board, PLAYER_COLOR

PIECE_POWER_FACTOR     : float = 3.0
NUM_CLUSTER_FACTOR     : float = 1.2
SIZE_CLUSTER_FACTOR    : float = 1.4
SIZE_DOMINANCE_FACTOR  : float = 1.5
POWER_DOMINANCE_FACTOR : float = 0.8


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.

    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # player power evaluation
    pow_blue = board.color_power(PlayerColor.BLUE)
    pow_red  = board.color_power(PlayerColor.RED)
    value    = (pow_red - pow_blue) * PIECE_POWER_FACTOR

    # clusters and dominance evaluation
    clusters = create_clusters(board)
    num_red_clusters    = 0
    num_blue_clusters   = 0
    num_red_dominates   = 0
    num_blue_dominates  = 0
    size_red_dominates  = 0
    size_blue_dominates = 0
    for cluster in clusters.values():
        if cluster.color == PlayerColor.RED:
            sign = 1
            num_red_clusters += 1
        else:
            sign = -1
            num_blue_clusters += 1

        # dominance factor is checked solely via player pieces
        if cluster.color == PLAYER_COLOR:
            for opponent in cluster.get_opponents():
                opponent_cluster = clusters[opponent]
                # cluster size dominance
                if len(cluster) < len(opponent_cluster):
                    num_blue_dominates += 1
                elif len(cluster) > len(opponent_cluster):
                    num_red_dominates += 1
                # cluster power dominance
                if cluster.get_power() < opponent_cluster.get_power():
                    size_blue_dominates += 1
                elif cluster.get_power() > opponent_cluster.get_power():
                    size_red_dominates += 1

        # cluster and dominance factor add-on, respectively
        value += sign * len(cluster) * SIZE_CLUSTER_FACTOR
        value += (num_red_dominates  - num_blue_dominates)  * SIZE_DOMINANCE_FACTOR
        value += (size_red_dominates - size_blue_dominates) * POWER_DOMINANCE_FACTOR
    value += (num_red_clusters - num_blue_clusters) * NUM_CLUSTER_FACTOR
    return value

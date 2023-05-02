from .cluster import create_clusters
from referee.game import PlayerColor
from .board import Board, PLAYER_COLOR

CLUSTER_SIZE_FACTOR : float = 1.4
NUM_CLUSTER_FACTOR  : float = 1.2
PIECE_POWER_FACTOR  : float = 3.0
DOMINANCE_FACTOR    : float = 1.5


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
    red_dominates     = 0
    blue_dominates    = 0
    num_red_clusters  = 0
    num_blue_clusters = 0
    for cluster in clusters.values():
        if cluster.color == PlayerColor.RED:
            sign = 1
            num_red_clusters += 1
        else:
            sign = -1
            num_blue_clusters += 1

        # dominance factor is checked solely via player pieces
        if cluster.color == PLAYER_COLOR:
            for opponent_len in cluster.get_opponents():
                # so far, dominance factor is entirely dictated by number of pieces, not their power
                if len(cluster) < opponent_len:
                    blue_dominates += 1
                elif len(cluster) > opponent_len:
                    red_dominates += 1

        # cluster and dominance factor add-on, respectively
        value += sign * len(cluster) * CLUSTER_SIZE_FACTOR
        value += (red_dominates - blue_dominates) * DOMINANCE_FACTOR
    value += (num_red_clusters - num_blue_clusters) * NUM_CLUSTER_FACTOR
    return value

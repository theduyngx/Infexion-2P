from referee.game import PlayerColor
from .board import Board


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # for now let's only consider number of pieces and power values
    num_blue = board.num_players(PlayerColor.BLUE)
    pow_blue = board.color_power(PlayerColor.BLUE)
    num_red  = board.num_players(PlayerColor.RED)
    pow_red  = board.color_power(PlayerColor.RED)
    value = num_red + pow_red - num_blue - pow_blue
    return value


def cluster_evaluation(board: Board) -> float:
    # A possible way to separate clusters:
    """
    for each occupied_cell on board:
        in_cluster = false
        for cluster in clusters:
            if occupied_cell in cluster:
                if in_cluster == true:
                    clusters.join_cluster(occupied_cell.prev_cluster, cluster)
                    occupied_cell.prev_cluster = joint_cluster
                else:
                    cluster.append(occupied_cell)
                    occupied_cell.prev_cluster = cluster
                    in_cluster = true
        cluster = [occupied_cell]
        clusters.append(cluster)
    """
    return 0

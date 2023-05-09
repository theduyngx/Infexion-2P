"""
Module:
    ``evaluation_data.py``

Purpose:
    Includes the representation and function to obtain all the information that is required
    to evaluate the state of the board.

Notes:
    The evaluation information includes the number of pieces of a both sides, their total power,
    and their clusters. The information on clusters will be used for dominance factor data. This
    is especially significant since much of Infexion is about dominating the blue.
    With the provided constants, the evaluation score of the board is calculated as follows:

    |
    .. math:: Eval(state) = 2.0  * (Num_r    - Num_b   ) +
                            1.6  * (Pow_r    - Pow_b   ) + \n
                            0.8  * (NumCl_r  - NumCl_b ) +
                            1.55 * (NumDom_r - NumDom_b) + \n
                            0.65 * (PowDom_r - PowDom_b)

    Where: (each of a specified color)
        * Num is the number of pieces
        * Pow is the total power
        * NumCl is the number of clusters
        * NumDom is the number of dominating clusters by size
        * PowDom is the power of clusters that dominate
"""

from dataclasses import dataclass

from referee.game import PlayerColor
from ..game import Board, INF, create_clusters

# weighting factors
NUM_PIECE_FACTOR     : float = 2.0
POW_PIECE_FACTOR     : float = 1.6
NUM_CLUSTER_FACTOR   : float = 0.8
NUM_DOMINANCE_FACTOR : float = 1.55
POW_DOMINANCE_FACTOR : float = 0.65


@dataclass(slots=True)
class EvaluateData:
    """
    Class represents the information required for evaluating the board.
    Attributes:
        num_red            : the number of red pieces on the board
        pow_red            : the red's total power
        num_red_clusters   : the number of red's clusters
        num_red_dominates  : the number of clusters where red dominates blue
        pow_red_dominates  : the power of clusters where red dominates blue

        num_blue           : the number of blue pieces on the board
        pow_blue           : the blue's total power
        num_blue_clusters  : the number of blue's clusters
        num_blue_dominates : the number of clusters where blue dominates red
        pow_blue_dominates : the power of clusters where blue dominates red

        immediate_eval     : immediate evaluation value where the game is already over
        immediate          : whether value is immediately evaluated or not
    """
    num_red            : int = 0
    pow_red            : int = 0
    num_red_clusters   : int = 0
    num_red_dominates  : int = 0
    pow_red_dominates  : int = 0

    num_blue           : int = 0
    pow_blue           : int = 0
    num_blue_clusters  : int = 0
    num_blue_dominates : int = 0
    pow_blue_dominates : int = 0

    immediate_eval     : int = 0
    immediate          : bool = False


def get_evaluate_data(board: Board) -> EvaluateData:
    """
    Get the data required for board evaluation.

    Args:
        board: current state of board
    Returns:
        the object containing all data relevant to evaluating a board's state
    """
    # number of pieces and total power evaluation data
    data = EvaluateData()
    num_red , pow_red  = board.color_number_and_power(PlayerColor.RED)
    num_blue, pow_blue = board.color_number_and_power(PlayerColor.BLUE)
    data.num_red       = num_red
    data.pow_red       = pow_red
    data.num_blue      = num_blue
    data.pow_blue      = pow_blue

    # immediate evaluation data
    if num_red == 0:
        data.immediate_eval = -INF
        data.immediate = True
        return data
    elif num_blue == 0:
        data.immediate_eval = INF
        data.immediate = True
        return data

    # clusters and dominance evaluation data
    clusters = create_clusters(board, PlayerColor.RED)
    for cluster in clusters:

        # red's cluster
        if cluster.color == PlayerColor.RED:
            data.num_red_clusters  += 1
            # dominance factor is checked solely via red pieces
            for adj_opponent in cluster.get_opponents():
                blue_cluster = clusters[adj_opponent]

                # cluster size dominance
                if len(cluster) < len(blue_cluster):
                    data.num_blue_dominates += 1
                elif len(cluster) > len(blue_cluster):
                    data.num_red_dominates += 1

                # cluster power dominance
                if cluster.get_power() < blue_cluster.get_power():
                    data.pow_blue_dominates += 1
                elif cluster.get_power() > blue_cluster.get_power():
                    data.pow_red_dominates += 1

        # blue's cluster
        else:
            data.num_blue_clusters  += 1
    return data

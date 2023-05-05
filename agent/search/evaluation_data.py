"""
    Module  : evaluation_data.py
    Purpose : Includes the representation and function to obtain all the information that is
              required to evaluate the state of the board.

The evaluation information includes the number of pieces of a both sides, their total power,
and their clusters. The information on clusters will be used for dominance factor data. This
is especially significant since much of Infexion is about dominating the opponent.
"""
from dataclasses import dataclass

from referee.game import PlayerColor
from ..game import Board, PLAYER_COLOR, INF, create_clusters

# weighting factors
NUM_PIECE_FACTOR     : float = 1.8
POW_PIECE_FACTOR     : float = 1.7
NUM_CLUSTER_FACTOR   : float = 1.2
SIZE_CLUSTER_FACTOR  : float = 1.4
NUM_DOMINANCE_FACTOR : float = 1.55
POW_DOMINANCE_FACTOR : float = 0.45


@dataclass(slots=True)
class EvaluateData:
    """
    Class represents the information required for evaluating the board.
    Attributes:
        num_player             : the number of player pieces on the board
        pow_player             : the player's total power
        num_player_clusters    : the number of player's clusters
        num_player_dominates   : the number of clusters where player dominates opponent
        pow_player_dominates   : the power of clusters where player dominates opponent
        size_player_clusters   : the size of player's clusters

        num_opponent           : the number of opponent pieces on the board
        pow_opponent           : the opponent's total power
        num_opponent_clusters  : the number of opponent's clusters
        num_opponent_dominates : the number of clusters where opponent dominates player
        pow_opponent_dominates : the power of clusters where opponent dominates player
        size_opponent_clusters : the size of player's clusters

        immediate_evaluation   : immediate evaluation value where the game is already over
        immediate              : whether value is immediately evaluated or not
        sign                   : multiplier sign, if player is red then maximize by multiplying 1,
                                 otherwise minimize by multiplying -1; only applicable for zero-sum
    """
    num_player             : int = 0
    pow_player             : int = 0
    num_player_clusters    : int = 0
    num_player_dominates   : int = 0
    pow_player_dominates   : int = 0
    size_player_clusters   : int = 0

    num_opponent           : int = 0
    pow_opponent           : int = 0
    num_opponent_clusters  : int = 0
    num_opponent_dominates : int = 0
    pow_opponent_dominates : int = 0
    size_opponent_clusters : int = 0

    immediate_evaluation   : int = 0
    immediate              : bool = False
    sign                   : int = 1


def get_evaluate_data(board: Board) -> EvaluateData:
    """
    Get the data required for board evaluation.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # number of pieces and total power evaluation data
    sign      = 1 if PLAYER_COLOR == PlayerColor.RED else -1
    data      = EvaluateData()
    data.sign = sign
    num_player, pow_player     = board.color_number_and_power(PLAYER_COLOR)
    num_opponent, pow_opponent = board.color_number_and_power(PLAYER_COLOR.opponent)
    data.num_player            = num_player
    data.pow_player            = pow_player
    data.num_opponent          = num_opponent
    data.pow_opponent          = pow_opponent

    # immediate evaluation data
    if num_player == 0:
        data.immediate_evaluation = -INF * sign
        data.immediate = True
        return data
    elif num_opponent == 0:
        data.immediate_evaluation = INF * sign
        data.immediate = True
        return data

    # clusters and dominance evaluation data
    clusters = create_clusters(board)
    for cluster in clusters.values():

        # player's cluster
        if cluster.color == PLAYER_COLOR:
            data.num_player_clusters  += 1
            data.size_player_clusters += len(cluster)
            # dominance factor is checked solely via player pieces
            for opponent in cluster.get_opponents():
                opponent_cluster = clusters[opponent]

                # cluster size dominance
                if len(cluster) < len(opponent_cluster):
                    data.num_opponent_dominates += 1
                elif len(cluster) > len(opponent_cluster):
                    data.num_player_dominates += 1

                # cluster power dominance
                if cluster.get_power() < opponent_cluster.get_power():
                    data.pow_opponent_dominates += 1
                elif cluster.get_power() > opponent_cluster.get_power():
                    data.pow_player_dominates += 1

        # opponent's cluster
        else:
            data.num_opponent_clusters  += 1
            data.size_opponent_clusters += len(cluster)
    return data

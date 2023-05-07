"""
Module:
    ``evaluation.py``

Purpose:
    NegaScout and Negamax search algorithm evaluation function.

Notes:
    The evaluation function for NegaScout and Negamax is a **zero-sum** evaluation function.
    We make RED as the maximizing side, and BLUE as the minimizing side.
    Used in both ``negascout.py``.
"""

from ...search.evaluation_data import *

# Constants
MAXIMIZE_PLAYER: PlayerColor = PlayerColor.RED


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the
    more 'negative' the evaluated value, the worse it is for the RED player and, conversely,
    the better it is for the BLUE player.

    In other words, it is a zero-sum evaluation function, suitably applied to the zero-sum
    Infexion game. And because of this, it also allows Negamax to make use of.

    Args:
        board: current state of board

    Returns:
        the evaluated value of the board
    """
    data: EvaluateData = get_evaluate_data(board)
    if data.immediate:
        return data.immediate_eval
    value  = (data.num_red - data.num_blue) * NUM_PIECE_FACTOR
    value += (data.pow_red - data.pow_blue) * POW_PIECE_FACTOR
    value += (data.num_red_clusters  - data.num_blue_clusters ) * NUM_CLUSTER_FACTOR
    value += (data.size_red_clusters - data.size_blue_clusters) * SIZE_CLUSTER_FACTOR
    value += (data.num_red_dominates - data.num_blue_dominates) * NUM_DOMINANCE_FACTOR
    value += (data.pow_red_dominates - data.pow_blue_dominates) * POW_DOMINANCE_FACTOR
    return value

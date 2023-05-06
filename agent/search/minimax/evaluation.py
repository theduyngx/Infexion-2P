"""
Module:
    ``evaluation.py``

Purpose:
    Minimax search algorithm evaluation function.

Notes:
    The evaluation function for Minimax is a **zero-sum** evaluation function. We make RED as the
    maximizing side, and BLUE as the minimizing side. It should be noted that the evaluation
    is dynamic, meaning if the player is BLUE, it will know to minimize the score.
"""

from ...search.evaluation_data import *


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the
    more 'negative' the evaluated value, the worse it is for the RED player and, conversely,
    the better it is for the BLUE player. In other words, it is a zero-sum evaluation function,
    suitably applied to the zero-sum Infexion game.

    Parameters
    ----------
    board: Board
        current state of board

    Returns
    -------
    float
        the evaluated value of the board
    """
    data: EvaluateData = get_evaluate_data(board)
    if data.immediate:
        return data.immediate_evaluation
    value  = (data.num_player - data.num_opponent) * NUM_PIECE_FACTOR
    value += (data.pow_player - data.pow_opponent) * POW_PIECE_FACTOR
    value += (data.size_player_clusters - data.size_opponent_clusters) * SIZE_CLUSTER_FACTOR
    value += (data.num_player_dominates - data.num_opponent_dominates) * NUM_DOMINANCE_FACTOR
    value += (data.pow_player_dominates - data.pow_opponent_dominates) * POW_DOMINANCE_FACTOR
    value += (data.num_player_clusters  - data.num_opponent_clusters ) * NUM_CLUSTER_FACTOR
    value *= data.sign
    return value

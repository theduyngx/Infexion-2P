"""
Module:
    ``evaluation.py``

Purpose:
    Monte Carlo Tree search evaluation function.

Notes:
    The evaluation function for MCTS will partially act as the simulation function, where play-outs
    will not go to terminal node, and instead for a fixed number of moves before it evaluates. This
    evaluation function is also not zero-sum, unlike Minimax's. Instead, it is normalized in range
    ``[0, 1]`` such that any value in between represents the desirability for a specific player, and
    that 0 means definite loss, and 1 means definite win.
"""

from ...search.evaluation_data import *


def mc_evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the state of the board after a monte carlo simulation. This
    is not a zero-sum evaluation function, but an evaluation function for the simulation. The
    evaluation is normalized, meaning if it is a win for the player, it will be 1, and if it is
    definite loss then it will be 0. Any value in between shows the desirability of the state.

    Args:
        board: current state of board

    Returns:
        the evaluated value of the board
    """
    data: EvaluateData = get_evaluate_data(board)
    if data.immediate:
        if board.true_turn == PlayerColor.RED:
            return 0 if data.immediate_eval < 0 else 1
        else:
            return 1 if data.immediate_eval < 0 else 0

    # adding another return value specifically for ordering the heapq for MonteCarlo
    red_val  = data.num_red_clusters   * NUM_CLUSTER_FACTOR   + \
               data.size_red_clusters  * SIZE_CLUSTER_FACTOR  + \
               data.num_red_dominates  * NUM_DOMINANCE_FACTOR + \
               data.pow_red_dominates  * POW_DOMINANCE_FACTOR
    blue_val = data.num_blue_clusters  * NUM_CLUSTER_FACTOR   + \
               data.size_blue_clusters * SIZE_CLUSTER_FACTOR  + \
               data.num_blue_dominates * NUM_DOMINANCE_FACTOR + \
               data.pow_blue_dominates * POW_DOMINANCE_FACTOR
    if board.true_turn == PlayerColor.RED:
        player_val = red_val
        opponent_val = blue_val
    else:
        player_val = blue_val
        opponent_val = red_val
    return player_val / (player_val + opponent_val)

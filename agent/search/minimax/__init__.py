"""
Package:
    ``minimax``

Purpose:
    Provide the Minimax search algorithm function to find the next move for agent.

Notes:
    Move ordering, which is an alpha-beta pruning optimization method, is also included to be shared
    with Monte Carlo Tree search algorithm.
"""

from .minimax_utils import move_ordering
from .minimax import minimax
from .negamax import negamax

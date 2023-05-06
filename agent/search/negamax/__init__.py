"""
Package:
    ``negamax``

Purpose:
    Provide the Negamax search algorithm function to find the next move for agent.

Notes:
    Move ordering, which is an alpha-beta pruning optimization method, is also included to be shared
    with Monte Carlo Tree search algorithm.
"""

from .negamax_utils import move_ordering
from .negamax import negamax
from .minimax import minimax

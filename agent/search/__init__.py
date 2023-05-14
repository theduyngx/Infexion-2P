"""
Package:
    ``agent.search``

Authors:
    The Duy Nguyen (1100548) and Ramon Javier L. Felipe VI (1233281)

Purpose:
    Search package providing algorithms to find the next best move for agent.

Notes:
    Search is bundled with a variety of testing agents, as well as a main agent utilizing the Minimax
    and alpha-beta pruning algorithms. There are also various important evaluation aspects of the board
    that the package also provides.
"""

from .search import search
from .search_utils import get_legal_moves
from .evaluation_data import *
from .agent_test import *

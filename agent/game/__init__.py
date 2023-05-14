"""
Package:
    ``agent.game``

Authors:
    The Duy Nguyen (1100548)

Purpose:
    Providing objects and functionalities directly related to the game, namely including board
    and clusters.

Notes:
    The board representation is highly optimized in terms of time and space complexity. It is
    based onn COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B referee's board
    representation.

    The clusters are another important aspect of the game, where it determines the dominance
    factor of a specific agent.
"""

from .board import Board, CellState
from .cluster import create_clusters, create_clusters_color, Clusters
from .game_utils import *
from .constants import *

"""
Package:
    ``agent``

Authors:
    The Duy Nguyen (1100548) and Ramon Javier L. Felipe VI (1233281)

Purpose:
    The Infexion game-playing agent.

Notes:
    The main agent uses Minimax (with alpha-beta pruning and a variety of other optimization methods)
    to find its next move.
    Package for COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent.
"""

from .program import Agent, RandomAgent, GreedyAgent,\
                     MinimaxShallowAgent, MonteCarloAgent, NegaScoutAgent

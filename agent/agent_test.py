"""
    Module  : agent_test.py
    Purpose : Includes all testing agent for the current agent to play against.

These agents range from simply picking a move randomly that's legal for them, to a greedy approach,
to more complex agents that are capable of making more complex moves.
"""

from random import randint

from agent.board import Board
from agent.search_utils import get_legal_moves
from referee.game import Action, PlayerColor, SpawnAction, SpreadAction


def random_move(board: Board, color: PlayerColor) -> Action:
    """
    Agent's move approach where it picks any random move from all of its possible move set.
    @param board : the current state of the board
    @param color : the agent's color (it is its turn)
    @return      : the random action to be taken by agent
    """
    actions: list[Action] = get_legal_moves(board, color)
    random_index: int = randint(0, len(actions)-1)
    return actions[random_index]


def greedy_move(board: Board, color: PlayerColor) -> Action:
    """
    Agent's move approach using greedy algorithm. The agent will look for which spread move gives
    it the most power, and if all spread moves lead to no power decrease of opponent, it will
    randomly spawn if possible, otherwise randomly spread.
    @param board : the board
    @param color : the agent's color turn
    @return      : the action to be taken by agent
    """
    actions: list[Action] = get_legal_moves(board, color)
    spawns : list[Action] = []
    min_opponent_power = board.color_power(color.opponent)
    greedy_action = None

    # for each legal action, find spread that reduces the most power from opponent
    for action in actions:
        match action:
            case SpawnAction(_):
                spawns.append(action)
            case SpreadAction(_, _):
                board.apply_action(action, concrete=False)
                curr_power = board.color_power(color.opponent)
                if curr_power < min_opponent_power:
                    min_opponent_power = curr_power
                    greedy_action = action
                board.undo_action()
            case _:
                raise Exception()

    # if no such action found, prioritize spawn randomly, then choose any other random action
    if greedy_action is None:
        return spawns[randint(0, len(spawns)-1)] if spawns else actions[randint(0, len(actions)-1)]
    return greedy_action

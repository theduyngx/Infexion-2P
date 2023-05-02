from referee.game import PlayerColor, Action
from .board import Board
from .evaluation import evaluate, create_clusters


# Constants
INF   : float = 9999
DEPTH : int   = 2


def minimax(board: Board, color: PlayerColor) -> Action:
    """
    Minimax search algorithm to find the next action to take for the agent. It is called when it
    is the agent with specified color's turn.

    NOTE: the behavior so far is like this: for whatever reason, our player insists NOT to use
    spread action for pieces with any power level above 1. It seems like there's a faulty feature
    in evaluation where power of a piece is too valued.
    @param board : the board
    @param color : the agent's color
    @return      : the action to take for agent
    """
    alpha = -INF
    beta  = INF

    ###
    # moves = board.get_legal_moves(PlayerColor.RED)
    # print("Number of legal moves =", len(moves))
    # for move in moves:
    #     print(move)
    ###

    _, action = alphabeta(board, color, DEPTH, None, alpha, beta)

    ###
    # clusters = create_clusters(board)
    # print()
    # print("===================================")
    # print("Number of clusters =", len(clusters))
    # for cluster in clusters.values():
    #     print("Cluster color", cluster.color)
    #     print("Cluster size =", len(cluster))
    #     print()
    # print("===================================")
    ###

    return action


def alphabeta(board  : Board,
              color  : PlayerColor,
              depth  : int,
              action : Action,
              alpha  : float,
              beta   : float
              ) -> (float, Action):
    """
    Alpha-beta pruning for minimax search algorithm.
    @param board  : the board
    @param color  : the current turn of player, specified by player's color
    @param depth  : the current depth in the search tree
    @param action : deduced best action
    @param alpha  : alpha - move that improves player's position
    @param beta   : beta  - move that improves opponent's position
    @return       : evaluated score of the board and the action to be made
    """

    # reached depth limit, or terminal node
    if depth == 0 or board.game_over:
        return evaluate(board), action

    # maximize
    if color == PlayerColor.RED:
        value = -INF
        ret   = None
        legal_moves = board.get_legal_moves(color)
        # for each child node of board
        for possible_action in legal_moves:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _ = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta)

            # undo after finishing
            board.undo_action()
            if curr_val > value:
                value = curr_val
                ret   = possible_action
            alpha = max(alpha, value)

            # beta cutoff
            if value >= beta:
                break

    # minimize
    else:
        value = INF
        ret   = None
        legal_moves = board.get_legal_moves(color)
        # for each child node of board
        for possible_action in legal_moves:

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _ = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta)

            # undo action after finishing
            board.undo_action()
            if curr_val < value:
                value = curr_val
                ret   = possible_action
            # NOTE: relying on reference based to have the argument changed
            # Must make sure that the argument is actually updated properly
            beta = min(beta, value)

            # alpha cutoff
            if value <= alpha:
                break

    # return evaluated value and corresponding action
    return value, ret

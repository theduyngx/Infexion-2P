# evaluation function
from referee.game import PlayerColor, Action, SpawnAction, SpreadAction, HexDir
from .board import Board, CellState

INF   : float = 9999
DEPTH : int   = 4


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # for now let's only consider number of pieces and power values
    num_blue = board.num_players(PlayerColor.BLUE)
    pow_blue = board.color_power(PlayerColor.BLUE)
    num_red  = board.num_players(PlayerColor.RED)
    pow_red  = board.color_power(PlayerColor.RED)
    value = num_red + pow_red - num_blue - pow_blue
    return value


def minimax(board: Board, color: PlayerColor) -> Action:
    alpha = -INF
    beta  = INF

    ### DEBUG
    before = board.get_state_copy()
    ###

    _, action = alphabeta(board, color, DEPTH, None, alpha, beta)

    ### DEBUG
    after = board.get_state_copy()
    assert before == after
    assert board.non_concrete_history_empty()
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
        # for each child node of board
        for possible_action in get_child_nodes(board, color):

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
        return value, ret

    # minimize
    else:
        value = INF
        ret   = None
        # for each child node of board
        for possible_action in get_child_nodes(board, color):

            # apply action
            board.apply_action(possible_action, concrete=False)
            curr_val, _ = alphabeta(board, color.opponent, depth-1, possible_action, alpha, beta)

            # undo action after finishing
            board.undo_action()
            if curr_val < value:
                value = curr_val
                ret   = possible_action
            beta = min(beta, value)

            # alpha cutoff
            if value <= alpha:
                break
        return value, ret


def get_child_nodes(board: Board, color: PlayerColor) -> list[Action]:
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: list[Action] = []
    movable_dict: list[CellState] = board.player_movable_cells(color)
    for state in movable_dict:
        # append spawn actions
        pos = state.pos
        if board.empty_cell(pos):
            actions.append(SpawnAction(pos))
        # append spread actions for each direction
        else:
            actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    return actions

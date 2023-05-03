from agent.board import Board
from agent.constants import MIN_TOTAL_POWER
from referee.game import HexPos, HexDir, PlayerColor, Action, SpawnAction, MAX_TOTAL_POWER, SpreadAction


def adjacent_positions(pos: HexPos) -> list[HexPos]:
    """
    Get all adjacent positions to the specified one.
    @param pos : the specified position
    @return    : list of 6 of its adjacent positions
    """
    return [pos + dir for dir in HexDir]


def get_legal_moves(board: Board, color: PlayerColor, full=True) -> list[Action]:
    """
    Get all possible legal moves of a specified player color from a specific state of the board.
    @param board:
    @param color : specified player's color
    @param full  : to get the full list of legal moves if true, or reduced list if otherwise
    @return      : list of all actions that could be applied to board
    """
    # for every possible move from a given board state, including SPAWN and SPREAD
    actions: list[Action] = []
    player_power   = board.color_power(color)
    opponent_power = board.color_power(color.opponent)
    for cell in board.get_cells():

        # append spawn actions - if full then always append (if power < 49), otherwise append on condition
        pos = cell.pos
        if not board.pos_occupied(pos):
            if board.total_power() < MAX_TOTAL_POWER:
                if full:
                    actions.append(SpawnAction(pos))

                # append on condition: board power < 10, player power >= opponent's, has adjacent pieces
                elif board.total_power() < MIN_TOTAL_POWER and player_power >= opponent_power:
                    adj_list = adjacent_positions(pos)
                    # and that if only the spawn action is not quiet - viz. has adjacent piece
                    if any([board.pos_occupied(adj) for adj in adj_list]):
                        actions.append(SpawnAction(pos))

        # append spread actions for every direction
        elif board[pos].color == color:

            # add if total power exceeds acceptable limit for reduction, and that spread is non-quiet
            if not full and board[pos].power == 1 and board.total_power() > MIN_TOTAL_POWER:
                for dir in HexDir:
                    adj = pos + dir
                    if board.pos_occupied(adj):
                        actions.append(SpreadAction(pos, dir))
            # otherwise, full list requested, or position has power exceeding 1
            else:
                actions.extend([SpreadAction(pos, dir) for dir in HexDir])
    return actions

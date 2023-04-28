from collections import defaultdict, deque

from referee.game import PlayerColor
from .board import Board, adjacent_positions, CellState, EMPTY_POWER


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


def cluster_evaluation(board: Board) -> float:
    # A possible way to separate clusters:
    """
    ALGORITHM -> O(nm):

    for each occupied_cell on board:
        in_cluster: dict = {}
        for each adjacent_cell of occupied_cell:
            for each cluster in clusters:
                if cluster[adjacent_cell] exists and of same color:
                    create cluster[occupied_cell]
                    in_cluster |= cluster
                    del cluster in clusters  // delete by reference
            if in_cluster == {}:
                create in_cluster[occupied_cell]
            clusters.append(in_cluster)

    It can still be improved, in that cells that already have entries within specific clusters may not
    have to be reconsidered. Although this can be flimsy and ultimately not that much of an improvement.
    """

    # There is a trade-off in speed and space here: space-wise suggests storing, incongruously enough, the entire
    # board in full instead of sparse representation where unoccupied cells are not to be considered.
    # This is because not storing in full won't allow undo_action, which is incredibly powerful since it lets
    # us to not have to create a new state at every node generation.

    state = board.__getstate__()
    clusters = deque([])

    # for each cell in state
    for cell in state.values():
        # skip empty cells
        if cell.power == EMPTY_POWER:
            continue

        # everything related to current occupied position
        pos = cell.pos
        player = cell.player
        pos_hash = pos.__hash__()
        in_cluster = defaultdict()
        adjacent = adjacent_positions(pos)

        # for each adjacent cell
        for adj_pos in adjacent:
            adj_hash = adj_pos.__hash__()
            for i in range(len(clusters)):
                cluster = clusters[i]
                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_hash in cluster and cluster[adj_hash].player == player:
                    cluster[pos_hash] = CellState(pos, cell.power, player)
                    in_cluster |= cluster
                    del clusters[i]
            if not in_cluster:
                in_cluster[pos_hash] = CellState(pos, cell.power, player)
            clusters.append(in_cluster)
    return 0

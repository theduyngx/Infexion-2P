from collections import defaultdict
from dataclasses import dataclass

from referee.game import PlayerColor, HexPos
from .board import Board, adjacent_positions, CellState, EMPTY_POWER


CLUSTER_SIZE_POWER: float = 1.4
NUM_CLUSTER_POWER : float = 1.1


@dataclass(slots=True)
class Cluster:
    """
    Class represents a cluster, which is a connected region of pieces of the same color on
    the board. When creating a cluster, it must be initialized with a proper cell, including
    its position on the board and its state.

    The initial cell is important because it dictates the hash value of the cluster, which
    can be used for quick accessing itself in a consistent and efficient manner.

    Attributes:
        init_pos   : the initial cell's position
        init_state : the initial cell's state
        color      : the color of the cluster
        cells      : all cells that are within the cluster, initialized with the initial cell
    """
    init_pos   : HexPos
    init_state : CellState
    color      : PlayerColor
    cells      : dict[int, CellState] = defaultdict

    def __init__(self, init_pos: HexPos, init_state: CellState):
        """
        Cluster constructor. Requires the information of the initial cell.
        @param init_pos   : initial cell's position
        @param init_state : initial cell's state
        """
        self.init_pos = init_pos
        self.init_state = init_state
        self.color = init_state.player
        self.cells = defaultdict()

    def __post_init__(self):
        """
        Post initialization, in this case includes cells mutation, as it adds the initial cell.
        """
        self.cells[self.init_pos.__hash__()] = self.init_state

    def __getitem__(self, pos: HexPos) -> CellState:
        """
        Accessing a cell via its position quickly within a cluster.
        @param pos : cell's position
        @return    : cell's state
        """
        return self.cells[pos.__hash__()]

    def __contains__(self, pos: HexPos) -> bool:
        """
        Check whether a cluster contains a cell with specified position or not.
        @param pos : specified position
        @return    : boolean denoting whether cluster contains cell with position
        """
        return pos.__hash__() in self.cells

    def reference_append(self, other):
        """
        Appending the cells of this object with another cluster's cells, but via reference.
        This means the operation is in constant time in both time and space.
        @param other : the other cluster
        """
        if type(other) == Cluster:
            self.cells |= other.cells

    def singular(self) -> bool:
        """
        Checks whether the cluster has only a single cell.
        @return: true if cluster has only a single cell, and false if otherwise
        """
        return len(self.cells) <= 1

    def __hash__(self):
        """
        Special hash function where it uses its initial cell as the hash value.
        @return: the hash value
        """
        return self.init_pos.__hash__()


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.
    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # number of pieces and power values
    num_blue = board.num_players(PlayerColor.BLUE)
    pow_blue = board.color_power(PlayerColor.BLUE)
    num_red  = board.num_players(PlayerColor.RED)
    pow_red  = board.color_power(PlayerColor.RED)
    value = num_red + pow_red - num_blue - pow_blue

    # clusters evaluation
    clusters = create_clusters(board)
    num_red_clusters  = 0
    num_blue_clusters = 0
    for cluster in clusters.values():
        if cluster.color == PlayerColor.RED:
            sign = 1
            num_red_clusters += 1
        else:
            sign = -1
            num_blue_clusters += 1
        value += sign * (len(cluster.cells) ** CLUSTER_SIZE_POWER)
    value += (num_red_clusters ** NUM_CLUSTER_POWER - num_blue_clusters ** NUM_CLUSTER_POWER)

    # domination evaluation
    # ...

    return value


def create_clusters(board: Board) -> dict[int, Cluster]:
    """
    Create a dictionary of clusters currently on the board, where the key is each cluster's hash.
    @param board : the given board
    @return      : dictionary of clusters
    """
    state = board.__getstate__()
    clusters: dict[int, Cluster] = defaultdict()

    # for each cell in state
    for cell in state.values():
        # skip empty cells
        if cell.power == EMPTY_POWER:
            continue

        # everything related to current occupied position
        pos        = cell.pos
        player     = cell.player
        adjacent   = adjacent_positions(pos)
        in_cluster = Cluster(pos, CellState(pos, player, cell.power))

        # for each adjacent cell
        for adj_pos in adjacent:
            for cluster in clusters.values():

                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_pos in cluster and cluster[adj_pos].player == player:
                    in_cluster.reference_append(cluster)
                    del clusters[cluster.__hash__()]

            # add the cluster with added position, whatever it may be
            clusters[in_cluster.__hash__()] = in_cluster
    return clusters

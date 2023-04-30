from collections import defaultdict
from dataclasses import dataclass
from referee.game import PlayerColor, HexPos
from .board import Board, adjacent_positions, CellState, PLAYER_COLOR, OPPONENT_COLOR

PIECE_POWER_FACTOR  : float = 1.5
DOMINANCE_FACTOR    : float = 1.4
CLUSTER_SIZE_FACTOR : float = 1.3
NUM_CLUSTER_FACTOR  : float = 1.1


def evaluate(board: Board) -> float:
    """
    Evaluation function to evaluate the desirability of the board. It should be noted that the more
    'negative' the evaluated value, the worse it is for the RED player and, conversely, the better
    it is for the BLUE player.

    NOTE:
    Possible heuristic improvements: bounded-ness
    -   If we know for certain the upper/lower bound of the heuristic, not necessarily in a standardized
        [0, 1] way but a more context-driven way, then we can significantly speed up evaluation process.
    -   i.e. We know evaluation can not exceed 49000 (just an example) because of how the game works and
             how we evaluate the scores (given that we've come to it in a proper manner). Then we can
             cut off branches more efficiently and evaluate more accurately.

    @param board : current state of board
    @return      : the evaluated value of the board
    """
    # player power evaluation
    pow_blue = board.color_power(PlayerColor.BLUE)
    pow_red  = board.color_power(PlayerColor.RED)
    value = pow_red  ** PIECE_POWER_FACTOR - pow_blue ** PIECE_POWER_FACTOR

    # clusters and dominance evaluation
    clusters = create_clusters(board)
    red_dominates     = 0
    blue_dominates    = 0
    num_red_clusters  = 0
    num_blue_clusters = 0
    for cluster in clusters.values():
        if cluster.color == PlayerColor.RED:
            sign = 1
            num_red_clusters += 1
        else:
            sign = -1
            num_blue_clusters += 1

        # dominance factor is checked solely via player pieces
        if cluster.color == PLAYER_COLOR:
            for opponent_len in cluster.get_opponents():
                print(opponent_len)
                if len(cluster) < opponent_len:
                    blue_dominates += 1
                elif len(cluster) > opponent_len:
                    red_dominates += 1

        # cluster and dominance factor add-on, respectively
        value += sign * (len(cluster) ** CLUSTER_SIZE_FACTOR)
        value += (red_dominates ** DOMINANCE_FACTOR - blue_dominates ** DOMINANCE_FACTOR)
    value += (num_red_clusters ** NUM_CLUSTER_FACTOR - num_blue_clusters ** NUM_CLUSTER_FACTOR)

    return value


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
        opponents  : dictionary of adjacent opponent clusters, with key being the cluster itself and value
                     being its number of cells
    """
    init_pos   : HexPos
    init_state : CellState
    color      : PlayerColor
    cells      : dict[int, CellState] = defaultdict
    opponents  : dict[int, int] = defaultdict

    def __init__(self, init_pos: HexPos, init_state: CellState):
        """
        Cluster constructor. Requires the information of the initial cell.
        @param init_pos   : initial cell's position
        @param init_state : initial cell's state
        """
        self.init_pos   = init_pos
        self.init_state = init_state
        self.color      = init_state.player
        self.cells      = defaultdict()
        self.opponents  = defaultdict()

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

    def get_opponents(self):
        assert self.color == PLAYER_COLOR
        return self.opponents.values()

    def __contains__(self, pos: HexPos) -> bool:
        """
        Check whether a cluster contains a cell with specified position or not.
        @param pos : specified position
        @return    : boolean denoting whether cluster contains cell with position
        """
        return pos.__hash__() in self.cells

    def __len__(self) -> int:
        """
        The length of the cluster is defined as the number of cells that the cluster contains.
        @return: the number of cells that cluster contains
        """
        return len(self.cells)

    def reference_append(self, other):
        """
        Appending the cells of this object with another cluster's cells, but via reference.
        This means the operation is in constant time in both time and space.
        @param other : the other cluster
        """
        if type(other) == Cluster:
            self.cells |= other.cells

    def opponent_update(self, other):
        """
        Update adjacent opponent cluster number of cells. If opponent cluster is not yet recorded, then
        a new entry for it will be added.
        @param other : the adjacent opponent cluster
        """
        if type(other) == Cluster:
            if self.color != other.color:
                self.opponents[other.__hash__()] = len(other)

    def singular(self) -> bool:
        """
        Checks whether the cluster has only a single cell.
        @return: true if cluster has only a single cell, and false if otherwise
        """
        return len(self) <= 1

    def __hash__(self):
        """
        Special hash function where it uses its initial cell as the hash value.
        @return: the hash value
        """
        return self.init_pos.__hash__()


def create_clusters(board: Board) -> dict[int, Cluster]:
    """
    Create a dictionary of clusters currently on the board, where the key is each cluster's hash.
    @param board : the given board
    @return      : dictionary of clusters
    """
    clusters: dict[int, Cluster] = defaultdict()

    # for each opponent cell in state
    for cell in board.player_cells(OPPONENT_COLOR):
        # everything related to current occupied position
        pos        = cell.pos
        adjacent   = adjacent_positions(pos)
        in_cluster = Cluster(pos, CellState(pos, OPPONENT_COLOR, cell.power))

        # for each adjacent cell
        for adj_pos in adjacent:
            for cluster in clusters.values():

                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_pos in cluster:
                    if cluster[adj_pos].player == OPPONENT_COLOR:
                        in_cluster.reference_append(cluster)
                        del clusters[cluster.__hash__()]

            # add the cluster with added position, whatever it may be
            clusters[in_cluster.__hash__()] = in_cluster

    # for each player cell in state
    for cell in board.player_cells(PLAYER_COLOR):
        # everything related to current occupied position
        pos        = cell.pos
        adjacent   = adjacent_positions(pos)
        in_cluster = Cluster(pos, CellState(pos, PLAYER_COLOR, cell.power))

        # for each adjacent cell
        for adj_pos in adjacent:
            for cluster in clusters.values():

                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_pos in cluster:
                    if cluster[adj_pos].player == PLAYER_COLOR:
                        in_cluster.reference_append(cluster)
                        del clusters[cluster.__hash__()]
                    # dominance factor
                    else:
                        in_cluster.opponent_update(clusters[cluster.__hash__()])

            # add the cluster with added position, whatever it may be
            clusters[in_cluster.__hash__()] = in_cluster
    return clusters

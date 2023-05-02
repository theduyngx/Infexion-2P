from collections import defaultdict
from dataclasses import dataclass

from referee.game import HexPos, PlayerColor
from .board import Board, adjacent_positions, CellState, PLAYER_COLOR, OPPONENT_COLOR


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
        self.color       = init_state.player
        self.cells       = {self.init_pos.__hash__(): self.init_state}
        self.opponents   = defaultdict()

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

    def append(self, pos: HexPos, board: Board):
        """
        Append a cell from the board to the cluster.
        @param pos   : specified position
        @param board : the board
        """
        if pos in board:
            if board[pos].player == self.color:
                self.cells[pos.__hash__()] = board[pos]

    def reference_append(self, other):
        """
        Appending the cells of this object with another cluster's cells, but via reference.
        This means the operation is in constant time in both time and space.
        @param other : the other cluster
        """
        if type(other) == Cluster:
            if other.color == self.color:
                self.cells |= other.cells

    def opponent_update(self, other):
        """
        Update adjacent opponent cluster number of cells. If opponent cluster is not yet recorded, then
        a new entry for it will be added.
        @param other : the adjacent opponent cluster
        """
        if type(other) == Cluster:
            if self.color == other.color.opponent:
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


@dataclass(slots=True)
class Clusters:
    """
    Class representing a collection of clusters, using dictionary data structure.
    Attributes:
        clusters: the collection of clusters, with key being the hashed value of the cluster,
                  and value being the cluster itself
    """
    clusters: dict[int, Cluster]

    def __init__(self, clusters: dict[int, Cluster] = None):
        """
        Clusters constructor.
        @param clusters: the dictionary of clusters, default being None
        """
        if clusters:
            self.clusters = clusters
        else:
            self.clusters = defaultdict()

    def __contains__(self, cluster: Cluster) -> bool:
        return cluster.__hash__() in self.clusters

    def __len__(self) -> int:
        return len(self.clusters)

    def __del__(self):
        del self.clusters
        del self

    def add(self, cluster: Cluster):
        self.clusters[cluster.__hash__()] = cluster

    def copy(self):
        return Clusters(self.clusters.copy())

    def values(self):
        return self.clusters.values()

    def delete(self, cluster: Cluster):
        del self.clusters[cluster.__hash__()]


def create_clusters(board: Board) -> dict[int, Cluster]:
    """
    Create a dictionary of clusters currently on the board, where the key is each cluster's hash.
    @param board : the given board
    @return      : dictionary of clusters
    """
    clusters = Clusters()

    # for each opponent cell in state
    for cell in board.player_cells(OPPONENT_COLOR):
        # everything related to current occupied position
        pos        = cell.pos
        adjacent   = adjacent_positions(pos)
        in_cluster = Cluster(pos, CellState(pos, OPPONENT_COLOR, cell.power))

        # for each adjacent cell
        for adj_pos in adjacent:
            clusters_copy = clusters.copy()
            for cluster in clusters.values():

                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_pos in cluster:
                    if cluster[adj_pos].player == OPPONENT_COLOR:
                        in_cluster.reference_append(cluster)
                        clusters_copy.delete(cluster)
                else:
                    in_cluster.append(adj_pos, board)

            # add the cluster with added position, whatever it may be
            clusters_copy.add(in_cluster)
            del clusters
            clusters = clusters_copy

    # for each player cell in state
    for cell in board.player_cells(PLAYER_COLOR):
        # everything related to current occupied position
        pos        = cell.pos
        adjacent   = adjacent_positions(pos)
        in_cluster = Cluster(pos, CellState(pos, PLAYER_COLOR, cell.power))

        # for each adjacent cell
        for adj_pos in adjacent:
            clusters_copy = clusters.copy()
            for cluster in clusters.values():

                # if adjacent cell belongs to a cluster already and of same color as player in question
                if adj_pos in cluster:
                    if cluster[adj_pos].player == PLAYER_COLOR:
                        in_cluster.reference_append(cluster)
                        clusters_copy.delete(cluster)
                    # dominance factor
                    else:
                        in_cluster.opponent_update(cluster)
                else:
                    in_cluster.append(adj_pos, board)

            # add the cluster with added position, whatever it may be
            clusters_copy.add(in_cluster)
            del clusters
            clusters = clusters_copy
    return clusters

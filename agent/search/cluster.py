"""
    Module  : cluster.py
    Purpose : Including the classes representing a single cluster, a collection of clusters, and a
              function to create said collection from a given state of the board.

Note: A cluster is simply a region of adjacent pieces of the same color. This is an important piece
of information because it is believed that cluster formation is a good strategy to build defense
and offense within the game.
"""

from collections import defaultdict
from dataclasses import dataclass

from referee.game import HexPos, PlayerColor
from agent.game import Board, CellState, PLAYER_COLOR, OPPONENT_COLOR
from .search_utils import adjacent_positions


@dataclass(slots=True)
class Cluster:
    """
    Class represents a cluster, which is a connected region of pieces of the same color on
    the board. When creating a cluster, it must be initialized with a proper cell, including
    its position on the board and its state.

    The initial cell is important because it dictates the hash value of the cluster, which
    can be used for quick accessing itself in a consistent and efficient manner.

    Attributes:
        init_state : the initial cell's state
        init_pos   : the initial cell's position
        color      : the color of the cluster
        cells      : all cells that are within the cluster, initialized with the initial cell
        opponents  : dictionary of adjacent opponent clusters - key being the cluster itself,
                     and value being its number of cells
    """
    init_state : CellState
    init_pos   : HexPos
    color      : PlayerColor
    cells      : dict[int, CellState] = defaultdict
    opponents  : dict[int, int] = defaultdict

    def __init__(self, init_state: CellState):
        """
        Cluster constructor. Requires the information of the initial cell.
        @param init_state : initial cell's state
        """
        self.init_state = init_state
        self.init_pos   = init_state.pos
        self.color      = init_state.color
        self.cells      = {self.init_pos.__hash__(): self.init_state}
        self.opponents  = defaultdict()

    def __getitem__(self, pos: HexPos) -> CellState:
        """
        Accessing a cell via its position quickly within a cluster.
        @param pos : cell's position
        @return    : cell's state
        """
        return self.cells[pos.__hash__()]

    def __setitem__(self, pos: HexPos, cell: CellState):
        """
        Setting an entry, with key being the position and value being cell at said position.
        @param pos  : specified position
        @param cell : the cell at position
        """
        # assert cell and cell.color == self.color and cell.power > EMPTY_POWER
        self.cells[pos.__hash__()] = cell

    def __contains__(self, pos: HexPos) -> bool:
        """
        Check whether a cluster contains a cell with specified position or not.
        @param pos : specified position
        @return    : boolean denoting whether cluster contains cell with position
        """
        return pos.__hash__() in self.cells

    def __len__(self) -> int:
        """
        The length of the cluster is defined as the number of cells that it contains.
        @return: the number of cells that cluster contains
        """
        return len(self.cells)

    def get_power(self) -> int:
        """
        Get the total power of the cluster.
        @return: the total power of cluster
        """
        return sum(self.cells)

    def get_opponents(self):
        """
        Get the iterable list of hashed values of opponent clusters.
        @return: iterable list of hashed opponent clusters
        """
        return self.opponents.keys()

    def append(self, pos: HexPos, cell: CellState):
        """
        Append a cell from the board to the cluster.
        @param pos  : specified position
        @param cell : the cell
        """
        if cell.color == self.color:
            self[pos] = cell

    def reference_append(self, other):
        """
        Appending the cells of this object with another cluster's cells, via reference.
        This means the operation is in constant time in both time and space.
        @param other : the other cluster
        """
        if type(other) == Cluster:
            if other.color == self.color:
                self.cells |= other.cells

    def opponent_update(self, other: 'Cluster'):
        """
        Update adjacent opponent cluster number of cells. If opponent cluster is not yet
        recorded, then a new entry for it will be added.
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
    Class representing a collection of clusters, using dictionary data structure. We will refer to
    this structure simply as the representation of a list of clusters.
    Attributes:
        clusters: the list of clusters, using dictionary structure where key being the hashed value
                  of the cluster, and value being the cluster itself
    """
    clusters: dict[int, Cluster]

    def __init__(self, clusters: dict[int, Cluster] = None):
        """
        Clusters constructor.
        @param clusters: the dictionary of clusters, default = None
        """
        if clusters:
            self.clusters = clusters
        else:
            self.clusters = defaultdict()

    def __getitem__(self, key: Cluster | int) -> Cluster:
        """
        Get cluster from the list of clusters.
        @param key : either the cluster (any mutation of itself as long as initial state remains)
                     or the cluster's hashed value
        @return    : the cluster from list
        """
        if type(key) == Cluster:
            return self.clusters[key.__hash__()]
        elif type(key) == int:
            return self.clusters[key]

    def __contains__(self, cluster: Cluster) -> bool:
        """
        Check whether Clusters contain a specified cluster or not.
        @param cluster : specified cluster
        @return        : true if contains, false if otherwise
        """
        return cluster.__hash__() in self.clusters

    def __len__(self) -> int:
        """
        The number of clusters stored within data class.
        @return: number of clusters
        """
        return len(self.clusters)

    def __del__(self):
        """
        Delete itself.
        """
        del self.clusters
        del self

    def add(self, cluster: Cluster):
        """
        Add a cluster to the list of clusters.
        @param cluster:
        @return:
        """
        self.clusters[cluster.__hash__()] = cluster

    def copy(self) -> 'Clusters':
        """
        Creating a copy of itself.
        @return: copy of itself
        """
        return Clusters(self.clusters.copy())

    def values(self):
        """
        Get an iterable list of clusters of the data class.
        @return: the iterable list of clusters
        """
        return self.clusters.values()

    def remove(self, cluster: Cluster):
        """
        Remove a specified cluster from the list of clusters.
        @param cluster: specified cluster
        """
        del self.clusters[cluster.__hash__()]


def create_clusters(board: Board) -> Clusters:
    """
    Create a dictionary of clusters currently on the board, where the key is each cluster's hash.
    We loop through the opponent pieces first, and then the player pieces. This is because the
    dominance factor determined by cluster evaluations compares the cluster size and their power
    of player against enemy.
    @param board : the given board
    @return      : dictionary of clusters
    """
    clusters = Clusters()

    # for each opponent cell in state
    for cell in board.player_cells(OPPONENT_COLOR):
        in_cluster = Cluster(cell)

        # for each adjacent cell
        for adj_pos in adjacent_positions(cell.pos):
            clusters_copy = clusters.copy()
            for cluster in clusters.values():

                # cluster not in copy anymore means it has already been merged so skip
                if cluster not in clusters_copy:
                    continue

                # if adjacent cell already belongs to a cluster and of same color
                if adj_pos in cluster:
                    if cluster[adj_pos].color == in_cluster.color:
                        in_cluster.reference_append(cluster)
                        clusters_copy.remove(cluster)
                else:
                    in_cluster.append(adj_pos, board[adj_pos])

            # add the cluster with added position, whatever it may be
            clusters_copy.add(in_cluster)
            del clusters
            clusters = clusters_copy

    # for each player cell in state
    for cell in board.player_cells(PLAYER_COLOR):
        in_cluster = Cluster(cell)

        # for each adjacent cell
        for adj_pos in adjacent_positions(cell.pos):
            clusters_copy = clusters.copy()
            for cluster in clusters.values():

                # skip merged clusters
                if cluster not in clusters_copy:
                    continue

                # if adjacent cell belongs to a cluster already and of same color
                if adj_pos in cluster:
                    if cluster[adj_pos].color == in_cluster.color:
                        in_cluster.reference_append(cluster)
                        clusters_copy.remove(cluster)
                    # dominance factor
                    else:
                        in_cluster.opponent_update(cluster)
                else:
                    in_cluster.append(adj_pos, board[adj_pos])

            # add the cluster with added position, whatever it may be
            clusters_copy.add(in_cluster)
            del clusters
            clusters = clusters_copy
    return clusters
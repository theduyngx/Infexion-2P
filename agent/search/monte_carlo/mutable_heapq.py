"""
Module:
    ``mutable_heapq.py``

Purpose:
    Max heap (priority queue) that can have its node data mutated, used specifically
    for the MCTS nodes.

Notes:
    This is a max heap structure which sorts list of nodes with priority being the best UCT score.
    Since these scores are constantly being mutated, a mutable heap structure is therefore needed.
"""

import heapq
import itertools
from .mc_node import MonteCarloNode

REMOVED = None
NEW     = 'new'


class MutableHeap:
    """
    Mutable heap object representing a max-heap with values of its entries mutable.
    The entries of the mutable heap is the node of the Monte Carlo tree.
    """

    def __init__(self):
        self.entry_finder = {}
        self.pq = []
        self.counter = itertools.count()
        return

    def add_task(self, task: MonteCarloNode, priority=0):
        """
        Add a new task or update the priority of an existing task
        """
        if task.hash_val in self.entry_finder:
            self.remove_task(task.hash_val)
        count = next(self.counter)
        entry = [task.depth, priority, count, task]
        self.entry_finder[task.hash_val] = entry
        heapq.heappush(self.pq, entry)

    def remove_task(self, task: MonteCarloNode):
        """
        Mark an existing task as REMOVED.  Raise KeyError if not found.
        """
        entry = self.entry_finder.pop(task.hash_val)
        entry[-1] = None

    def pop_task(self):
        """
        Remove and return the lowest priority task. Raise KeyError if empty.
        """
        while self.pq:
            depth, priority, count, task = heapq.heappop(self.pq)
            if task is not None:
                del self.entry_finder[task.hash_val]
                return task
        raise KeyError('pop from an empty priority queue')

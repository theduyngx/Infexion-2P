from collections import defaultdict

from agent.board import Board


class Node:
    identity: int
    children: dict[int, 'Node']

    def __init__(self, board: Board):
        self.identity = board.__hash__()
        self.children = defaultdict()

    def add_child(self, child: 'Node'):
        self.children[child.identity] = child


class MemoryTree:
    root  : Node
    curr  : Node
    nodes : dict[int, Node]

    def __init__(self, node: Node):
        self.root  = node
        self.curr  = node
        self.nodes = {node.identity: node}

    def __contains__(self, board: Board) -> bool:
        return board.__hash__() in self.nodes

    def to_node(self, board: Board):
        self.curr = self.nodes[board.__hash__()]

    def append_and_move_to(self, board: Board):
        child = Node(board)
        self.curr.add_child(child)
        self.nodes[board.__hash__()] = child
        self.curr = child

    def delete_branch(self, board: Board):
        branch = self.nodes[board.__hash__()]
        self.delete_nodes(branch)

    def delete_nodes(self, branch: Node):
        for child in branch.children.values():
            self.delete_nodes(child)
        del branch

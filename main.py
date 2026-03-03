from __future__ import annotations

class Node:
    def __init__(self, name: str):
        self.name = name
        self.edges = list()

    def addEdge(self, node: Node, cost: float):
        #add edge going out of self
        outEdge: Edge = Edge(node, cost)
        self.edges.append(outEdge)

        #add edge going into self
        inEdge: Edge = Edge(self, cost)
        node.edges.append(inEdge)

    def calcHeuristic(self) -> float:
        return 0


class Edge:
    def __init__(self, node: Node, cost: float):
        self.node = node
        self.cost = cost

    




myNode: Node = Node("My node")

print(myNode.name)
        
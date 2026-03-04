from __future__ import annotations
import json


class Node:
    """
    name: str
    edges: list[Edge]
    """
    def __init__(self, name: str):
        self.name = name
        self.edges: list[Edge] = list()
        pass

    def __str__(self):
        return f"{self.name}"
        
    
    def addEdge(self, edge: Edge):
        #append edge to self and to other node
        #edge should be appended such that edge.homeNode == self
        if edge.homeNode == self:
            self.edges.append(edge)

        elif edge.destNode == self:
            tempEdge: Edge = Edge(edge.destNode, edge.homeNode, edge.cost)
            self.edges.append(tempEdge)

        else:
            print(f"Edge does not belong to node: {edge}")

        return

    def calcHeuristic(self) -> float:
        return 0


class Edge:
    """
    homeNode: Node
    destNode: Node
    cost: float
    """
    def __init__(self, homeNode: Node, destNode: Node, cost: float):
        self.homeNode = homeNode
        self.destNode = destNode
        self.cost = cost
        pass

    def __str__(self):
        return f"{self.homeNode.name} - {self.destNode.name} : {self.cost}"


class NodeMap:
    """
    nodes: dict[name: str | node: Node]
    """
    def __init__(self):
        self.nodes = dict()
        pass

    def addNode(self, node: Node):
        #add node to dict
        self.nodes[node.name] = node

        #connect all edges of node to map
        for edge in node.edges[:]:
            
            assert(edge.homeNode == node)

            #find target node in nodes dict
            #if not there then throw KeyError
            if edge.destNode.name in self.nodes:
                targetNode: Node = self.nodes[edge.destNode.name]
                targetNode.addEdge(edge)

            else:
                print(f"Key not found: {edge.destNode.name}")
                node.edges.remove(edge)
        pass

    def printMap(self):
        for key in self.nodes:

            node: Node = self.nodes[key]
            print(f"{node}:")

            for edge in node.edges:
                print(f"\t{edge}")

            print()
        pass








#main==============================================
def main():
    map: NodeMap = NodeMap()

    """
    t1: Node = Node("house")
    map.addNode(t1)

    t2: Node = Node("school")
    e1 = Edge(t2, t1, 1)
    t2.addEdge(e1)
    map.addNode(t2)
    """

    setUp(map)
    print()
    map.printMap()

    return








#functions=========================================

def setUp(map: NodeMap):
    loadNodes("maps/mapNodes.json", map)
    pass


""""returns the json data as a python dict"""
def loadJSON(fileName: str):
    try:
        with open(fileName, 'r') as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError
    

"""loads nodes specified in JSON file into map"""
def loadNodes(fileName: str, map: NodeMap):
    try:
        data = loadJSON(fileName)

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError
    
    #for each node in JSON add to map
    for node in data["nodes"]:
        #get name
        newNode: Node = Node(node["name"])

        #get edges
        for edge in node["edges"]:
            target: str = edge["name"]
            #check if target exists in map
            if target in map.nodes:
                newEdge: Edge = Edge(newNode, map.nodes[target], edge["cost"])
                newNode.edges.append(newEdge)

        #add node to map
        map.addNode(newNode)
    pass

def A_Star(start: Node, goal: Node):
    path: list[Node] = list()
    cost: float = 0

    return path, cost








    






main()      
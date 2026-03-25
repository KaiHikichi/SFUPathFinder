from __future__ import annotations
import json


class Node:
    """
    name: str
    edges: list[Edge]
    h: float
    long: float
    lat: float
    """
    def __init__(self, name: str, long: float, lat: float):
        self.name = name
        self.edges: list[Edge] = list()
        self.h = 0
        self.long = long
        self.lat = lat
        pass

    def __str__(self):
        return f"{self.name}"
        
    
    def addEdge(self, edge: Edge):
        #append edge to self and to other node
        #edge should be appended such that edge.homeNode == self
        if edge.homeNode == self:
            self.edges.append(edge)

        elif edge.destNode == self:
            tempEdge: Edge = Edge(edge.destNode, edge.homeNode, edge.cost, edge.isIndoor)
            self.edges.append(tempEdge)

        else:
            print(f"Edge does not belong to node: {edge}")

        return

    def calcHeuristic(self) -> float:
        self.h = 0


class Edge:
    """
    homeNode: Node
    destNode: Node
    cost: float
    isIndoor: bool
    """
    def __init__(self, homeNode: Node, destNode: Node, cost: float, isIndoor: bool):
        self.homeNode = homeNode
        self.destNode = destNode
        self.cost = cost
        self.isIndoor = isIndoor
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

class FringeElement:
    def __init__(self, node: Node, parent: FringeElement, cost: float):
        self.node = node
        self.parent = parent
        self.cost = cost
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

    (path, cost) = A_Star(map.nodes["CS Common Room"], map.nodes["AQ NW"])

    for node in path:
        print(node)

    print(cost)

    return





#functions=========================================

def setUp(map: NodeMap):
    loadNodes("maps/mapNodes.json", map)
    pass


"""returns the json data as a python dict"""
def loadJSON(fileName: str):
    try:
        with open(fileName, 'r') as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError

    

"""
    loads nodes specified JSON file into map
    edges that connect to nodes that are not yet part of the map are ignored
"""
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
        newNode: Node = Node(node["name"], node["long"], node["lat"])

        #get edges
        for edge in node["edges"]:
            target: str = edge["name"]
            #check if target exists in map
            for key in map.nodes:
                if target.lower() == key.lower():
                    newEdge: Edge = Edge(newNode, map.nodes[target], edge["cost"], edge["isIndoor"])
                    newNode.edges.append(newEdge)

        #add node to map
        map.addNode(newNode)
    pass


def A_Star(start: Node, goal: Node):
    finalPath: list[Node] = list()
    cost: float = 0

    fringe: list[FringeElement] = list()
    currentFE: FringeElement = FringeElement(start, None, 0)

    foundGoal: bool = False
    while not foundGoal:
        #create fringe elements for all the edges
        for edge in currentFE.node.edges:
            #get cost of new fringe element (cost of current, minus its h, plus the cost to get to new node, plus new h)
            newCost: float = currentFE.cost - currentFE.node.h + edge.cost + edge.destNode.h
            temp: FringeElement = FringeElement(edge.destNode, currentFE, newCost)
            fringe.append(temp)

        #find the path with lowest cost
        cheapest: FringeElement = fringe[0]
        for FE in fringe:
            if FE.cost < cheapest.cost:
                cheapest = FE
        
        #expand the cheapest FringeElement
        currentFE = cheapest
        fringe.remove(cheapest)

        if currentFE.node == goal:
            foundGoal = True

    #get final path
    finalPath.append(buildPath(finalPath, currentFE))
    cost = currentFE.cost

    return finalPath, cost

def buildPath(path: list[Node], FE: FringeElement):
    if FE.parent == None:
        return FE.node
    
    path.append(buildPath(path, FE.parent))
    return FE.node












    






main()      
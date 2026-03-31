from __future__ import annotations
from enum import Enum
import math

class Weather(Enum):
    CLEAR = 1
    RAINING = 1.25
    SNOWY = 1.75

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
        #append edge to self
        #edge should be appended such that edge.homeNode == self
        if edge.homeNode == self:
            self.edges.append(edge)

        elif edge.destNode == self:
            tempEdge: Edge = Edge(edge.destNode, edge.homeNode, edge.cost, edge.isIndoor)
            self.edges.append(tempEdge)

        else:
            print(f"Edge does not belong to node: {edge}")

        return
    
    """
    Update edge costs based on user weather tolerance and current weather state
    weatherTolerance: float between 0 and 1, 1 means user does not care about the weather
    """
    def updateWeatherCosts(self, weatherTolerance: float, weatherState: Weather):
        for edge in self.edges:
            edge: Edge
            edge.updateWeatherCosts(weatherTolerance, weatherState)
        pass

    def calcHeuristic(self, goal: Node):
        dist: float = math.sqrt((pow(self.long - goal.long, 2) + pow(self.lat - goal.lat, 2)))
        self.h = dist
        pass


class Edge:
    """
    homeNode: Node
    destNode: Node
    cost: float
    isIndoor: bool

    edges are directed (for a pair of connected nodes, each node has one edge pointing to the other)
    """
    def __init__(self, homeNode: Node, destNode: Node, cost: float, isIndoor: bool):
        self.homeNode = homeNode
        self.destNode = destNode
        self.cost = self.calcCost()
        self.isIndoor = isIndoor
        pass

    """
    Update cost based on user weather tolerance and current weather state
    weatherTolerance: float between 0 and 1, 1 means user does not care about the weather
    """
    def updateWeatherCosts(self, weatherTolerance: float, weatherState: Weather):
        if (self.isIndoor == False):
            self.cost = self.cost + (1 - weatherTolerance) * weatherState.value
        pass

    """calculate the cost of this edge based off distance between nodes"""
    def calcCost(self) -> float:
        dist: float = math.sqrt((pow(self.homeNode.long - self.destNode.long, 2) + pow(self.homeNode.lat - self.destNode.lat, 2)))
        return dist

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
            if edge.destNode.name in self.nodes.keys():
                targetNode: Node = self.nodes[edge.destNode.name]
                targetNode.addEdge(edge)

            else:
                print(f"Key not found: {edge.destNode.name}")
                node.edges.remove(edge)
        pass

    """
    Update edge costs based on user weather tolerance and current weather state
    weatherTolerance: float between 0 and 1, 1 means user does not care about the weather
    """
    def updateWeatherCosts(self, weatherTolerance: float, weatherState: Weather):
        if (weatherTolerance < 0 or weatherTolerance > 1):
            print("invalid weather tolerance")
            pass

        for node in self.nodes.values():
            node: Node
            node.updateWeatherCosts(weatherTolerance, weatherState)
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

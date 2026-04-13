from util import graph
from util.graph import FringeElement, Node



def A_Star(start: Node, goal: Node):
    finalPath: list[Node] = list()
    cost: float = 0

    fringe: list[FringeElement] = list()
    currentFE: FringeElement = FringeElement(start, None, 0, 0)

    visited: list[Node] = list()

    foundGoal: bool = False
    while not foundGoal:
        for edge in currentFE.node.edges:
            if (edge.destNode in visited):
                continue

            newG: float = currentFE.g + edge.cost
            newCost: float = newG + edge.destNode.h
            temp: FringeElement = FringeElement(edge.destNode, currentFE, newCost, newG)
            fringe.append(temp)

        cheapest: FringeElement = fringe[0]
        for FE in fringe:
            if FE.cost < cheapest.cost:
                cheapest = FE

        currentFE = cheapest
        fringe.remove(cheapest)
        visited.append(cheapest.node)

        if currentFE.node == goal:
            foundGoal = True

    finalPath.append(buildPath(finalPath, currentFE))
    cost = currentFE.g

    return finalPath, cost

def buildPath(path: list[Node], FE: FringeElement):
    if FE.parent == None:
        return FE.node
    
    path.append(buildPath(path, FE.parent))
    return FE.node


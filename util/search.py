from util import graph
from util.graph import FringeElement, Node



def A_Star(start: Node, goal: Node):
    finalPath: list[Node] = list()
    cost: float = 0

    fringe: list[FringeElement] = list()
    currentFE: FringeElement = FringeElement(start, None, 0)

    visited: list[Node] = list()

    foundGoal: bool = False
    while not foundGoal:
        #expand current fringe element
        #create fringe elements for all the edges
        for edge in currentFE.node.edges:
            #ignore nodes that have already been expanded
            if (edge.destNode in visited):
                continue

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
        visited.append(cheapest.node)

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


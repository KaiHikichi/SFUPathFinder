from __future__ import annotations
from util import graph
from util.graph import NodeMap, Node, Edge, FringeElement
from util.setup import setUp
from util.search import A_Star



#main==============================================
def main():
    #setup
    map: NodeMap = NodeMap()
    setUp(map, "maps/mapNodes.json")

    #print the map
    print()
    map.printMap()

    #find path and print it
    (path, cost) = A_Star(map.nodes["Saywell"], map.nodes["Dining Hall"])
    for node in path:
        print(node)
    print(cost)


    pass






 


if __name__ == "__main__":
    main()      
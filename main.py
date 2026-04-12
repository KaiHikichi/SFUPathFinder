from __future__ import annotations
from util.graph import NodeMap
from util.setup import setUp
from util.search import A_Star
from util.graph import Weather
from util.graph import simulateConstruction



#main==============================================
def main():
    #setup
    map: NodeMap = NodeMap()
    setUp(map, "maps/mapNodes.json")

    #update based on wether
    map.updateWeatherCosts(0.5, Weather.RAINING)

    #simulate construction
    simulateConstruction(map, 0.01, 2)

    #find path
    (path, cost) = A_Star(map.nodes["Residence Townhouses"], map.nodes["CS Common Room"])

    #print the path
    for node in path:
        print(node)
    print(cost)


    pass






 


if __name__ == "__main__":
    main()      
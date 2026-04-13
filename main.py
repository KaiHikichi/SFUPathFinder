from __future__ import annotations
from util.graph import NodeMap, Node
from util.setup import setUp
from util.search import A_Star
from util.graph import Weather
from util.graph import simulateConstruction
from util.edge_operations import METERS_PER_MIN
from util.edge_operations import update_edge_costs_in_path, estimate_time_per_edge

METERS_PER_DEGREE = 111139 




#main==============================================
def main():
    #setup
    map: NodeMap = NodeMap()
    setUp(map, "maps/mapNodes.json")

    while True:

        #get weather
        weatherIn = input("Weather (0, 1, 2): ")
        weather: Weather
        if weatherIn == "0":
            weather = Weather.CLEAR
        elif weatherIn == "1":
            weather = Weather.RAINING
        else:
            weather = Weather.SNOWY

        #get weather tolerance
        weatherTol = input("Weather tolerance: ")

        #update based on wether
        map.updateWeatherCosts(float(weatherTol), weather)

        #construction chance and penalty can be set below
        constructionChance = input("Construction chance (0 - 1.0): ")
        constructionPenalty = input("Construction penalty: ")
        #simulate construction
        simulateConstruction(map, float(constructionChance), float(constructionPenalty))

        #get start and dest
        start = input("Start: ")
        dest = input("Dest: ")        
       
        for node in map.nodes.values():
            noe: Node
            node.h = node.calcHeuristic(map.nodes[dest])

        #find path
        (path, cost) = A_Star(map.nodes[start], map.nodes[dest])

        #print the path
        print("\nPath ===================")
        for node in path:
            print(node)
        print("\nEstimated time walk:")
        print(cost * METERS_PER_DEGREE / METERS_PER_MIN)
        print()

        #get how long it took for user to walk path
        #update the edge costs to learn different walking speeds
        time = input("How long did it take to walk in minutes: ")
        times = estimate_time_per_edge(path, float(time), cost)
        expectedTimes = estimate_time_per_edge(path, cost  * METERS_PER_DEGREE / METERS_PER_MIN, cost)
        update_edge_costs_in_path(path, times, expectedTimes)


    pass






 


if __name__ == "__main__":
    main()

    # IF YOU DONT WANT MAIN TO OPEN UI, COMMENT THIS OUT
    import sfu_pathfinder_ui 
from __future__ import annotations
from util.graph import NodeMap
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

        #update based on wether
        map.updateWeatherCosts(0.5, Weather.CLEAR)

        #simulate construction
        simulateConstruction(map, 0.001, 2)

        #get start and dest
        start = input("Start: ")
        dest = input("Dest: ")

        start = "ASB Entrance"
        dest = "CS Common Room"

        #find path
        #(path, cost) = A_Star(map.nodes["Residence Townhouses"], map.nodes["CS Common Room"])
        (path, cost) = A_Star(map.nodes[start], map.nodes[dest])

        #print the path
        for node in path:
            print(node)
        print(cost * METERS_PER_DEGREE / METERS_PER_MIN)

        #get how long it took for user to walk path
        #update the edge costs to learn different walking speeds
        time = input("How long did it take to walk in minutes: ")
        times = estimate_time_per_edge(path, int(time), cost)
        update_edge_costs_in_path(path, times)


    pass






 


if __name__ == "__main__":
    main()      
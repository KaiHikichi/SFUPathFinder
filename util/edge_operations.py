import json
import math
from util.graph import Node, Edge


LEARNING_RATE = 0.1
METERS_PER_MIN = 85



def update_edge_cost_by_speed(edge: Edge, time: float, estTime: float): 
    # Arriving 1 minute earlier or later does not change cost, change this value as needed
    threshold = 0.1

    if abs(estTime - time) < threshold:
        return edge.trueCost
    
    # If arriving earlier than expected, reduce cost
    if time < estTime:
        return edge.trueCost * (1 + LEARNING_RATE * ((time / estTime) - 1))
    
    # If arriving later than expected, increase cost
    return edge.trueCost * (1 + LEARNING_RATE * ((time / estTime) - 1))


def update_edge_costs_in_path(finalPath: list[Node], time: list[float], estTime):
    """
    Given a path (List of Nodes) 
    and the time taken to traverse each edge (List of floats), 
    update the cost of each edge in the path based on the time taken.
    estTime is time in minutes
    """
    
    for i in range(len(finalPath) - 1):
        node = finalPath[i]
        next_node = finalPath[i + 1]

        edge = next((e for e in node.edges if e.destNode == next_node), None)

        if edge is not None:
            new_cost = update_edge_cost_by_speed(edge, time[i], estTime)
            edge.cost = new_cost
            edge.trueCost = new_cost

            # update back edge too
            back_edge = next((e for e in next_node.edges if e.destNode == node), None)
            if back_edge is not None:
                back_edge.cost = new_cost
                back_edge.trueCost = new_cost

    return

def estimate_time(edge: Edge):
    """
    Given an edge estimate how long it should take to travel in minutes
    """
    
    #cost is measured in lat, long
    #convert to meters
    distance: float = coords_to_meters(edge.homeNode.lat, edge.homeNode.long, edge.destNode.lat, edge.destNode.long)

    #avg human walking speed in meters per minute
    avgWalkingSpeed: float = METERS_PER_MIN

    return distance / avgWalkingSpeed

def coords_to_meters(lat1, lon1, lat2, lon2):
    R = 6378.137  # Radius of earth in KM
    d_lat = (lat2 - lat1) * math.pi / 180
    d_lon = (lon2 - lon1) * math.pi / 180
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d * 1000  # meters

def estimate_time_per_edge(path: list[Node], totalTime: float, totalCost: float):
    """
    given the time taken to walk a path estimate the time spent walking on each edge
    time measured in minutes
    """

    times: list[float] = list()

    for i in range(len(path) - 1):
        node = path[i]
        next_node = path[i + 1]

        # Find the edge connecting node to next_node
        edge = next((e for e in node.edges if e.destNode == next_node), None)

        # If there is an edge between node and next_node
        if edge is not None: 
            # add estimated time spent to list

            #estimate time spent on edge by proportion of total cost
            estTime = (edge.cost / totalCost) * totalTime

            times.append(estTime)

    return times


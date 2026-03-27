import json
from main import Node, Edge, NodeMap, loadNodes, loadJSON



def update_edge_cost_by_speed(edge: Edge, time: float): 
    # Arriving 1 minute earlier or later does not change cost, change this value as needed
    threshold = 1 

    if abs(edge.cost - time) < threshold:
        return edge.cost
    
    # If arriving earlier than expected, reduce cost
    if time < edge.cost:
        return edge.cost * (1 - (edge.cost - time) / edge.cost)
    
    # If arriving later than expected, increase cost
    return edge.cost * (1 + (time - edge.cost) / edge.cost)


def update_edge_costs_in_path(finalPath: list[Node], time: list[float]):
    """
    Given a path (List of Nodes) 
    and the time taken to traverse each edge (List of floats), 
    update the cost of each edge in the path based on the time taken.
    """
    
    for i in range(len(finalPath) - 1):
        node = finalPath[i]
        next_node = finalPath[i + 1]

        # Find the edge connecting node to next_node
        edge = next((e for e in node.edges if e.destNode == next_node), None)

        # If there is an edge between node and next_node
        if edge is not None: 
            # Update the cost of the edge based on the time taken
            new_cost = update_edge_cost_by_speed(edge, time[i])
            print(f"Updating cost of edge from {node.name} to {next_node.name} from {edge.cost} to {new_cost}")
            edge.cost = new_cost

    return
            

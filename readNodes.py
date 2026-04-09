import json
from util.setup import loadJSON

# Read nodes from a CSV file and write to JSON file for pathfinding.
# Allows convenience of using Excel to create nodes and edges, and then easily importing them into our program.

def main():
    # Take in CSV file name and JSON file name from user
    fileName = input("Please enter the name of the CSV file: ")
    try:
        file = open(fileName, "r")
    except FileNotFoundError:
        raise FileNotFoundError
    
    jsonFileName = input("Please enter the name of the JSON file to write to: ")
    
    # Load existing data from JSON file
    data = loadJSON(jsonFileName)
    
    # Dissect each line of the CSV file and create nodes and edges accordingly
    for line in file:
        name, long, lat, edges = readLine(line.strip())
        createNode(data, name, long, lat, edges)


    # Write back to JSON file
    with open(jsonFileName, "w") as f:
        json.dump(data, f, indent=4)

    file.close()



def readLine(line):
    # Expected format: name,long,lat,edge1_name,edge1_cost,edge1_isIndoor,edge2_name,edge2_cost,edge2_isIndoor,...
    # Dissect name, long, lat from first 3 parts

    parts = line.split(",")
    name = parts[0]
    long = float(parts[1])
    lat = float(parts[2])
    edges = []

    # Read remaining data for edges in groups of 3
    for i in range(3, len(parts), 3):
        
        edge_name = parts[i]

        if edge_name == "":
            break

        cost = float(parts[i+1])
        isIndoor = parts[i+2].lower() == "true"
        edges.append({
            "name": edge_name,
            "cost": cost,
            "isIndoor": isIndoor
        })

    return name, long, lat, edges

def createNode(data, name: str, long: float, lat: float, edges):
    
    # Code borrowed from WriteToJSON function in readNodes.py. Adapted to avoid repeated file opening

    # Define your new node
    new_node = {
        "name": name,
        "long": long,
        "lat": lat,
        "edges": edges
    }

    # Append to the nodes list
    data["nodes"].append(new_node)

    #add edges to existing nodes
    for edge in edges:
        for node in data["nodes"]:
            if(edge["name"] == node["name"]):
                newEdge = {
                    "name": name,
                    "cost": edge["cost"],
                    "isIndoor": edge["isIndoor"]
                }
                node["edges"].append(newEdge)

    return


if __name__ == "__main__":
    main()
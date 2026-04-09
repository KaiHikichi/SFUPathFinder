from util import setup
from util.setup import loadJSON
import json

JSONFILE: str = "maps/mapNodes.json"

def main():
    #get info
    name: str = input("\nName: ")
    long: float = float(input("Long: "))
    lat: float = float(input("Lat: "))
    edges = list()

    while(True):
        
        edgeDest: str = input("Edge destination (enter 'done' to continue): ")
        if(edgeDest.lower() == "done"): break

        cost: float = float(input("Cost: "))
        s = input("Is indoor? (True/False): ")
        isIndoor: bool = False
        if(s == "True"):
            isIndoor = True
        

        edge = {
            "name": edgeDest,
            "cost": cost,
            "isIndoor": isIndoor
        }
        edges.append(edge)
        

    #verify
    print()
    print(f"Name: {name}\nlong: {long}\nlat: {lat}")
    print("Edges: ")
    for edge in edges:
        print(f"\tDest: {edge["name"]} Cost: {edge["cost"]} Indoor: {edge["isIndoor"]}")

    correct = input("\nIs this correct? (y/n): ")

    #write to json
    if(correct.lower() == 'y'):
        writeToJSON(JSONFILE, name, long, lat, edges)

    return




def writeToJSON(fileName: str, name: str, long: float, lat: float, edges):
    try:
        data = loadJSON(fileName)

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError
    
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

    # Write back
    with open(fileName, "w") as f:
        json.dump(data, f, indent=4)

    return

























if __name__ == "__main__":
    main()
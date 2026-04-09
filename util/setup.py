from util import graph
from util.graph import NodeMap, Node, Edge
import json




def setUp(map: NodeMap, fileName: str):
    loadNodes(fileName, map)
    pass


"""returns the json data as a python dict"""
def loadJSON(fileName: str):
    try:
        with open(fileName, 'r') as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError

    

"""
    loads nodes specified JSON file into map
    edges that connect to nodes that are not yet part of the map are ignored
"""
def loadNodes(fileName: str, map: NodeMap):
    try:
        data = loadJSON(fileName)

    except FileNotFoundError:
        raise FileNotFoundError
    except json.JSONDecodeError:
        raise json.JSONDecodeError
    
    #for each node in JSON add to map
    for node in data["nodes"]:
        #get name
        newNode: Node = Node(node["name"], node["long"], node["lat"])

        #get edges
        for edge in node["edges"]:
            target: str = edge["name"]
            #check if target exists in map
            for key in map.nodes:
                if target.lower() == key.lower():
                    newEdge: Edge = Edge(newNode, map.nodes[target], edge["cost"], edge["isIndoor"])
                    newNode.edges.append(newEdge)

        #add node to map
        map.addNode(newNode)
    pass

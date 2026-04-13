from util.graph import NodeMap, Weather, Node
from util.setup import setUp
from util.search import A_Star
from util.graph import simulateConstruction
from util.edge_operations import update_edge_costs_in_path, estimate_time_per_edge
from util.edge_operations import METERS_PER_MIN

METERS_PER_DEGREE = 111139 

def test_A_Star():
    #setup
    map: NodeMap = NodeMap()
    setUp(map, "tests/testWeather2.json")

    (path, cost) = A_Star(map.nodes["A"], map.nodes["D"])

    assert path[1].name == "B"

    pass


def test_updateWeatherCosts_1(): 

    #setup
    map: NodeMap = NodeMap()
    setUp(map, "tests/testWeather1.json")

    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 5

    #adjust for outdoor
    weatherTolerance = 0.5
    map.updateWeatherCosts(weatherTolerance, Weather.SNOWY)
    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 5 * (1 + (1 - weatherTolerance) * Weather.SNOWY.value)

    pass


def test_updateWeatherCosts_2(): 

    #setup
    map: NodeMap = NodeMap()
    setUp(map, "tests/testWeather2.json")

    (path, cost) = A_Star(map.nodes["A"], map.nodes["D"])

    assert path[1].name == "B"

    #adjust for outdoor
    weatherTolerance = 0
    map.updateWeatherCosts(weatherTolerance, Weather.SNOWY)
    (path, cost) = A_Star(map.nodes["A"], map.nodes["D"])

    assert path[1].name == "B"

    pass

def test_construction_1():

     #setup
    map: NodeMap = NodeMap()
    setUp(map, "tests/testConstruction1.json")

    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 5

    simulateConstruction(map, 1, 2)

    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 5 * 2

    pass

def test_dynamic_edge_weighting_1():

    #setup
    map: NodeMap = NodeMap()
    setUp(map, "tests/testEdgeOps.json")

    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 0.0004792985106955507
    print(f"1: {cost * METERS_PER_DEGREE}")

    times = estimate_time_per_edge(path, 3, cost)
    update_edge_costs_in_path(path, times, cost * METERS_PER_DEGREE / METERS_PER_MIN)

    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 0.0006606257534372025
    print(f"2: {cost * METERS_PER_DEGREE}")


    pass










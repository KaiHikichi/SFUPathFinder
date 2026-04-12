from util import graph
from util.graph import NodeMap, Weather
from util.setup import setUp
from util.search import A_Star
from util.graph import simulateConstruction

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








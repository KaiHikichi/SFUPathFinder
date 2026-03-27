from util import graph
from util.graph import NodeMap, Weather
from util.setup import setUp
from util.search import A_Star

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

    assert cost == 1

    #adjust for outdoor
    weatherTolerance = 0.5
    map.updateWeatherCosts(weatherTolerance, Weather.SNOWY)
    (path, cost) = A_Star(map.nodes["A"], map.nodes["B"])

    assert cost == 1 + (1 - weatherTolerance) * Weather.SNOWY.value

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

    assert path[1].name == "C"

    pass







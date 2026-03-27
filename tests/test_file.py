from main import NodeMap
from main import setUp
from main import A_Star
from main import Weather



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







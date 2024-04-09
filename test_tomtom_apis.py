import requests

url = "https://api.tomtom.com/routing/1/calculateRoute"

params = {
    "key": "XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6",
    "versionNumber": 1,
    "locations": "52.37245,4.89406:52.37822,4.90041", #:52.36637,4.89454:52.379189,4.899431",
    "contentType": "json",
    "maxAlternatives": 3,
    "instructionsType": "text",
    "language": "en-GB",
    "computeBestOrder": True,
    "routeRepresentation": "polyline",
    "computeTravelTimeFor": "all",
    "routeType": "fastest",
    "traffic": True,
    "avoid": "tollRoads,motorways,ferries",
    "travelMode": "car",
    "hilliness": "normal",
    "windingness": "normal",
    "vehicleMaxSpeed": 120,
    "vehicleWeight": 1500,
    "vehicleAxleWeight": 500,
    "vehicleNumberOfAxles": 2,
    "vehicleLength": 4.5,
    "vehicleWidth": 2,
    "vehicleHeight": 1.8,
    "vehicleCommercial": False
}

response = requests.get(url, params=params)

print(response.url)
print(response.json())

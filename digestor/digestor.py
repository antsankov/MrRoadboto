import xmltodict
import argparse

route_ids = ['11',  # Vail-Vail Pass
             '10',  # Vail Pass-Copper Mtn
             '9',  # Copper Mtn-Silverthorne
             '6',  # Silverthorne-Eisenhower/Johnson tunnels
             '5060',  # Eisenhower/Johnson tunnels-Georgetown
             '4',  # Georgetown-Idaho Springs
             '3',  # Idaho Springs-Genesee
             '2']  # Genesee-C470


def main():
    parser = argparse.ArgumentParser(
            description='Gather and digest data from CDOT')
    parser.add_argument('--live', type=bool, default=False)
    args = parser.parse_args() 
    parse_routes(gather_useful_routes(args.live))


def gather_useful_routes(live=False):
    useful_routes = []
    if live:
        print('===RUNNING LIVE===')

        import os
        import requests
        import urllib

        username = os.getenv('username')
        password = os.getenv('password')

        url = "https://{0}:{1}@data.cotrip.org/xml/road_conditions.xml".format(
                username, urllib.quote(password, safe=''))
        r = requests.get(url)
        weather_routes = xmltodict.parse(r.content)
    else:
        print('---RUNNING LOCAL---')
        weather_routes = xmltodict.parse(
                open('../schema/road_conditions.xml', 'r').read())

    for route in weather_routes["rc:RoadConditionsDetails"]["rc:WeatherRoute"]:
        if route["rc:WeatherRouteId"] in route_ids:
            useful_routes.append(route)

    return useful_routes


def parse_routes(useful_routes):
    for route in useful_routes:
        if route["rc:IsHazardousCondition"] == "true":
            print route["rc:RouteName"] + " is hazardous!"
        else:
            print route["rc:RouteName"] + " is NOT hazardous!"


if __name__ == '__main__':
    main()

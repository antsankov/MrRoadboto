import xmltodict
import argparse

OBSERVED_ROUTE_IDS = set([
             '11',  # Vail-Vail Pass
             '10',  # Vail Pass-Copper Mtn
             '9',  # Copper Mtn-Silverthorne
             '6',  # Silverthorne-Eisenhower/Johnson tunnels
             '5060',  # Eisenhower/Johnson tunnels-Georgetown
             '4',  # Georgetown-Idaho Springs
             '3',  # Idaho Springs-Genesee
             '2'  # Genesee-C470
             ])

VAIL_ROUTES = set([11,10,9,6,5060,4,3,2])
COPPER_ROUTES = set([9,6,5060,4,3,2])
BRECK_ROUTES = set([9,6,5060,4,3,2])
KEYSTONE_ROUTES = set([6,5060,4,3,2])
ABASIN_ROUTES = set([6,5060,4,3,2])


class Resort:

    def __init__(self, name):
        self.name = name
        self.closed_routes = []
        self.hazardous_routes = []
        self.dates = set([])
        # TODO is the date of everything always the same? 

    def generate_message(self):
        if len(self.closed_routes) != 0:
            return 'I70 is CLOSED between {route_names}. This affects {resort}. Calculated on {date}.'.format(
                    route_names=', '.join(self.closed_routes), resort=self.name, date=self.dates) 
        
        elif len(self.hazardous_routes) != 0:
            return 'I70 is open, but marked hazardous between {route_names}. This affects {resort}. Calculated on {date}.'.format(
                     route_names=', '.join(self.hazardous_routes), resort=self.name, date=self.dates) 

        else:  
            return 'I70 is open, and makred as safe. This affects {resort}. Calculated on {date}.'.format(
                    resort=self.name, date=self.dates)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', type=bool, default=False)
    args = parser.parse_args() 
    raw = gather_observed_routes(args.live) 
    vail = parse_routes(raw)

    print(vail.generate_message())

def gather_observed_routes(live=False):
    """
    Gathers and reurns an array of parsed route dictionaries based on route_ids.
    """
    observed_routes = []
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
        if route["rc:WeatherRouteId"] in OBSERVED_ROUTE_IDS:
            observed_routes.append(route)
 
    return observed_routes


def parse_routes(raw_routes):
    """
    Converts observed routes into sane python route dictionary. 
    """

    vail = Resort('Vail') 

    closed_routes = []
    hazardous_routes = [] 
    for route in raw_routes: 
        route_state = {
                'id' : int(route['rc:WeatherRouteId']),
                'route_name' : route['rc:RouteName'],
                'date' : route['rc:CalculatedDate'], 
                'condition' : route['rc:RoadConditionCategoryTxt'],
                'condition_code' : float(route['rc:RoadConditionCategoryCd']),
                'hazardous' : bool(route['rc:IsHazardousCondition']),
                }
 
        if route_state['condition'] == 'Closed' or route_state['condition_code'] == 1:
            if route_state['id'] in VAIL_ROUTES:
                vail.closed_routes.append(route_state['route_name'])
                vail.dates.add(route_state['date'])
        
        elif route_state['hazardous']:  
            if route_state['id'] in VAIL_ROUTES:
                vail.hazardous_routes.append(route_state['route_name'])
                vail.dates.add(route_state['date'])
                      
    return vail


if __name__ == '__main__':
    main()

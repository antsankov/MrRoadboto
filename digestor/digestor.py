import xmltodict
import argparse
from datetime import datetime


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
COPPER_BRECK_ROUTES = set([9,6,5060,4,3,2])
KEYSTONE_ABASIN_ROUTES = set([6,5060,4,3,2])


class Resort:

    def __init__(self, name, watched_routes, raw_routes):
        self.name = name
        self.watched_routes = watched_routes
        self.raw_routes = raw_routes
        
        self.closed_routes = []
        self.hazardous_routes = []
        self.dates = []
        # TODO is the date of everything always the same? 

        for route in self.raw_routes:
            if int(route['rc:WeatherRouteId']) in self.watched_routes:
                route_state = {
                        'id' : int(route['rc:WeatherRouteId']),
                        'route_name' : route['rc:RouteName'],
                        'date' : datetime.strptime(route['rc:CalculatedDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                        'condition' : route['rc:RoadConditionCategoryTxt'],
                        'condition_code' : float(route['rc:RoadConditionCategoryCd']),
                        'hazardous' : bool(route['rc:IsHazardousCondition']),
                        }
 
                if route_state['condition'] == 'Closed' or route_state['condition_code'] == 1:
                    self.closed_routes.append(route_state['route_name'])
                    self.dates.append(route_state['date'])
                
                elif route_state['hazardous']:   
                    self.hazardous_routes.append(route_state['route_name'])
                    self.dates.append(route_state['date'])

    def generate_message(self): 
        if len(self.closed_routes) != 0:
            return 'I70 is CLOSED between {aggregate_route}. This affects {resort}. Calculated on {date}.'.format(
                    aggregate_route= route_digest(self.closed_routes), resort=self.name, date=earliest_date(self.dates)) 
        
        elif len(self.hazardous_routes) != 0:
            return 'I70 is OPEN, but is being impacted by weather between {aggregate_route}. This affects {resort}. Calculated on {date}.'.format(
                     aggregate_route= route_digest(self.hazardous_routes), resort=self.name, date=earliest_date(self.dates)) 

        else:  
            return 'I70 is OPEN, and unaffected by weather. This affects {resort}. Calculated on {date}.'.format(
                    resort=self.name, date=earliest_date(dates))

def route_digest(route_names):
    first = route_names[0].split('-')[0]
    last = route_names[-1].split('-')[1]
    return '{0} and {1}'.format(first, last)

def earliest_date(dates):
    earliest = dates[0]
    for date in dates:
        if date < earliest:
            earliest = date

    return earliest.strftime('%m/%d @ %I:%M %p')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', type=bool, default=False)
    args = parser.parse_args() 
    raw = gather_observed_routes(args.live)

    vail = Resort('Vail', VAIL_ROUTES, raw) 
    breck = Resort('Breckenridge', COPPER_BRECK_ROUTES, raw) 
    arapahoe_basin = Resort('Araphaoe Basin', KEYSTONE_ABASIN_ROUTES, raw) 

    print(vail.generate_message())
    print(breck.generate_message())
    print(arapahoe_basin.generate_message())

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


if __name__ == '__main__':
    main()

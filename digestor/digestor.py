import requests
import urllib
from datetime import datetime
import redis
import hashlib
import os
import logging


ROAD_CONDITIONS = {
        11 : 'No Data',
        10 : 'Error',
        9 : 'Dryness',
        8 : 'Wetness',
        7 : 'High Wind',
        6 : 'Poor Visibility',
        5 : 'Snow',
        4 : 'Ice',
        3 : 'Blowing Snow',
        1 : 'Closed',
}

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

cache = None 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Resort:

    def __init__(self, name, watched_routes, raw_routes):
        self.name = name
        self.watched_routes = watched_routes
        self.raw_routes = raw_routes
        
        self.closed_routes = []
        self.hazardous_routes = []
        self.dates = []

        self.hazards = set([])

        for route in self.raw_routes:
            if int(route['rc:WeatherRouteId']) in self.watched_routes:
                route_state = {
                        'id' : int(route['rc:WeatherRouteId']),
                        'route_name' : route['rc:RouteName'],
                        'date' : datetime.strptime(route['rc:CalculatedDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                        # included for extra protection with closures
                        'condition' : route['rc:RoadConditionCategoryTxt'],
                        'condition_code' : float(route['rc:RoadConditionCategoryCd']),
                        'hazardous' : bool(route['rc:IsHazardousCondition']),
                        }
                if route_state['condition_code'] == 10 or route_state['condition_code'] == None:
                    logger.error('CDOT route code has an error.')

                self.dates.append(route_state['date'])

                if route_state['condition'] == 'Closed' or route_state['condition_code'] == 1:
                    self.closed_routes.append(route_state['route_name']) 
                
                # TODO Can a route ever be dry and dangerous?
                elif route_state['hazardous'] and route_state['condition_code'] != 9:
                    self.hazardous_routes.append(route_state['route_name'])    
                    self.hazards.add(ROAD_CONDITIONS.get(route_state['condition_code'],''))

        self.generate_message()

    def generate_message(self):
        if len(self.closed_routes) != 0:
            message = 'I70 is CLOSED between {aggregate_route}. This affects {resort} resort. Calculated on {date}.'.format(
                    aggregate_route= route_summarizer(self.closed_routes), resort=self.name, date=earliest_date(self.dates)) 
        
        elif len(self.hazardous_routes) != 0:
            message = 'I70 is OPEN, but is being impacted by {hazards} from {aggregate_route}. This affects {resort} resort. Calculated on {date}.'.format(
                     hazards= ', '.join(self.hazards), aggregate_route= route_summarizer(self.hazardous_routes), resort=self.name, date=earliest_date(self.dates)) 

        else:  
            message = 'I70 is OPEN, and unaffected by weather. This affects {resort} resort. Calculated on {date}.'.format(
                    resort=self.name, date=earliest_date(self.dates))
        
        print('{} - {}'.format(self.name, message))
        cache.set(self.name, message)


def route_summarizer(route_names):
    first = route_names[0].split('-')[0]
    last = route_names[-1].split('-')[1]
    return '{0} to {1}'.format(first, last)

def earliest_date(dates):
    earliest = dates[0]
    for date in dates:
        if date < earliest:
            earliest = date

    return earliest.strftime('%m/%d @ %I:%M %p')


def gather_observed_routes(local):
    """
    Gathers and reurns an array of parsed route dictionaries based on route_ids.
    """
 
    observed_routes = []
    if local:
        print('GATHERING_LOCAL')
        import xmltodict
        weather_routes = xmltodict.parse(
                open('../schema/road_conditions.xml', 'r').read())
    
    else: 
        username = os.getenv('username')
        password = os.getenv('password')

        url = 'https://{0}:{1}@data.cotrip.org/xml/road_conditions.xml'.format(
                username, urllib.quote(password, safe=''))
    
        r = requests.get(url) 
        if not content_update(r.content):
            return []
        import xmltodict
        weather_routes = xmltodict.parse(r.content) 
 
    for route in weather_routes['rc:RoadConditionsDetails']['rc:WeatherRoute']:
        if route['rc:WeatherRouteId'] in OBSERVED_ROUTE_IDS:
            observed_routes.append(route)

    return observed_routes

def content_update(content):
    new_hash = hashlib.sha224(content).hexdigest()
    old_hash = cache.get('hash')

    if old_hash == new_hash: 
        logger.info('no update.')
        return False
    
    else:
        logger.info('new: ' + new_hash)
        cache.set('hash', new_hash)
        return True


def handler(event, context, local=False):

    global cache
    cache = redis.StrictRedis(host=os.getenv('hostname'), port=int(os.getenv('port')), db=0)
    
    raw = gather_observed_routes(local)

    if raw == []: 
        return 'No update.'

    Resort('Vail', VAIL_ROUTES, raw) 
    
    Resort('Copper Mountain', COPPER_BRECK_ROUTES, raw)
    Resort('Breckenridge', COPPER_BRECK_ROUTES, raw) 

    Resort('Keystone', KEYSTONE_ABASIN_ROUTES, raw) 
    Resort('Arapahoe Basin', KEYSTONE_ABASIN_ROUTES, raw) 
    
    return 'Data updated.'

if __name__ == '__main__': 
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', default=False)
    args = parser.parse_args() 
    handler(None, None, args.local)


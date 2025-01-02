"""
Concept:

* call this script (which queries the forro-app.com) daily in a pythonanywhere task
* save result in a database
* use this database later to create a festivals.html
* then, reload the app with an updated festivals.html
"""


from datetime import datetime
import requests

from forro_festivals.scripts.event import Event


def get_api_url():
    """Creates the url of the forro-app.com API used to gather the festival data"""

    # Note: the request can return 'next'. We ignore this currently because the festival
    #       count returned is smaller than 30 at the time of this writing and navigating through
    #       all results is not yet necessary
    base_url = 'https://service.filora.eu/api/events'
    filter_tags = '5155a1d1-bdc8-4436-ad04-467fb27ccbae'
    date_filter = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
    return f'{base_url}/?filter_tags={filter_tags}&filter_domain=forró&filter_start_date_gt={date_filter}&ordering=start_date'


def parse_forro_app_single_item(event: dict):
    try:
        city = event['location'][0]['data']['localityLongName']
    except KeyError as e:
        city = event['location'][0]['data'].get('routeLongName', None)

    owner_id = event['location'][0]['owner_id']
    link = f'https://service.filora.eu/plugin/event/{owner_id}?style=card&backgroundColor=ffffff&filter_tags=5155a1d1-bdc8-4436-ad04-467fb27ccbae&filter_domain=forr%C3%B3'

    return {
        # Note(fe): The [:10] just assumes the date is in 'yyyy-mm-dd'
        'date_start': event['start_date'][:10],
        'date_end': event['end_date'][:10],
        'city': city,
        'country': event['location'][0]['data']['countryLongName'],
        'organizer': event['host_details']['username'],
        'uuid': event['uuid'],
        'link': link,
        'link_text': event['name'],
    }

def parse_forro_app_query(query):
    events = []
    if 'results' not in query:
         print(f'no "results" in {list(query.keys())}')
         return events
    for i, event_data in enumerate(query['results']):
        try:
            event_dict = parse_forro_app_single_item(event_data)
            if event_dict:
                event_dict['source'] = 'automatic'  # This script created that entry
                event = Event(**event_dict)
                events.append(event)
        except Exception as e:
            print(f'could not parse {event_data}.\n\nreason:\n{e}')
    return events

def get_forro_app_events():
    url = get_api_url()
    request = requests.get(url)
    events = parse_forro_app_query(request.json())
    return events


if __name__ == '__main__':
    url = get_api_url()
    request = requests.get(url)
    events = parse_forro_app_query(request.json())

    for event in events:
        print(event)


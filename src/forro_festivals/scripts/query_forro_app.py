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
    today = datetime.today().strftime('%y-%m-%d')
    return f'https://api.filora.eu/events/?filter_tags=5155a1d1-bdc8-4436-ad04-467fb27ccbae&filter_domain=forró&filter_start_date_gt={today}T23:00:44.277Z&ordering=start_date'


def parse_forro_app_single_item(event: dict):
    try:
        city = event['location'][0]['data']['localityLongName']
    except KeyError as e:
        city = event['location'][0]['data'].get('routeLongName', None)

    owner_id = event['location'][0]['owner_id']
    link = f'https://service.filora.eu/plugin/event/{owner_id}?style=card&backgroundColor=ffffff&filter_tags=5155a1d1-bdc8-4436-ad04-467fb27ccbae&filter_domain=forr%C3%B3'

    return {
        # Note(fe): The [:10] just assumes the date is in '%Y-%m-%d'
        'date_start': event['start_date'][:10],
        'date_end': event['end_date'][:10],
        'city': city,
        'country': event['location'][0]['data']['countryLongName'],
        'link_text': event['name'],
        'link': link
    }

def parse_forro_app_query(query):
    events = []
    if 'results' not in query:
         print(f'no "results" in {list(query.keys())}')
         return events
    for i, event_data in enumerate(query['results']):
        print(i)
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
    #query = requests.get(url)

    with open('response.json', 'r') as file:
        import json
        query = json.load(file)

    events = parse_forro_app_query(query)
    return events


if __name__ == '__main__':
    url = get_api_url()

    with open('response.json', 'r') as file:
        import json
        query = json.load(file)

    events = parse_forro_app_query(query)

    for event in events:
        print(event)


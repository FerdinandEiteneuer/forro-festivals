"""
Functionality for sending a notification to my phone via ntfy.sh
for an event which was manually added by a user.
"""

import requests
import json

from forro_festivals.models.event import Event

def event_to_message(event: Event):
    return f'Name: {event.link_text}\n' \
           f'City: {event.city}\n' \
           f'Date: {event.date_start} - {event.date_end}\n' \
           f'Link: {event.link}'

def post_event_to_ntfy_channel(event: Event, event_id: int, topic: str):
    view_link = {
        "action": "view",
        "label": "View Link",
        "url": event.link,
    }
    accept_festival = {
        "action": "view",
        "label": "Accept Event",
        "url": f"https://www.forro-festivals.com/update-event?id={event_id}&validated=true",
    }

    return requests.post("https://ntfy.sh/",
        data=json.dumps({
            "topic": topic,
            "title": "New Festival :-)",
            "message": event_to_message(event),
            "tags": ["tada"],
            "actions": [
                view_link,
                accept_festival,
            ]
        })
    )


def post_error_to_ntfy_channel(message, topic):
    return requests.post("https://ntfy.sh/",
        data=json.dumps({
            "topic": topic,
            "title": "Error",
            "message": message,
            "tags": ["rotating_light"],
        }))


if __name__ == '__main__':

    event = Event(
        date_start='2024-10-02',
        date_end='2024-10-06',
        city='Berlin',
        country='Germany',
        organizer='testor',
        link='https://www.example.com',
        link_text='Miudinho',
        source='tester',
    )

    #req = post_event_to_ntfy_channel(event=event)
    #print(req.status_code)
    #print(req.text)

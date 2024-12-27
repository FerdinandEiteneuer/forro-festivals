from pathlib import Path

from forro_festivals.scripts.db import DataBase
from forro_festivals.scripts.event import Event
import tempfile

# Note: Yes, tests are not clean atm since individual scenarios are not seperated at all.

def test_db():
    event_0 = Event(
        date_start='2024-10-02',
        date_end='2024-10-04',
        city='Cologne',
        country='Germany',
        organizer='event0orga',
        link='https://www.example.com',
        link_text='example',
        validated=True,
        source='testing',
    )
    event_1 = Event(
        date_start='2023-06-15',
        date_end='2023-06-18',
        city='Lissabon',
        country='Portugal',
        organizer='event1orga',
        link='https://www.example2.com',
        link_text='example2',
        validated=True,
        source='testing',
    )
    event_2 = Event(
        date_start='2021-04-25',
        date_end='2021-04-28',
        city='Berlin',
        country='Germany',
        organizer='event2orga',
        link='https://www.example2.com',
        link_text='FakeFestival',
        validated=False,
        source='testing',
    )

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        path = Path(temp_file.name)
        db = DataBase(path)

        db.create()
        db.insert_event(event_0)
        db.insert_event(event_0)  # duplicate which should not show up in db
        db.insert_event(event_1)
        db.insert_event(event_2)

        # Example usage
        events = db.get_all_events()

        assert len(events) == db.get_size() == 3

        assert events[0] == event_0
        assert events[1] == event_1
        assert events[2] == event_2

        db.delete_event_by_id(event_id=1)
        assert db.get_size() == 2

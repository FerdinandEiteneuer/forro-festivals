from pathlib import Path

from forro_festivals.scripts.db import DataBase
from forro_festivals.scripts.event import Event
import tempfile

# Note: Yes, tests are not clean since individual scenarios are not seperated at all.

def test_db():
    event_0 = Event(
        date_start='10-02-2024',
        date_end='12-02-2024',
        city='Cologne',
        country='Germany',
        link='https://www.example.com',
        link_text='example',
        source='testing',
    )
    event_1 = Event(
        date_start='11-06-2023',
        date_end='15-06-2023',
        city='Lissabon',
        country='Portugal',
        link='https://www.example2.com',
        link_text='example2',
        source='testing',
    )

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        path = Path(temp_file.name)
        db = DataBase(path)

        db.create()
        db.insert_event(event_0)
        db.insert_event(event_0)  # duplicate which should not show up in db
        db.insert_event(event_1)

        # Example usage
        events = db.get_all_events()

        assert len(events) == 2
        assert events[0] == event_0
        assert events[1] == event_1

        db.delete_event_by_id(event_id=1)
        assert len(db.get_all_events()) == 1

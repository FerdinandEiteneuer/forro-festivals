from pathlib import Path
from unittest.mock import patch

import pytest

from forro_festivals.scripts.user import User, Permissions
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
        organizer='event 0 orga',
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
        organizer='event 1 orga',
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
        organizer='event 2 orga',
        link='https://www.example2.com',
        link_text='FakeFestival',
        validated=False,
        source='testing',
    )

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        path = Path(temp_file.name)
        db = DataBase(path)

        db.create()
        event_id = db.insert(event_0)
        assert event_id == 1  # First id created

        assert event_0 == db.get_event_by_id(event_id=1)
        assert db.get_event_by_id(event_id=123) is None

        event_id = db.insert(event_0)  # duplicate which should not show up in db.
        assert event_id == 0  # Since this is a duplicated, 0 should be returned by insert_event
        # Note: the sqlite3 db did increase its id counter though!

        assert db.insert(event_1) == 3  # 3 because it's the third insertion event
        assert db.insert(event_2) == 4

        # Example usage
        events = db.get_all_events()

        assert len(events) == db.get_size() == 3
        assert events[0] == event_0
        assert events[1] == event_1
        assert events[2] == event_2

        partial_data = {'city': 'Changed City'}
        event_0 = Event.merge(event=event_0, partial_data=partial_data)
        db.update_by_id(id=1, obj=event_0)

        events = db.get_all_events()
        assert events[0].id == 1
        assert events[0].city == 'Changed City'

        db.delete_events_by_ids(event_ids=[1])
        assert db.get_size() == 2

        db.delete_events_by_ids(event_ids=[3, 4])
        assert db.get_size() == 0

        db.delete_events_by_ids(event_ids=[1234, 4321])
        assert db.get_size() == 0

@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        path = Path(temp_file.name)
        db = DataBase(path)
        db.create()
        yield db

@pytest.fixture
def permission_mock():
    with patch.object(Permissions, "values", return_value={'a', 'b', 'c'}):
        yield

def test_user(db, permission_mock):
    user = User(
        id='testuser@bla.com',
        permissions='a, b',
        hashed_pw='123',
    )

    db.insert(user)

    db_users = db.get_all(User)
    db_user = db.get_by_id('testuser@bla.com', User)
    assert user == db_users[0]
    assert user == db_user
    assert len(db_users) == 1

    updated_user = User(
        id='testuser@bla.com',
        permissions='a',  # remove a permission in comparison to 'user'
        hashed_pw='123',
    )

    db.update_by_id(updated_user.id, updated_user)
    db_user = db.get_by_id('testuser@bla.com', User)
    assert db_user.permissions == 'a'

    assert db.delete_by_id('testuser@bla.com', User) is True
    assert len(db.get_all(User)) == 0
    assert db.delete_by_id('not-existent', User) is False

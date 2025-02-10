from datetime import datetime

import pytest

from forro_festivals.models.event import Event


def test_event_creation():
    e = Event(
        date_start='2024-10-02',
        date_end='2024-10-06',
        city='Cologne',
        country='Germany',
        organizer='testor',
        link='https://www.example.com',
        link_text='example',
        source='tester',
        sold_out=False,
        validated=True,
    )

    assert e.city == 'Cologne'
    assert e.date_start == '2024-10-02'
    assert e.date_end == '2024-10-06'
    assert e.city == 'Cologne'
    assert e.country == 'Germany'
    assert e.organizer == 'testor'
    assert e.link == 'https://www.example.com'
    assert e.link_text == 'example'
    assert e.source == 'tester'
    assert e.sold_out is False
    assert e.validated is True
    # properties
    assert e.start == datetime(year=2024, month=10, day=2)
    assert e.end == datetime(year=2024, month=10, day=6)

    recreated_event = Event(**e.model_dump())
    assert recreated_event.model_dump() == e.model_dump()

@pytest.mark.parametrize(
    'event',
    [
        dict(
            date_start='10-02-2024',
            date_end='12-02-2024',
            city='Cologne',
            country='Germany',
            organizer='failbob',
            link='https://www.example.com',
            link_text='testomat',
            source='tester',
        ),
        dict(
            date_start='2024-02-12',
            date_end='2024-02-10',
            city='Cologne',
            country='Germany',
            organizer='failbob',
            link='https://www.example.com',
            link_text='testomat',
            source='tester',
        )
    ]
)
def test_validation_errors(event):
    with pytest.raises(ValueError):
        Event(**event)

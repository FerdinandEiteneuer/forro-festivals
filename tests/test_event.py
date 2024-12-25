import pytest

from forro_festivals.scripts.event import Event


def test_valid_event():
    e = Event(
        date_start='10-02-2024',
        date_end='12-02-2024',
        city='Cologne',
        country='Germany',
        link='https://www.example.com',
        link_text='example',
        source='tester',
    )

    assert e.city == 'Cologne'
    assert e.date_start == '10-02-2024'
    assert e.date_end == '12-02-2024'
    assert e.city == 'Cologne'
    assert e.country == 'Germany'
    assert e.link == 'https://www.example.com'
    assert e.link_text == 'example'
    assert e.source == 'tester'


@pytest.mark.parametrize(
    'event',
    [
        dict(
            date_start='10-02-2024-23',
            date_end='12-02-2024',
            city='Cologne',
            country='Germany',
            link='https://www.example.com',
            link_text='testomat',
            source='tester',
        ),
        dict(
            date_start='15-02-2024',
            date_end='12-02-2024',
            city='Cologne',
            country='Germany',
            link='https://www.example.com',
            link_text='testomat',
            source='tester',
        )
    ]
)
def test_validation_errors(event):
    with pytest.raises(ValueError):
        Event(**event)

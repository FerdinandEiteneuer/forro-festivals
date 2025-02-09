"""
Defines the basic object to hold the information about a Forro Festival
"""
from typing import Optional

import pydantic
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
import re
from datetime import datetime

from forro_festivals.config import DateFormats

def get_timestamp():
    return datetime.now().strftime(DateFormats.ymd_hms)

def transform_date(date, fmt_from, fmt_to):
    return datetime.strptime(date, fmt_from).strftime(fmt_to)

class Event(BaseModel):
    # Note: potentially, I can add a date for the start of the ticket sell
    id: int = -1  # coming from my database
    date_start: str
    date_end: str
    city: str
    country: str
    organizer: str
    uuid: str = 'None'  # coming from forro-app
    link: str
    link_text: str
    validated: bool = True
    source: str
    #date_next_lot: str = None
    #validated_next_lot: bool = False
    #date_
    sold_out: bool = False
    timestamp: str = Field(default_factory=get_timestamp)  # refers to object creation timestamp

    class Config:
        # Prevent modification of fields after instantiation.
        # Note: The way I use the database is to read from it and return Event objects.
        #       Therefore, they should better not be corrupted at any stage in my handling of them.
        frozen = True

    @staticmethod
    def sql_table():
        return 'events'

    @property
    def start(self):
        return datetime.strptime(self.date_start, DateFormats.ymd)

    @property
    def end(self):
        return datetime.strptime(self.date_end, DateFormats.ymd)

    @field_validator('date_start', 'date_end')
    def validate_start_end_dates(cls, value):
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, value):
            raise ValueError(f"'date' must be exactly of format 'yyyy-mm-dd', got '{value}'")
        return value

    # Root validator to compare date_end with date_start
    @model_validator(mode='after')
    def check_dates(cls, event):
        if event.start > event.end:
            raise ValueError(f"{event.date_end=}) must come after than {event.date_start=}")
        return event

    def to_tuple(self):
        model = self.model_dump()
        model.pop('id')
        return tuple(model.values())

    @property
    def sql_values(self):
        model = self.model_dump()
        model.pop('id')
        return tuple(model.values())

    @property
    def sql_insert_fields(self):
        fields = list(self.model_fields.keys())
        fields.remove('id')
        return fields

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False  #
        # Assume that no city ever has two festivals at the same weekend
        return (self.date_start == other.date_start and
                self.date_end == other.date_end and
                self.city == other.city and
                self.country == other.country
        )

    @classmethod
    def merge(cls, event: 'Event', partial_data: dict):
        # Important: Because the 'get_all_events' function from db.py immediately creates Event objects and returns them
        #            I write this function to ensure that if I want to update an event with the form data from the dashboard
        #            this essentially tests if the Event I want to put into the db is still working.
        #            History: I manually edited an event in the db to have date_end before date_start, saved this to db
        #            and then the dashboard was not usable anymore.
        event_data = event.model_dump()
        merged_data = {**event_data, **partial_data}  # Note: partial_data will overwrite event_data
        return cls(**merged_data)  # If merged data is inconsisted, we will raise here automatically and wont be able to use this


    @classmethod
    def from_request(cls, request):
        default_kwargs = dict(
            organizer='None',
            validated=False,
            source='add-festival',
        )
        kwargs = {
            key: value
            for key, value in request.form.items()
            if value != ''
        }
        kwargs = {**default_kwargs, **kwargs}
        return Event(**kwargs)

    @classmethod
    def from_db_row(cls, db_row):
        return cls(**db_row)

    @classmethod
    def get_default_event(cls):
        now = datetime.now().strftime(DateFormats.ymd)
        return cls(
            date_start=now,
            date_end=now,
            city='City',
            country='Country',
            organizer='None',
            link='https://www.example.com',
            link_text='Event Name',
            validated=False,
            source='add-festival',
        )

    @classmethod
    def human_readable_validation_error_explanation(cls, exc: pydantic.ValidationError):
        try:
            N_err = exc.error_count()
            error_or_errors = "error" if N_err == 1 else "errors"
            error_msg = f'Unfortunately, the data you submitted contained {N_err} {error_or_errors} :<br><ul>'
            translation_dict = {
                'link': 'Link',
                'link_text': 'Festival',
                'country': 'Country',
                'date_end': 'End Date',
                'date_start': 'Start Date',
                'city': 'City',
            }
            for err in exc.errors():
                if err['type'] == 'missing':
                    field = translation_dict[err['loc'][0]]
                    error_msg += f'<li>Missing Field: {field}</li>'
                elif err['type'] == 'value_error':
                    error_msg += f'<li>{err["msg"]}</li>'
            error_msg += '</ul>'
            return error_msg
        except Exception:
            return f'Error: {exc.errors()}'
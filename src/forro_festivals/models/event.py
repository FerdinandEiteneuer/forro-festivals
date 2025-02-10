"""
Defines the basic object to hold the information about a Forro Festival
"""

import pydantic
from pydantic import Field, field_validator, model_validator
import re
from datetime import datetime

from forro_festivals.config import DateFormats
from forro_festivals.models.base import BaseModel

def get_timestamp():
    return datetime.now().strftime(DateFormats.ymd_hms)

def transform_date(date, fmt_from, fmt_to):
    return datetime.strptime(date, fmt_from).strftime(fmt_to)

class Event(BaseModel):
    id: int = -1  # coming from my database
    date_start: str
    date_end: str
    city: str
    country: str
    organizer: str
    uuid: str = 'None'  # only important for events from forro app source
    link: str
    link_text: str
    validated: bool = True
    source: str
    # TODO(add date_next_lot) ...
    #date_next_lot: str = None
    sold_out: bool = False
    timestamp: str = Field(default_factory=get_timestamp)  # refers to object creation timestamp


    @staticmethod
    def sql_table():
        return 'events'

    @property
    def show(self):
        return self.validated == '1'

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
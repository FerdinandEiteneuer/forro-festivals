"""
Defines the basic object to hold the information about a Forro Festival
"""
import pydantic
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
import re
from datetime import datetime
from urllib.parse import urlparse

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
    timestamp: str = Field(default_factory=get_timestamp)  # refers to object creation timestamp

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

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False  #
        # Assume that no city ever has two festivals at the same weekend
        return (self.date_start == other.date_start and
                self.date_end == other.date_end and
                self.city == other.city and
                self.country == other.country
        )

    def update(self, event_data: dict):
        self.date_end = event_data.get('date_end', self.date_end)
        self.date_start = event_data.get('date_start', self.date_start)
        self.city = event_data.get('city', self.city)
        self.link = event_data.get('link', self.link)
        self.link_text = event_data.get('link_text', self.link_text)
        self.validated = bool(event_data.get('validated', self.validated))

    def to_html_string(self):
        link = self.link
        if urlparse(self.link).scheme == '':
            link = f'http://{link}'
        start = transform_date(self.date_start, fmt_from=DateFormats.ymd, fmt_to=DateFormats.dm)
        end = transform_date(self.date_end, fmt_from=DateFormats.ymd, fmt_to=DateFormats.dm)
        return f"[{self.city}, {self.country}] {start} \u2013 {end} | <a href='{link}'>{self.link_text}</a>"

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
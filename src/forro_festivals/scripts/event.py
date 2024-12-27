"""
Defines the basic object to hold the information about a Forro Festival
"""

from pydantic import BaseModel, Field, field_validator, model_validator
import re
from datetime import datetime

from forro_festivals.config import date_fmt_ymd_hms, date_fmt_ymd

def get_timestamp():
    return datetime.now().strftime(date_fmt_ymd_hms)

class Event(BaseModel):
    date_start: str
    date_end: str
    city: str
    country: str
    organizer: str
    link: str
    link_text: str
    validated: bool = True
    source: str
    timestamp: str = Field(default_factory=get_timestamp)  # refers to object creation timestamp

    @property
    def start(self):
        return datetime.strptime(self.date_start, date_fmt_ymd)

    @property
    def end(self):
        return datetime.strptime(self.date_end, date_fmt_ymd)

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
        return tuple(self.model_dump().values())
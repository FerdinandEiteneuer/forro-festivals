"""
Defines the basic object to hold the information about a Forro Festival
"""

from pydantic import BaseModel, field_validator, model_validator
import re
from datetime import datetime


class Event(BaseModel):
    date_start: str
    date_end: str
    city: str
    country: str
    link: str
    link_text: str
    source: str

    @field_validator('date_start', 'date_end')
    def validate_start_end_dates(cls, value):
        date_pattern = r'^\d{2}-\d{2}-\d{4}$'
        if not re.match(date_pattern, value):
            raise ValueError(f"'date' must be exactly 10 characters, got '{value}'")
        return value

    # Root validator to compare date_end with date_start
    @model_validator(mode='after')
    def check_dates(cls, event):
        date_format = "%d-%m-%Y"

        date_start = event.date_start
        date_end = event.date_end

        start = datetime.strptime(date_start, date_format)
        end = datetime.strptime(date_end, date_format)

        if end < start:
            raise ValueError(f"date_end ({date_end}) must be later than date_start ({date_start})")
        return event

    def to_tuple(self):
        return tuple(self.model_dump().values())
        #return self.date_start, self.date_end, self.city, self.country, self.link, self.link_text, self.source

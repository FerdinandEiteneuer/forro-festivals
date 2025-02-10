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


# TODO date validation and formats
class Suggestion(BaseModel):
    id: int = -1  # coming from db
    event_id: int = -1  # this is the event_id which this update suggestion corresponds to
    date_next_lot: str
    sold_out: bool
    applied: bool

    class Config:
        # Prevent modification of fields after instantiation.
        # Note: The way I use the database is to read from it and return Event objects.
        #       Therefore, they should better not be corrupted at any stage in my handling of them.
        frozen = True

    @staticmethod
    def sql_table():
        return 'suggestions'

    @property
    def next_lot(self):
        return datetime.strptime(self.date_next_lot, DateFormats.ymd)

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
        if not isinstance(other, Suggestion):
            return False
        return (self.event_id == other.event_id and
                self.date_next_lot == other.date_next_lot and
                self.sold_out == other.sold_out and
                self.applied == other.applied
        )

    @classmethod
    def merge(cls, suggestion: 'Suggestion', partial_data: dict):
        # Important: Because the 'get_all_events' function from db.py immediately creates Event objects and returns them
        #            I write this function to ensure that if I want to update an event with the form data from the dashboard
        #            this essentially tests if the Event I want to put into the db is still working.
        #            History: I manually edited an event in the db to have date_end before date_start, saved this to db
        #            and then the dashboard was not usable anymore.
        suggestion_data = suggestion.model_dump()
        merged_data = {**suggestion_data, **partial_data}  # Note: partial_data will overwrite event_data
        return cls(**merged_data)  # If merged data is inconsisted, we will raise here automatically and wont be able to use this


    #@classmethod
    #def from_request(cls, request):
    #    default_kwargs = dict(
    #        organizer='None',
    #        validated=False,
    #        source='add-festival',
    #    )
    #    kwargs = {
    #        key: value
    #        for key, value in request.form.items()
    #        if value != ''
    #    }
    #    kwargs = {**default_kwargs, **kwargs}
    #    return Suggestion(**kwargs)

    @classmethod
    def from_db_row(cls, db_row):
        return cls(**db_row)


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
"""
Defines the basic object to hold the information about a Forro Festival
"""
from typing import Optional

import pydantic
from pydantic import Field, field_validator, model_validator, ValidationError
import re
from datetime import datetime

from forro_festivals.config import DateFormats
from forro_festivals.models.base import BaseModel

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

    @staticmethod
    def sql_table():
        return 'suggestions'

    @property
    def next_lot(self):
        return datetime.strptime(self.date_next_lot, DateFormats.ymd)

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
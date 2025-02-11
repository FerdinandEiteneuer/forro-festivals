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
    date_next_lot: Optional[str] = None
    sold_out: Optional[bool] = False
    applied: bool = False

    @staticmethod
    def sql_table():
        return 'suggestions'

    @property
    def next_lot(self):
        return datetime.strptime(self.date_next_lot, DateFormats.ymd)

    @classmethod
    def from_request(cls, request):
        kwargs = dict(request.form)
        return cls(
            event_id=int(kwargs['event_id']),
            sold_out=kwargs['sold_out'] == 'True',
            date_next_lot=kwargs['date_next_lot'] if kwargs['date_next_lot'] != 'None' else None,
            applied=False
        )

    @classmethod
    def human_readable_validation_error_explanation(cls, exc: pydantic.ValidationError):
        pass

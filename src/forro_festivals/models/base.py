"""
Defines the basic object to hold the information about a Forro Festival
"""
import abc

import pydantic
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
import re
from datetime import datetime

from forro_festivals.config import DateFormats


class BaseModel(pydantic.BaseModel, abc.ABC):
    class Config:
        # Prevent modification of fields after instantiation.
        # Note: The way I use the database is to read from it and return Event objects.
        #       Therefore, they should better not be corrupted at any stage in my handling of them.
        frozen = True

    @staticmethod
    @abc.abstractmethod
    def sql_table():
        raise NotImplementedError

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
        if not isinstance(other, BaseModel):
            return NotImplemented  #

        return self.to_tuple() == other.to_tuple()

    @classmethod
    def merge(cls, obj: 'cls', partial_data: dict):
        # Important: Because the 'get_all_events' function from db.py immediately creates Event objects and returns them
        #            I write this function to ensure that if I want to update an event with the form data from the dashboard
        #            this essentially tests if the Event I want to put into the db is still working.
        #            History: I manually edited an event in the db to have date_end before date_start, saved this to db
        #            and then the dashboard was not usable anymore.
        obj_data = obj.model_dump()
        merged_data = {**obj_data, **partial_data}  # Note: partial_data will overwrite obj_data
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

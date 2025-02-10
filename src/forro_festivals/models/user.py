from enum import Enum

import flask_login
import pydantic

from forro_festivals.models.base import BaseModel


class Permissions(Enum):
    reload = 'reload'
    dashboard = 'dashboard'

    @classmethod
    def values(cls):
        return {perm.value for perm in cls}


class User(BaseModel, flask_login.UserMixin):  # Order of classes import for __eq__, since both implement it. I use the one from my BaseModel
    id: int = -1  # coming from database
    email: str
    permissions: str
    hashed_pw: str = None

    @pydantic.field_validator('permissions')
    def validate_permissions(cls, value):
        permission_set = cls.make_permission_set(value)
        if not permission_set.issubset(Permissions.values()):
            raise ValueError(f'invalid permissions: "{value}". {permission_set=}')
        return value

    @staticmethod
    def sql_table():
        return 'users'

    @staticmethod
    def make_permission_set(permissions):
        return set(permissions.replace(' ', '').split(','))

    @property
    def permission_set(self):
        return self.make_permission_set(self.permissions)
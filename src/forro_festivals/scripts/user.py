from enum import Enum

import flask_login
import pydantic

from forro_festivals.scripts.passwords import hash_password


class Permissions(Enum):
    reload = 'reload'
    dashboard = 'dashboard'

    @classmethod
    def values(cls):
        return {perm.value for perm in cls}


class User(flask_login.UserMixin, pydantic.BaseModel):
    id: str
    permissions: str
    hashed_pw: str = None

    @pydantic.field_validator('permissions')
    def validate_permissions(cls, value):
        permission_set = cls.make_permission_set(value)
        if not permission_set.issubset(Permissions.values()):
            raise ValueError(f'invalid permissions: "{value}". {permission_set=}')
        return value

    def to_tuple(self):
        return self.id, ','.join(self.permissions), self.hashed_pw

    @classmethod
    def from_db_row(cls, db_user):
        usr = dict(db_user)
        return cls(**usr)

    @staticmethod
    def sql_table():
        return 'users'

    @property
    def sql_insert_fields(self):
        return tuple(self.model_fields.keys())

    @property
    def sql_values(self):
        return tuple(self.model_dump().values())

    @staticmethod
    def make_permission_set(permissions):
        return set(permissions.replace(' ', '').split(','))

    @property
    def permission_set(self):
        return self.make_permission_set(self.permissions)
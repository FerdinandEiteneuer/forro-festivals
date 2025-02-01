import flask_login
import pydantic

class User(flask_login.UserMixin, pydantic.BaseModel):
    id: str
    permissions: str
    hashed_pw: str = None

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
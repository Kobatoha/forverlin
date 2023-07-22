from sqlalchemy import Column, Integer, VARCHAR, DATE
from .base import BaseModel
import datetime


class User(BaseModel):
    __tablename__ = 'users'

    user_id = Column(Integer, unique=True, nullable=False)

    username = Column(VARCHAR(32), unique=False, nullable=True)

    reg_date = Column(DATE, default=datetime.date.today())

    upd_date = Column(DATE, onupdate=datetime.date.today())

    def __str__(self) -> str:
        return f'<User:{self.user_id}>'



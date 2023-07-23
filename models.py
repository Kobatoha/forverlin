from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    wallet = Column(String, unique=True)
    transactions = relationship('Transactions', backref='user')


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    wallet = Column(String, ForeignKey('users.wallet'))
    transaction_id = Column(String)
    token_abbr = Column(String)
    count = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    date = Column(DATE, default=datetime.date.today())
    time = Column(TIME, default=datetime.datetime.now().time())
    send_message = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))

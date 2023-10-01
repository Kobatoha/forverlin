from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey, BigInteger
from DataBase.Base import Base
import datetime


class Transaction(Base):
    __tablename__ = 'transactions tron wallets'

    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, ForeignKey('wallets tron.wallet_address'))
    transaction_id = Column(String)
    token_abbr = Column(String)
    count = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    date = Column(DATE)
    time = Column(TIME)
    send_message = Column(Boolean, default=False)

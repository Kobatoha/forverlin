from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey, BigInteger
from DataBase.Base import Base
import datetime


class TrustedUser(Base):
    __tablename__ = 'trusted users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    wallet_address = Column(String, ForeignKey('watch wallets.wallet_address'))

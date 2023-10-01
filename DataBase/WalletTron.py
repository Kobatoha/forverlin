from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey, BigInteger
from DataBase.Base import Base
import datetime


class WalletTron(Base):
    __tablename__ = 'wallets tron'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    wallet_address = Column(String, unique=True)
    wallet_name = Column(String)
    only_watch = Column(Boolean, default=False)
    private_key = Column(String, unique=True)
    reg_date = Column(DATE, default=datetime.date.today())
    upd_date = Column(DATE, onupdate=datetime.date.today())

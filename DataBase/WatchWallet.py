from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey, BigInteger
from DataBase.Base import Base
import datetime


# Адреса, которые пользователь вводит самостоятельно и исключительно для мониторинга транзакций > 1 usdt
class WatchWallet(Base):
    __tablename__ = 'watch wallets'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String)

    wallet_address = Column(String, unique=True)
    wallet_name = Column(String)

    reg_date = Column(DATE, default=datetime.date.today())
    upd_date = Column(DATE, onupdate=datetime.date.today())

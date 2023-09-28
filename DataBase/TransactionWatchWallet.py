from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR, DATE, TIME, ForeignKey, BigInteger
from DataBase.Base import Base
import datetime


# Транзакции, которые относятся только к адресам WatchWallet
class TransactionWatchWallet(Base):
    __tablename__ = 'transactions watch wallets'

    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, ForeignKey('watch wallets.wallet_address'))
    transaction_id = Column(String)
    token_abbr = Column(String)
    count = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    date = Column(DATE)
    time = Column(TIME)
    send_message = Column(Boolean, default=False)

import schedule
from parser import main
import time
from main import send_transaction_info
import asyncio


async def run_schedule():
    schedule.every(1).minutes.do(main)
    schedule.every(1).minutes.do(send_transaction_info)
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run_schedule())
    await send_transaction_info()

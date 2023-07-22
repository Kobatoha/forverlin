from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, TELEGRAM_ID
from parser import main
import json
import datetime


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

tg_account = TELEGRAM_ID

@dp.message_handler(commands=['active'])
async def send_welcome(message: types.Message):
    global tg_account
    tg_account = message.from_user.id
    print(tg_account)

    await message.answer('Hello, your account activated')


@dp.message_handler()
async def send_transfer(message: types.Message):
    chat_id = tg_account
    with open('usdt.txt', 'r') as file:
        data = file.readlines()
        for line in data:
            transfer = json.loads(line)
            count = transfer['quant']
            valid = transfer['send_message']
            if valid is False:
                if count[-6:] == '000000':
                    count = count[:-9] + ',' + count[-9:-6]
                else:
                    count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]
                await message.answer(f"+{count} usdt in {transfer['time']}\n")



@dp.message_handler(commands=['usdt'])
async def send_usdt(message: types.Message):
    main()
    with open('usdt.txt', 'r') as file:
        data = file.readlines()
        for line in data:
            transfer = json.loads(line)
            count = transfer['quant']
            if count[-6:] == '000000':
                count = count[:-9] + ',' + count[-9:-6]
            else:
                count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]
            await message.answer(f"+{count} usdt in {transfer['time']}\n")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import asyncio
import json

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

with open('config.json') as file:
    data = json.load(file)
TOCKEN = data['TOCKEN']

# session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(TOCKEN)
dp = Dispatcher()
papa_chat = 2109964431


async def send_info_tg(message):
    await bot.send_message(papa_chat, str(message))


def send_info(message):
    asyncio.run(send_info_tg(message))


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Hello, {message.from_user.first_name}", reply_markup=main_kb)
    await bot.send_message(papa_chat, str(message.text))


@dp.message()
async def other(message: Message):
    if papa_chat != message.chat.id:
        await bot.send_message(papa_chat, f"{message} \n@{message.from_user.username}")
    pass


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    send_info('datadatadata')

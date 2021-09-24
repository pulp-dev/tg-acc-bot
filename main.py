import asyncio

import config
import menu_texts
import get_phone_number_script
from get_phone_number_script import Payment, Confirmations
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.__token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    get_phone_number_script.reg_handlers(dp)

    @dp.message_handler(commands=["start", "confirm"])
    async def cmd_start(message: types.Message):
        if message.text == '/confirm' and message.chat.id == config.__admin_id:
            await message.answer('Телефон пользователя')
            await Confirmations.waiting_for_verifiable_users_phone_num.set()
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Правила пользования", "Получить аккаунт", "Поддержка"]
        keyboard.add(*buttons)
        await message.answer(menu_texts.__greeting)

    @dp.message_handler(Text(equals="Поддержка"))
    async def send_support_info(message: types.Message):
        await message.reply('По любому вопросу, вы можете обратиться в нашу поддержку 🥰🥰:\n'
                            'https://t.me/pulpich')

    @dp.message_handler(Text(equals="Получить аккаунт"))
    async def reply_for_ask(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Global Elite"]
        keyboard.add(*buttons)
        await message.reply('Выберите звание', reply_markup=keyboard)

    @dp.message_handler(lambda message: message.text == "Global Elite")
    async def from_who(message: types.Message):
        await message.reply('Сообщите номер с которого будет производиться оплата (ввод без пробелов, только цифры)',
                            reply_markup=types.ReplyKeyboardRemove())
        await Payment.waiting_for_phone_number.set()

    @dp.message_handler(Text(equals="Правила пользования"))
    async def send_rules(message: types.Message):
        await message.answer(menu_texts.__rules, parse_mode=types.ParseMode.HTML)

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())

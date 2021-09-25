import asyncio

import admin_operations
import config
import menu_texts
import get_phone_number_script
from get_phone_number_script import Payment, Confirmations
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


def account_existence():
    for i in config.accounts:
        if config.accounts[i][0]:
            return True


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.__token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    get_phone_number_script.reg_handlers(dp)
    admin_operations.reg_admin_handlers(dp)

    @dp.message_handler(commands=["start", "confirm", "add_account"])
    async def cmd_start(message: types.Message):
        if message.text == '/add_account' and message.chat.id == config.__admin_id:
            admin = admin_operations.Admin(config.__admin_id, bot)
            await admin.add_account_com()
            return
        if message.text == '/confirm' and message.chat.id == config.__admin_id:
            await message.answer('Телефон пользователя')
            await Confirmations.waiting_for_verifiable_users_phone_num.set()
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Правила пользования", "Получить аккаунт", "Поддержка"]
        keyboard.add(*buttons)
        await message.answer(menu_texts.__greeting, reply_markup=keyboard)

    @dp.message_handler(Text(equals="Поддержка"))
    async def send_support_info(message: types.Message):
        await message.answer('По любому вопросу, вы можете обратиться в нашу поддержку 🥰🥰:\n'
                             'https://t.me/pulpich')

    @dp.message_handler(Text(equals="Получить аккаунт"))
    async def reply_for_ask(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Global Elite"]
        keyboard.add(*buttons)
        await message.reply('Выберите звание', reply_markup=keyboard)

    @dp.message_handler(lambda message: message.text == "Global Elite")
    async def possibility(message: types.Message):
        if not account_existence():
            await message.answer('В настоящий момент, к сожалению, нет свободных аккаунтов. Попробуйте позже.')
            return
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Оплатить"]
        keyboard.add(*buttons)
        await message.answer(
            '🔺 Стоимость одного аккаунта 100₽ \n\n'
            '🔺 Размер залога - 500₽ (возврат залога происходит сразу же по истечению срока аренды)\n\n'
            '🔺 Оплата производится переводом на Qiwi или Сбербанк',
            reply_markup=keyboard
        )

    # выбор способа оплаты
    @dp.message_handler(lambda message: message.text == 'Оплатить')
    async def choose_payment_variant(message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Qiwi', callback_data="Qiwi"),
                     types.InlineKeyboardButton(text='Сбербанк', callback_data="sber"))
        await message.answer("Выберете способ оплаты💳", reply_markup=keyboard)

    @dp.callback_query_handler(text='sber')
    async def from_who(call: types.CallbackQuery):
        await call.message.answer('Сообщите номер с которого будет производиться оплата (ввод без пробелов, '
                                  'только цифры)',
                                  reply_markup=types.ReplyKeyboardRemove())
        await Payment.waiting_for_phone_number.set()

    @dp.message_handler(Text(equals="Правила пользования"))
    async def send_rules(message: types.Message):
        await message.answer(menu_texts.__rules, parse_mode=types.ParseMode.HTML)

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())

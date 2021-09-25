from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import json


class Payment(StatesGroup):
    waiting_for_phone_number = State()


class Confirmations(StatesGroup):
    waiting_for_verifiable_users_phone_num = State()


def free_account_search():
    for i in config.accounts:
        if config.accounts[i][0]:
            login = i
            password = config.accounts[i][1]
            config.accounts[i][0] = False

            with open('accounts.json', 'w') as file:
                json.dump(config.accounts, file)

            return login, password


async def verify_user(message: types.message, state: FSMContext, bot=Bot(token=config.__token)):
    await state.update_data(user_phone_num=message.text)
    number = await state.get_data()
    try:
        await bot.send_message(config.users_phone_numbers[number['user_phone_num']],
                               'Спасибо за ожидание.\nВаш перевод подтвержден!')
        login, password = free_account_search()
        await bot.send_message(config.users_phone_numbers[number['user_phone_num']],
                               f'Высылаю ваш аккаунт ->\nlogin: {login}\npassword: {password}')
        await bot.send_message(config.users_phone_numbers[number['user_phone_num']], 'Приятного пользования!')
        config.users_phone_numbers.pop(number['user_phone_num'])
        await state.finish()
    except:
        await bot.send_message(config.__admin_id, 'Несуществующий номер')


async def get_phone_number(message: types.Message, state: FSMContext, bot=Bot(token=config.__token)):
    try:
        print(int(message.text))
    except:
        await message.answer("Неверно введен номер телефона")
        return
    if len(message.text) != 11 or message.text[0] != '8':
        await message.answer("Неверно введен номер телефона")
        return
    await message.reply('Поддтверждение перевода займет пару минут')
    await state.update_data(phone_number=message.text)
    user_data = await state.get_data()
    config.users_phone_numbers[user_data['phone_number']] = message.chat.id
    await bot.send_message(config.__admin_id, user_data['phone_number'])
    await state.finish()


def reg_handlers(dp: Dispatcher):
    dp.register_message_handler(get_phone_number, state=Payment.waiting_for_phone_number)
    dp.register_message_handler(verify_user, state=Confirmations.waiting_for_verifiable_users_phone_num)

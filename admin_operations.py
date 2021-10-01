from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

import config
from get_phone_number_script import Confirmations

bot = Bot(token=config.__token)


class StatesWhichAdminsCommandsNeed(StatesGroup):
    waiting_for_login_and_password = State()


class Admin:

    def __init__(self, admins_id, bot):
        self.admins_id = admins_id
        self.bot = bot

    async def add_account_com(self):
        await self.bot.send_message(self.admins_id, "Введите логин и пароль")
        await StatesWhichAdminsCommandsNeed.waiting_for_login_and_password.set()


async def add_account(message: types.message, state: FSMContext):
    await state.update_data(new_login_password=message.text)
    incomed_line = await state.get_data()
    login = incomed_line['new_login_password'].split()[0]
    password = incomed_line['new_login_password'].split()[1]
    config.accounts[login] = [True, password]
    await bot.send_message(config.__admin_id, f"Создан новый аккаунт: {login}: {password}")
    await state.finish()


async def cmd_confirm(message: types.message):
    await message.answer('Телефон пользователя')
    await Confirmations.waiting_for_verifiable_users_phone_num.set()


def reg_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(add_account, state=StatesWhichAdminsCommandsNeed.waiting_for_login_and_password)

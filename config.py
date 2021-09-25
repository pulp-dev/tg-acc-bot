import json

__token = '2038424042:AAFODfTh0WshcHKK7f7A9FIHiypyZndXV_w'
__admin_id = 838184521

# аккаунты: логин, свободность, пароль
with open('accounts.json', 'r') as file:
    accounts = json.load(file)

users_phone_numbers = {}
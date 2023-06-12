from aiogram import types, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from main import TOKEN

def create_currency_keyboard(currencies):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for currency in currencies:
        keyboard.add(types.KeyboardButton(currency))
    return keyboard


supported_currencies = ['RUB', 'MXN', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']

bot = Bot(token=TOKEN)
storage = MemoryStorage()
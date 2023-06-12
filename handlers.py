import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram import Dispatcher

from utils import create_currency_keyboard, supported_currencies, bot, storage
from main import c
from forex_python.converter import RatesNotAvailableError

dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
      Обработчик команды /start. Отправляет приветственное сообщение и клавиатуру с доступными командами.

      Args:
          message: Объект types.Message с информацией о сообщении.

      Returns:
          None
      """
    logging.info('Команда start')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_exchange = types.KeyboardButton('/exchange')
    button_calculator = types.KeyboardButton('/calculator')
    button_help = types.KeyboardButton('/help')
    keyboard.add(button_exchange, button_calculator, button_help)
    await message.reply("Привет! Я бот, который предоставляет информацию о курсе обмена валюты.",
                        reply_markup=keyboard)


@dp.message_handler(commands=['exchange'])
async def get_exchange_rate(message: types.Message, state: FSMContext):
    """
        Обработчик команды /exchange. Запускает процесс получения курса обмена валюты.

        Args:
            message: Объект types.Message с информацией о сообщении.
            state: Объект FSMContext для работы с состоянием бота.

        Returns:
            None
        """
    logging.info('Команда exchange')
    await message.reply("Выберите базовую валюту:", reply_markup=create_currency_keyboard(supported_currencies))

    await state.set_state('base_currency')


@dp.message_handler(state='base_currency')
async def process_base_currency(message: types.Message, state: FSMContext):
    """
    Обработчик выбора базовой валюты при получении курса обмена валюты.

    Args:
        message: Объект types.Message с информацией о сообщении.
        state: Объект FSMContext для работы с состоянием бота.

    Returns:
        None
    """
    await state.update_data(base_currency=message.text)

    await message.reply("Выберите целевую валюту:", reply_markup=create_currency_keyboard(supported_currencies))

    await state.set_state('target_currency')


@dp.message_handler(state='target_currency')
async def process_target_currency(message: types.Message, state: FSMContext):
    """
     Обработчик выбора целевой валюты при получении курса обмена валюты.

     Args:
         message: Объект types.Message с информацией о сообщении.
         state: Объект FSMContext для работы с состоянием бота.

     Returns:
         None
     """
    await state.update_data(target_currency=message.text)

    data = await state.get_data()
    base_currency = data['base_currency']
    target_currency = data['target_currency']

    try:
        rate = c.get_rate(base_currency, target_currency)
        rounded_rate = round(rate, 3)

        await message.reply(f"Текущий курс обмена: 1 {base_currency} = {rounded_rate} {target_currency}")

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_next_exchange = types.KeyboardButton('/exchange')
        button_calculator = types.KeyboardButton('/calculator')
        keyboard.add(button_next_exchange, button_calculator)
        await message.reply("Выберите действие:", reply_markup=keyboard)

        await state.reset_state()

    except RatesNotAvailableError:
        await message.reply("К сожалению, в данный момент не доступны курсы обмена.")

    except Exception as e:
        await message.reply(f"Произошла ошибка при получении курса обмена: {str(e)}")

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_next_exchange = types.KeyboardButton('/exchange')
        button_calculator = types.KeyboardButton('/calculator')
        keyboard.add(button_next_exchange, button_calculator)
        await message.reply("Выберите действие:", reply_markup=keyboard)

        await state.reset_state()


@dp.message_handler(Command("calculator"))
async def start_calculator(message: types.Message, state: FSMContext):
    logging.info('Команда calculator')
    await message.reply("Выберите базовую валюту:", reply_markup=create_currency_keyboard(supported_currencies))

    await state.set_state('calculator_base_currency')


@dp.message_handler(state='calculator_base_currency')
async def process_calculator_base_currency(message: types.Message, state: FSMContext):
    await state.update_data(calculator_base_currency=message.text)

    await message.reply("Введите количество базовой валюты:")

    await state.set_state('calculator_amount')


@dp.message_handler(state='calculator_amount')
async def process_calculator_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    calculator_base_currency = data['calculator_base_currency']

    await state.update_data(calculator_amount=float(message.text), calculator_base_currency=calculator_base_currency)

    await message.reply("Выберите целевую валюту:", reply_markup=create_currency_keyboard(supported_currencies))

    await state.set_state('calculator_target_currency')


@dp.message_handler(state='calculator_target_currency')
async def process_calculator_target_currency(message: types.Message, state: FSMContext):
    data = await state.get_data()
    calculator_base_currency = data['calculator_base_currency']
    calculator_amount = data['calculator_amount']
    calculator_target_currency = message.text

    try:
        rate = c.get_rate(calculator_base_currency, calculator_target_currency)
        target_amount = round(calculator_amount * rate, 2)

        await message.reply(f"Результат: {calculator_amount} {calculator_base_currency} = {target_amount} {calculator_target_currency}")

        await state.reset_state()

    except RatesNotAvailableError:
        await message.reply("К сожалению, в данный момент не доступны курсы обмена.")

    except Exception as e:
        await message.reply(f"Произошла ошибка при вычислении: {str(e)}")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_next_exchange = types.KeyboardButton('/exchange')
    button_calculator = types.KeyboardButton('/calculator')
    keyboard.add(button_next_exchange, button_calculator)
    await message.reply("Выберите действие:", reply_markup=keyboard)


@dp.message_handler(Command("help"))
async def get_help(message: types.Message):
    logging.info('Команда help')
    await message.reply("Это бот, который предоставляет информацию о курсе обмена валюты.\n"
                        "Чтобы узнать курс обмена, введите команду /exchange и выберите базовую и целевую валюту.\n"
                        "Чтобы воспользоваться калькулятором, введите команду /calculator и следуйте инструкциям.\n"
                        "Для получения этой справки снова, используйте команду /help.")

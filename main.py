import logging

from forex_python.converter import CurrencyRates, CurrencyCodes

TOKEN = '6048892911:AAGiuXg7PVXo9BsxhDtx_k_nRvej7rQ4Mxw'

c = CurrencyRates()
codes = CurrencyCodes()

if __name__ == '__main__':
    from handlers import dp
    logging.basicConfig(level=logging.INFO)
    logging.info('Запуск')
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

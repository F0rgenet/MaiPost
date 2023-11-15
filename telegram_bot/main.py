from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
from aiogram.exceptions import TelegramUnauthorizedError
from telegram_bot.database import register_models
from .handlers import router as handlers_router
import os


async def on_startup(dispatcher: Dispatcher):
	register_models()
	dispatcher.include_router(handlers_router)
	logger.info("Бот запущен")


async def startup():
	fsm_storage = MemoryStorage()
	dispatcher = Dispatcher(storage=fsm_storage)
	dispatcher.startup.register(on_startup)
	try:
		bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"), parse_mode="HTML")
		await dispatcher.start_polling(bot)
	except (TokenValidationError, TelegramUnauthorizedError):
		logger.warning("Токен некорректен")

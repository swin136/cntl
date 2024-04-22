import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

from handlers import router

from config import BOT_TOKEN
from config import USER_TLG_ID

from app_text import AFTER_REBOOT_MSG


async def main():
    # старая версия - на эту строчку вываливается Warning
    # bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Отправляем приветсвенное сообщение о начале работы бота
    await bot.send_message(USER_TLG_ID, AFTER_REBOOT_MSG)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
   

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
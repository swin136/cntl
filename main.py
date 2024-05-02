import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

from handlers import router
from handlers import bot_start_handler, bot_stop_handler


from config_settings import bot_settings


async def main():
    # старая версия - на эту строчку вываливается Warning
    # bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot = Bot(token=bot_settings.bots.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
           
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Регистрируем на диспетчере обработчики событий старта/оставновки бота
    dp.startup.register(bot_start_handler)
    dp.shutdown.register(bot_stop_handler)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
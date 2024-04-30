import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

from handlers import router
from handlers import shutdown_handler

from config import BOT_TOKEN
from config import USER_TLG_IDS

from app_text import AFTER_REBOOT_MSG, AFTER_POWER_ON_OFF_MSG
from app_text import OS_SEMAPHOR_CREATE, FIRST_LAUNCH_FILE 


async def main():
    # старая версия - на эту строчку вываливается Warning
    # bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Работа с файлом-семафором
    first_run = True
    if not os.path.isfile(FIRST_LAUNCH_FILE):
        process = await asyncio.create_subprocess_shell(OS_SEMAPHOR_CREATE)
        await process.communicate()
        first_run = False

    # Отправляем приветсвенное сообщение о начале работы бота
    for item in USER_TLG_IDS:
        try:
            await bot.send_message(item, AFTER_REBOOT_MSG)
            if not first_run:
                # Оповещаем о первом запуске платы
                await bot.send_message(item, AFTER_POWER_ON_OFF_MSG)
        except TelegramBadRequest:
            continue
        
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.shutdown.register(shutdown_handler)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
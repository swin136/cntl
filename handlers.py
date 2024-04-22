from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

from config import USER_TLG_ID

import os
import asyncio

from app_text import SYSTEM_REBOOT_CMD
from app_text import HELLO_MSG, REBOOT_MSG, STATUS_ANSWER_MSG #, REBOOT_NO_MSG


router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(HELLO_MSG)


@router.message(Command("status"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(STATUS_ANSWER_MSG)
        await asyncio.sleep(10)
        await msg.answer('Данные ...')


@router.message(Command("reboot"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(REBOOT_MSG)
        os.system(SYSTEM_REBOOT_CMD)

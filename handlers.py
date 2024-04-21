from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

from config import USER_TLG_ID

import os
import asyncio

from app_text import SYSTEM_REBOOT_CMD


router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer("Привет! Добро пожаловать в бот-помощник для обслуживания точки доступа к 'МИС Барс'.")


@router.message(Command("status"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer('Отправляем данные о параметрах точки доступа к МИС "Барс".')
        await asyncio.sleep(10)
        await msg.answer('Данные ...')


@router.message(Command("reboot"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer('Отправляем сигнал на перезагрузку точки доступа МИС "Барс".')
        os.system(SYSTEM_REBOOT_CMD)
        


# @router.message()
# async def message_handler(msg: Message):
#     await msg.answer(f"Твой ID: {msg.from_user.id}")
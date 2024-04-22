from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

from config import USER_TLG_ID

import os
import asyncio
import aiofiles
import math

from app_text import SYSTEM_REBOOT_CMD
from app_text import HELLO_MSG, REBOOT_MSG, STATUS_ANSWER_MSG, MEM_INFO_FILE, THERMAL_FILE, UPTIME_INFO_FILE 
from app_text import NO_TEMP_FOUND

EMPTY_MSG = "NO_CONTENTS"

# Время удаления сообщения
TIME_DELETE = 50


router = Router()


async def delete_message(message: types.Message, second: int = 0):
    """
    Удалят сообщение из чата Телеграмма
    :param message:
    :param second:
    :return:
    """
    await asyncio.sleep(second)
    await message.delete()


@router.message(Command("start"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(HELLO_MSG)


@router.message(Command("status"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(STATUS_ANSWER_MSG)
        await asyncio.sleep(5)
        # Получаем данные о расходовании памяти
        try:
            contents =[]
            memory_device = {}
            async with aiofiles.open(MEM_INFO_FILE, mode='r') as linux_file:
                async for line in linux_file:
                    contents.append(line)
                    record = line.strip().split(':')
                    if record[0] == "MemTotal":
                        memory_device['MemTotal'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'MemFree':
                        memory_device['MemFree'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'Buffers':
                        memory_device['Buffers'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'Cached':
                        memory_device['Cached'] = int(record[1].strip()[:-2].strip())

            # print(memory_device)
            # Расчитваем процент загрузки памяти
            used_memory_percent = round((memory_device['MemTotal'] - memory_device['MemFree'] - memory_device['Buffers'] - memory_device['Cached']) * 100 / memory_device['MemTotal'])
            memory_msg = f"Занято памяти: <b>{used_memory_percent}%</b> из <b>{memory_device['MemTotal'] / (1024 * 1024):.2f}</b> Гб"
        except FileNotFoundError:
            memory_msg = EMPTY_MSG
        # температура платы
        try:
            async with aiofiles.open(THERMAL_FILE, mode='r') as linux_file:
                contents = await linux_file.read()
        except FileNotFoundError:
            contents = EMPTY_MSG
        if contents == EMPTY_MSG:
            user_temp_msg = NO_TEMP_FOUND
        else:
            user_temp_msg = f"Температура ЦП: <b>{round(int(contents) / 1000)}°C</b>"
        # Время непрерывной работы
        try:
            async with aiofiles.open(UPTIME_INFO_FILE, mode='r') as linux_file:
                contents = await linux_file.read()
        except FileNotFoundError:
            contents = EMPTY_MSG
        if contents == EMPTY_MSG:
           system_timing_msg = NO_TEMP_FOUND
        else:
            system_timing = round(float(contents.split()[0]))
            if system_timing > 3600:
                hours = int(math.floor((system_timing) / 3600))
                minutes = int(math.floor((system_timing - (hours * 3600))/60))
                system_timing_msg = f"Время работы устройства: <b>{hours}</b> ч <b>{minutes}</b> мин."
            else:
                system_timing_msg = f"Время работы устройства: <b>{round(system_timing/60)}</b> мин."

        # Вывод сообщений
         # Отправлеям в едином сообщении время работы устройства, параметры использования памяти устройства, температуру процессора
        await msg.answer(system_timing_msg + '\n' + memory_msg + '\n' + user_temp_msg)

        # Информационной сообщение пользователю бота
        await msg.answer('Успешной работы!')
        # создаем задачу по удалению исходного сообщение
        asyncio.create_task(delete_message(msg, TIME_DELETE))

# Отправляем команду на перезагрузку
@router.message(Command("reboot"))
async def start_handler(msg: Message):
    if msg.from_user.id == USER_TLG_ID:
        await msg.answer(REBOOT_MSG)
        os.system(SYSTEM_REBOOT_CMD)

from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import aiohttp.client_exceptions

from config import USER_TLG_IDS

import os

import asyncio
import aiofiles
import aiohttp

import math

from app_text import SYSTEM_REBOOT_CMD
from app_text import HELLO_MSG, REBOOT_MSG, STATUS_ANSWER_MSG, MEM_INFO_FILE, THERMAL_FILE, UPTIME_INFO_FILE 
from app_text import NO_TEMP_FOUND, NET_DEVICE_CARRIER_FILE, SYSTEM_DOWN_NETWORK_CMD, LINK_OFF_MSG, LINK_ON_MSG, SYSTEM_UP_NETWORK_CMD 
from app_text import RESTORE_ROUTE

from kb import keyboard


EMPTY_MSG = "NO_CONTENTS"

# URL_WEB_Server
SOURCE_WEB_SERVER_URL = 'http://192.168.1.1'

# Задержка выполнения бота
APP_DELAY = 5

# aiohttp.client_exceptions.ClientConnectorError:

# Время удаления сообщения
TIME_DELETE = 50

from app_text import STATUS_BUTTON, REBOOT_BUTTON, CONNECT_TO_BARS, DISCONNET_FROM_BARS


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
    if msg.from_user.id in USER_TLG_IDS:
        # await msg.answer(HELLO_MSG)
        await msg.answer(HELLO_MSG, reply_markup=keyboard)
        

@router.message(Command("status"))
@router.message(F.text.lower() == STATUS_BUTTON.lower())
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        await msg.answer(STATUS_ANSWER_MSG)
        await asyncio.sleep(APP_DELAY)
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
            if  round(int(contents) / 1000) > 59:
                user_temp_msg = user_temp_msg + ' \U000026A0'
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

        # Параметры проводного интерфейса
        must_access__web_server = False
        try:
            async with aiofiles.open(NET_DEVICE_CARRIER_FILE, mode='r') as linux_file:
                contents = await linux_file.read()
                net_device_status_msg = 'Подключение к сети <I>МИС "БАРС"</I> : <b>АКТИВНО</b>'  #'\U000026A0'
                must_access__web_server = True
        except (FileNotFoundError, OSError):
            net_device_status_msg = 'Подключение к сети <I>МИС "БАРС"</I> : <b>ОТКЛЮЧЕНО </b>' + '\U0001F198'

        # await msg.answer(net_device_status_msg)

        # Вывод сообщений
        # Отправлеям в едином сообщении время работы устройства, параметры использования памяти устройства, температуру процессора
        # Состояние сетевого интерфейся для подключение к ГИС "БАРС"
        await msg.answer(system_timing_msg + '\n' + memory_msg + '\n' + user_temp_msg + '\n' + net_device_status_msg)

        # Тестируем доступ к веб-серверу при наличии инфомации об активном подключении
        if must_access__web_server:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(SOURCE_WEB_SERVER_URL) as response:
                        if response.status == 200:
                            await msg.answer('\U00002705' + f" Веб-сервер МИС Барс <b>ДОСТУПЕН!</b>!")
                        else:
                            await msg.answer('\U000026A0' + f" Пробелемы с доступом к веб-серверу <b>МИС Барс</b>!")
                        # await msg.answer(f"Статус ответа от веб-сервера {SOURCE_WEB_SERVER_URL}: {response.status}")
                except aiohttp.client_exceptions.ClientConnectionError:
                    await msg.answer('\U0001F534' + f" Веб-сервер МИС Барс <b>НЕДОСТУПЕН!</b>!")
       


        # Информационной сообщение пользователю бота
        await msg.answer('Успешной работы!')
        # создаем задачу по удалению исходного сообщение
        asyncio.create_task(delete_message(msg, TIME_DELETE))

async def change_net_interfase(cmd_to_change: str, msg: Message):
    """
    Функция изменяет состояние сетевого интерфейса (включат/выключает его)
    """
    # Отправляем команду на изменение проводного интерфейса
    process = await asyncio.create_subprocess_shell(cmd_to_change)
    await process.communicate()
    # Пауза - может убрать её ?????
    await asyncio.sleep(2)
    # восстанавливаем маршрутизацию
    if cmd_to_change == SYSTEM_UP_NETWORK_CMD:
        process = await asyncio.create_subprocess_shell(RESTORE_ROUTE)
        await process.communicate()


    # Скидываем флаг проверки доступа к веб-серверу в ЛВС
    must_access__web_server = False
     # Считываем параметры проводного интерфейса
    try:
        async with aiofiles.open(NET_DEVICE_CARRIER_FILE, mode='r') as linux_file:
            contents = await linux_file.read()
            net_device_status_msg = 'Подключение к сети <I>МИС "БАРС"</I> : <b>АКТИВНО</b>'  #'\U000026A0'
            # Подключение активно - взводим флаг проверки доступа к веб-серверу
            must_access__web_server = True
    except (FileNotFoundError, OSError):
        net_device_status_msg = 'Подключение к сети <I>МИС "БАРС"</I> : <b>ОТКЛЮЧЕНО </b>' + '\U0001F198'
    
    # Отправляям сообщение о результатх проверки состояния сетевого инттерфейса после включения/отключения
    await msg.answer(net_device_status_msg)

    # Тестируем доступ к веб-серверу при наличии информации об активном подключении
    if must_access__web_server:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(SOURCE_WEB_SERVER_URL) as response:
                    if response.status == 200:
                        await msg.answer('\U00002705' + f" Веб-сервер МИС Барс <b>ДОСТУПЕН!</b>!")
                    else:
                        # сервер доступен - но отвечает не то что надо - Status Code не равен 200
                        await msg.answer('\U000026A0' + f" Пробелемы с доступом к веб-серверу <b>МИС Барс</b>!")
            except aiohttp.client_exceptions.ClientConnectionError:
                # Не смоглм связаться с веб-сервером
                await msg.answer('\U0001F534' + f" Веб-сервер МИС Барс <b>НЕДОСТУПЕН!</b>!")


# Отправляем команду на ВЫКЛЮЧЕНИЕ проводного интерфейса
@router.message(Command("linkoff"))
@router.message(F.text.lower() == DISCONNET_FROM_BARS.lower())
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        # отправляем сообщению пользователе о начале операции по отключению 
        # сетевого интерфейса
        await msg.answer(LINK_OFF_MSG)
        # Вызываем функцию для смены состояния сетвого интерфейса
        await change_net_interfase(cmd_to_change=SYSTEM_DOWN_NETWORK_CMD, msg=msg)
       
        # создаем задачу по удалению исходного сообщение с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


# Отправляем команду на ВКЛЮЧЕНИЕ проводного интерфейса
@router.message(Command("linkon"))
@router.message(F.text.lower() == CONNECT_TO_BARS.lower())
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        # отправляем сообщению пользователе о начале операции по включению 
        # сетевого интерфейса
        await msg.answer(LINK_ON_MSG)
        # Вызываем функцию для смены состояния сетвого интерфейса
        await change_net_interfase(cmd_to_change=SYSTEM_UP_NETWORK_CMD, msg=msg)

        # создаем задачу по удалению исходного сообщение с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


# Отправляем команду на перезагрузку
@router.message(Command("reboot"))
@router.message(F.text.lower() == REBOOT_BUTTON.lower())
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        for item in USER_TLG_IDS:
            try:
                await msg.bot.send_message(item, REBOOT_MSG)
            except TelegramBadRequest:
                continue
        # await msg.answer(REBOOT_MSG)
        await asyncio.sleep(2)
        os.system(SYSTEM_REBOOT_CMD)

# Сообщаем команды бота
@router.message(Command("help"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        help_msg = "Команды бота помощника:\n/status - получить статус устройства\n" + "/reboot - перегрузить устройство\n"
        help_msg = help_msg + "/linkon - подключиться к МИС 'Барс'.\n/linkoff - отключиться от МИС 'Барс'\n"
        help_msg = help_msg + "/help - вывести справку по командам бота"
        await msg.answer(help_msg)
        # создаем задачу по удалению исходного сообщение с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


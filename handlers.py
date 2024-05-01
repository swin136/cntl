from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import aiohttp.client_exceptions

from config import USER_TLG_IDS

import os
import subprocess

import asyncio
import aiofiles
import aiohttp

import math

from app_text import SYSTEM_REBOOT_CMD
from app_text import HELLO_MSG, REBOOT_MSG, STATUS_ANSWER_MSG, MEM_INFO_FILE, THERMAL_FILE, UPTIME_INFO_FILE 
from app_text import NO_TEMP_FOUND, NET_DEVICE_CARRIER_FILE, SYSTEM_DOWN_NETWORK_CMD, LINK_OFF_MSG, LINK_ON_MSG, SYSTEM_UP_NETWORK_CMD 
from app_text import RESTORE_ROUTE, NO_INTERFACE_DATA, IP_LOG_FILE, ERROR_IP_LOG, GATEWAY_LOG_FILE 
from app_text import OS_RELEASE_INFO, OS_RELEASE_INFO, SHOW_CPU_INFO, KERNEL_VERSION_FILE, HOSTNAME_FILE, RELEASE_BOARD_FILE 
from app_text import OS_DF_INFO, ERROR_DEVICE_GET_DATA  
from app_text import STATUS_BUTTON, HELP_BUTTON, CONNECT_TO_BARS, DISCONNET_FROM_BARS
from app_text import SOURCE_WEB_SERVER_URL
from app_text import SEARCH_AUTUSSH_CMD, RUN_AUTUSSH_CMD, AUTO_SSH_FOUND_MSG, AUTO_SSH_NO_FOUND_MSG, AUTO_SSH_START_MSG  
from app_text import TEST_NETWORK_HOSTS
from app_text import START_NETWORK_TEST_MSG, STOP_BOT_MSG  

from app_utils import ping_host

from kb import keyboard


EMPTY_MSG = "NO_CONTENTS"

# Задержка выполнения бота
APP_DELAY = 5

# aiohttp.client_exceptions.ClientConnectorError:

# Время удаления сообщения
TIME_DELETE = 20

# Порог предупреждений по логам 
LEVEL_LOG_WARNING = 70

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
        await msg.answer(f"Привет, <b>{msg.from_user.first_name}</b>! {HELLO_MSG}", reply_markup=keyboard)
        # создаем задачу по удалению исходного сообщение
        asyncio.create_task(delete_message(msg, TIME_DELETE))
        

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

            # Расчитываем процент загрузки памяти
            used_memory_percent = round((memory_device['MemTotal'] - memory_device['MemFree'] - memory_device['Buffers'] - memory_device['Cached']) * 100 / memory_device['MemTotal'])
            memory_msg = f"Занято памяти: <b>{used_memory_percent}%</b> из <b>{memory_device['MemTotal'] / (1024 * 1024):.2f}</b> Гб"
            if used_memory_percent > 75:
                memory_msg = memory_msg + ' \U000026A0'
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
            if system_timing > 86_400:
                days = int(math.floor((system_timing) / 86_400))
                hours = int(math.floor((system_timing - days * 86_400) / 3_600))
                minutes = int(math.floor((system_timing - (days * 86_400) - (hours * 3_600))/60))
                system_timing_msg = f"Время работы устройства: <b>{days}</b> д <b>{hours}</b> ч <b>{minutes}</b> мин."
            elif system_timing > 3_600:
                hours = int(math.floor((system_timing) / 3600))
                minutes = int(math.floor((system_timing - (hours * 3600))/60))
                system_timing_msg = f"Время работы устройства: <b>{hours}</b> ч <b>{minutes}</b> мин."
            else:
                system_timing_msg = f"Время работы устройства: <b>{round(system_timing/60)}</b> мин."

            # system_timing = round(float(contents.split()[0]))
            # if system_timing > 3600:
            #     hours = int(math.floor((system_timing) / 3600))
            #     minutes = int(math.floor((system_timing - (hours * 3600))/60))
            #     system_timing_msg = f"Время работы устройства: <b>{hours}</b> ч <b>{minutes}</b> мин."
            # else:
            #     system_timing_msg = f"Время работы устройства: <b>{round(system_timing/60)}</b> мин."

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
                            await msg.answer('\U000026A0' + f" Проблемы с доступом к веб-серверу <b>МИС Барс</b>!")
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
    process = await asyncio.create_subprocess_shell(cmd_to_change, 
                                                    stdout=asyncio.subprocess.DEVNULL,
                                                    stderr=asyncio.subprocess.DEVNULL)
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
            await linux_file.read()
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
        # создаем задачу по удалению исходного сообщение
        asyncio.create_task(delete_message(msg, TIME_DELETE))

# Сообщаем команды бота
@router.message(Command("help"))
@router.message(F.text.lower() == HELP_BUTTON.lower())
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        help_msg = "Команды бота помощника:\n<b>/reboot</b> - <b><u>перегрузить устройство </u></b>" + "\U0001F198" + "\n"
        help_msg = help_msg + "<b>/status</b> - получить статус устройства\n"
        help_msg = help_msg + "<b>/linkon</b> - подключиться к МИС 'Барс'\n<b>/linkoff</b> - отключиться от МИС 'Барс'\n"
        help_msg = help_msg + "<b>/ssh_restart</b> - запуск/перезапуск SSH-клиента\n"
        help_msg = help_msg + "<b>/net_test</b> - тест соединения с Интернетом\n" 
        help_msg = help_msg + '<b>/addr</b> - данные по сетевым адресам устройства\n'
        help_msg = help_msg + '<b>/route</b> - таблица маршрутизации устройства\n'
        help_msg = help_msg + '<b>/lastip</b> - последний полученный ip-адрес по DHCP\n'
        help_msg = help_msg + '<b>/info</b> - информация об устройстве\n'
        help_msg = help_msg + "<b><I>/help</I></b> - вывести справку по командам бота"
        await msg.answer(help_msg)
        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))

# Выводим адреса устройства
@router.message(Command("addr"))
async def start_handler(msg: Message):
    show_interface_cmd = '/sbin/ifconfig'
    if msg.from_user.id in USER_TLG_IDS:
        interfaces = {'eth0': '', 
                      'wlan0': '',
                      }
        for interface in interfaces.keys():
            try:
                result = subprocess.run([show_interface_cmd, interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                interfaces[interface] = result.stdout.strip().split("\n")[1].split()[1]
            except IndexError:
                interfaces[interface] = NO_INTERFACE_DATA
        interfaces_msg = '<b>Данные по сетевым интерефейсам устройства</b>:\n'
        for interface in interfaces.keys():
            interfaces_msg = interfaces_msg + f"<u>{interface}</u>: {interfaces[interface]}\n"

        await msg.answer(interfaces_msg)
        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))

# Выводим сведения о маршрутизации устройства
@router.message(Command("route"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        result = subprocess.run(['/sbin/ip', 'r'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        route_msg = "<b>Таблица маршрутизации устройства:</b>\n"+result.stdout.strip()
        await msg.answer(route_msg)
        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


# Выводим сведения о последнем полученном ip-адресе
# проводным интефейсом через DHCP
@router.message(Command("lastip"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
            try:
                # Считываем данные о сетевых интерфейсах
                contents = []
                async with aiofiles.open(IP_LOG_FILE, mode='r') as linux_file:
                    async for line in linux_file:
                        contents.append(line)
                test_ip = contents[len(contents) - 1].strip().split()
                # print(test_ip)
                if test_ip[0] != 'inet' or test_ip[2] != 'netmask':
                    raise ValueError
                mgs_last_ip = "<b>Последняя запись о сетевом адресе, полученном от DHCP-сервера</b>:\n" 
                mgs_last_ip = mgs_last_ip + f'<u>ip-адрес</u>:{test_ip[1]}\n<u>сетевая маска</u>: {test_ip[3]}\n'

                # Добавляем в сообщение широковещательный адрес
                mgs_last_ip = mgs_last_ip + f'<u>Широковещательный адрес</u>: {test_ip[5]}\n'

                # Считываем данные о шлюзе
                contents = []
                async with aiofiles.open(GATEWAY_LOG_FILE, mode='r') as linux_file:
                    async for line in linux_file:
                        contents.append(line)

                test_gateway = contents[len(contents) - 1].strip().split()
                mgs_last_ip = mgs_last_ip + f'<u>сетевой шлюз</u>:{test_gateway[2]}'

                await msg.answer(mgs_last_ip) 
            except (FileNotFoundError, ValueError, IndexError):
                # Ошибка при получении данных ip-адресах
                await msg.answer(ERROR_IP_LOG)
            # создаем задачу по удалению исходного сообщения с командой
            asyncio.create_task(delete_message(msg, TIME_DELETE))

# Выводим сведения о устройстве
# UnboundLocalError
@router.message(Command("info"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        device_info_msg = "<b>Сведения об устройстве</b>:\n"
        # Считываем информацию оБ имени машины
        async with aiofiles.open(HOSTNAME_FILE, mode='r') as linux_file:
                contents = await linux_file.read()
        hostname_msg = f"Имя машины: <b>{contents.strip()}</b>\n"
        device_info_msg = device_info_msg + hostname_msg 

        try:
            # Время непрерывной работы
            async with aiofiles.open(UPTIME_INFO_FILE, mode='r') as linux_file:
                contents = await linux_file.read()

            system_timing = round(float(contents.split()[0]))
            if system_timing > 86_400:
                days = int(math.floor((system_timing) / 86_400))
                hours = int(math.floor((system_timing - days * 86_400) / 3600))
                minutes = int(math.floor((system_timing - (days * 86_400) - (hours * 3600))/60))
                system_timing_msg = f"Непрерывная работа: <b>{days}</b> д <b>{hours}</b> ч <b>{minutes}</b> мин.\n"
            elif system_timing > 3600:
                hours = int(math.floor((system_timing) / 3600))
                minutes = int(math.floor((system_timing - (hours * 3600))/60))
                system_timing_msg = f"Непрерывная работа: <b>{hours}</b> ч <b>{minutes}</b> мин.\n"
            else:
                system_timing_msg = f"Непрерывная работа: <b>{round(system_timing/60)}</b> мин.\n"

            device_info_msg =  device_info_msg + system_timing_msg    

            # Информация о релизе платы
            async with aiofiles.open(RELEASE_BOARD_FILE, mode='r') as linux_file:
                async for line in linux_file:
                    parms_list = line.strip().split("=")
                    if parms_list[0] == 'BOARD_NAME':
                        board_name = parms_list[1]
                        continue
                    elif parms_list[0] == 'VERSION':
                        verion_board =  parms_list[1]
                        continue
                    elif parms_list[0] == 'ARCH':                        
                        arch_board =  parms_list[1]
                        continue                        
                
            device_info_msg =  device_info_msg + f'Имя платы: <b>{board_name}</b>\n'
            device_info_msg =  device_info_msg + f'Версия платы: <b>{verion_board}</b>\n'
            device_info_msg =  device_info_msg + f"Архитектура: <b>{arch_board.upper()}</b>\n"


            # Считываем информацию о процессоре - команда lscpu
            result = subprocess.run([SHOW_CPU_INFO], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            cpu_info = result.stdout.strip().split("\n")
            for line in cpu_info:
                test_line = line.split(":")
                 # Архитектура ЦПУ
                if test_line[0].strip().lower() == 'architecture':
                        arch_type = f"Архитектура: <b>{test_line[1].strip().lower()}</b>\n"
                        continue
                # Количество ядер ЦПУ
                if test_line[0].strip().lower() == 'cpu(s)':
                        cpu_core_count = f"Количество ядер: <b>{test_line[1].strip().lower()}</b>\n"
                        continue
                # Модель ЦПУ
                if test_line[0].strip().lower() == 'model name':
                        model_name = f"Процессор: <b>{test_line[1].strip()}</b>\n"
                        continue
                # Минимальная частота ЦПУ
                if test_line[0].strip().lower() == 'CPU min MHz'.lower():
                        min_cpu_freq = f"Минимальная частота: <b>{test_line[1].strip().split(',')[0]} МГц</b>\n"
                        continue
                # Максимальная частота ЦПУ
                if test_line[0].strip().lower() == 'CPU max MHz'.lower():
                        max_cpu_freq = f"Максимальная частота: <b>{test_line[1].strip().split(',')[0]} МГц</b>\n"
                        continue
            device_info_msg =  device_info_msg + model_name + arch_type +  min_cpu_freq 
            device_info_msg = device_info_msg + max_cpu_freq + cpu_core_count

            # считываем релиз опреационной системы
            result = subprocess.run(OS_RELEASE_INFO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            release_info = result.stdout.strip().split("\n")
            for release in release_info:
                analyze_release = release.split(":")
                if analyze_release[0].strip().lower() == 'Description'.lower():
                    release_info_msg = f"Операционная система: <b>{analyze_release[1].strip()}</b>\n"
                    break
            
            device_info_msg = device_info_msg + release_info_msg 
            # Считываем информацию о версии ядра ОС
            async with aiofiles.open(KERNEL_VERSION_FILE, mode='r') as linux_file:
                contents = await linux_file.read()
            hostname_msg = f"Версия ядра: <b>{contents.strip().split()[2].strip()}</b>\n"
            device_info_msg = device_info_msg + hostname_msg 

            # Считывае сведения о памяти и свопе
            contents =[]
            memory_device = {}
            async with aiofiles.open(MEM_INFO_FILE, mode='r') as linux_file:
                async for line in linux_file:
                    # contents.append(line)
                    record = line.strip().split(':')
                    if record[0] == "MemTotal":
                        memory_device['MemTotal'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'MemFree':
                        memory_device['MemFree'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'Buffers':
                        memory_device['Buffers'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'Cached':
                        memory_device['Cached'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'SwapTotal':
                        memory_device['SwapTotal'] = int(record[1].strip()[:-2].strip())
                    elif record[0] == 'SwapFree':
                        memory_device['SwapFree'] = int(record[1].strip()[:-2].strip())

            # Расчитываем процент загрузки памяти
            used_memory_percent = round((memory_device['MemTotal'] - memory_device['MemFree'] - memory_device['Buffers'] - memory_device['Cached']) * 100 / memory_device['MemTotal'])
            memory_msg = f"Оперативная память: занято <b>{used_memory_percent}%</b> из <b>{memory_device['MemTotal'] / (1024 * 1024):.2f}</b> Гб\n"
            device_info_msg = device_info_msg + memory_msg
            # Расчитываем процент загрузки свопа
            used_swap_percent = round((memory_device['SwapTotal'] - memory_device['SwapFree']) * 100 / memory_device['SwapTotal'])
            swap_msg = f"Cвоп: занято <b>{used_swap_percent}%</b> из <b>{memory_device['SwapTotal'] / (1024 * 1024):.2f}</b> Гб\n"
            device_info_msg = device_info_msg + swap_msg 

            # OS_DF_INFO
            # Сведения об использовании карты памяти и раздела с логами
            result = subprocess.run(OS_DF_INFO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            partions_usage_raw = result.stdout.strip().split("\n")
            for item in partions_usage_raw:
                root_partion = item.split()
                if root_partion[5].strip() == "/":
                    root_info = root_partion
                    continue
                if root_partion[5].strip() == "/var/log":
                    log_info = root_partion
                
            total_capacity = root_info[1].strip()
            if total_capacity[len(total_capacity) - 1] == "G":
                total_capacity = total_capacity[:-1] + " Гб"
            
            root_usage_msg = f"Карта памяти: занято <b>{root_info[4].strip()}</b> из <b>{total_capacity}</b>\n"

            device_info_msg = device_info_msg + root_usage_msg 

            # # Добавляем сообщение об использовании раздела с логами
            total_capacity = log_info[1].strip()
            if total_capacity[len(total_capacity) - 1] == "G":
                total_capacity = total_capacity[:-1] + " Гб"
            elif total_capacity[len(total_capacity) - 1] == "M":
                total_capacity = total_capacity[:-1] + " Мб"

            log_usage_msg = f"Логи: занято <b>{log_info[4].strip()}</b> из <b>{total_capacity}</b>"

            log_level_count = int(log_info[4].strip()[:-1])
            if log_level_count > LEVEL_LOG_WARNING:
                log_usage_msg = log_usage_msg + ' \U0001F198\n' #' \U0001F534\n'
            else:
                log_usage_msg = log_usage_msg + "\n"

            device_info_msg = device_info_msg + log_usage_msg

            await msg.answer(device_info_msg)            
        except (UnboundLocalError, IndexError, FileNotFoundError) as _exp:
            # await msg.answer(str(_exp))
            await msg.answer(ERROR_DEVICE_GET_DATA)
       
        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))

# Обработчик для ЗАПУСКА/ПЕРЕЗАПУСКА ssh-клиента (в обертке c AutoSSH)
@router.message(Command("ssh_restart"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        # Ищем запущенный экземпляр процесса autossh
        proc = await asyncio.create_subprocess_shell(
            cmd = SEARCH_AUTUSSH_CMD,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE
        )
        # stderr - оставил для примера
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            pid_autossh = int(stdout.decode())
            await msg.answer(AUTO_SSH_FOUND_MSG)
            proc = await asyncio.create_subprocess_shell(
            cmd = f'kill {pid_autossh}',
            stdout = asyncio.subprocess.DEVNULL            
        )
            await proc.communicate()
        else:
            # Экземпляр процесса autossh не найден
            await msg.answer(AUTO_SSH_NO_FOUND_MSG)

        await asyncio.sleep(10)
        proc = await asyncio.create_subprocess_shell(
            cmd = RUN_AUTUSSH_CMD,
            stdout = asyncio.subprocess.DEVNULL            
        )
        await proc.communicate()
        # Сообщение о запуске клиента ssh
        await msg.answer(AUTO_SSH_START_MSG)            

        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


@router.message(Command("net_test"))
async def start_handler(msg: Message):
    if msg.from_user.id in USER_TLG_IDS:
        await msg.answer(START_NETWORK_TEST_MSG)
        for host in TEST_NETWORK_HOSTS.keys():
            result = await ping_host(host)
            if result['return_code'] == 0:
                info_msg = f'{TEST_NETWORK_HOSTS[host]} ({host}) <b>доступен</b>' + ' \U00002705\n'
                info_msg = info_msg + f"Cреднее время пингования узла - <b>{result['avarage_time']}</b> мс.\n"
                info_msg = info_msg + f"Потери ICMP-пакетов: <b>{result['persent_loss']}%</b>"
                
                await msg.answer(info_msg)
            else:
                await msg.answer(f'{TEST_NETWORK_HOSTS[host]} ({host}) <b>недоступен</b>.' + ' \U0001F198')
        # Информационной сообщение пользователю бота
        await msg.answer('<u>Успешной работы!</u>')
        # создаем задачу по удалению исходного сообщения с командой
        asyncio.create_task(delete_message(msg, TIME_DELETE))


async def shutdown_handler(bot: Bot):
    for item in USER_TLG_IDS:
        try:
            await bot.send_message(item, STOP_BOT_MSG)
        except TelegramBadRequest:
            continue
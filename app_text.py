# Текстовые сообщения, передаваемые через Telegram-бота 
HELLO_MSG = "Привет! Добро пожаловать в бот-помощник для обслуживания точки доступа к 'МИС Барс'."
REBOOT_MSG = 'Отправляем сигнал на перезагрузку точки доступа к <b>МИС "Барс"</b>.'
LINK_OFF_MSG = 'Выключаем связь с сетью <b>МИС "Барс"</b>.'
LINK_ON_MSG = 'Включаем связь с сетью <b>МИС "Барс"</b>.'
#REBOOT_NO_MSG = 'У бота нет прав для перезагрузки точки доступа к МИС "Барс".'
STATUS_ANSWER_MSG = 'Считываем данные о параметрах точки доступа к <b>МИС "Барс"</b>.'
AFTER_REBOOT_MSG = 'Бот на устройстве <b><I><u>Бегемотик</u></I></b> запущен.'


NO_TEMP_FOUND = "Температура: <I>нет данных</I>"

# Команда оболочки для перезагрузки системы 
SYSTEM_REBOOT_CMD = '/sbin/reboot'

# Команды оболочки для включения/отключения интерфейса
# ВАЖНО! Требуются изменения в файле /etc/sudoerrs (я внес такие)
# orangepi  ALL=NOPASSWD: /sbin/ip
SYSTEM_UP_NETWORK_CMD = 'sudo /sbin/ip link set eth0 up'
SYSTEM_DOWN_NETWORK_CMD = 'sudo /sbin/ip link set eth0 down'


# Имена фалов из каталога /proc для получения данных о системе
# Использование памяти
MEM_INFO_FILE = '/proc/meminfo'
# Температура платы
THERMAL_FILE =  '/sys/devices/virtual/thermal/thermal_zone0/temp'
# Время непрерывной работы
UPTIME_INFO_FILE = '/proc/uptime'
# файл для получения статуса интерфейса eth0
NET_DEVICE_CARRIER_FILE =  '/sys/class/net/eth0/carrier'

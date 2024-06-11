# Параметры для доступа к МИС БАРС
TARGET = '10.20.3.9'
WEB_PROTOCOL = 'http://'
WEB_PORT = ''
GTW = '10.21.151.65'

# Текстовые сообщения, передаваемые через Telegram-бота 
HELLO_MSG = "Добро пожаловать в бот-помощник <b>'МИС Барс'</b>. Ваше действие:"
REBOOT_MSG = 'Отправлен сигнал на перезагрузку точки доступа к <b>МИС "Барс"</b>.'
LINK_OFF_MSG = 'Выключаем связь с сетью <b>МИС "Барс"</b>.'
LINK_ON_MSG = 'Включаем связь с сетью <b>МИС "Барс"</b>.'
#REBOOT_NO_MSG = 'У бота нет прав для перезагрузки точки доступа к МИС "Барс".'
STATUS_ANSWER_MSG = 'Считываем данные о параметрах точки доступа к <b>МИС "Барс"</b>.'
AFTER_REBOOT_MSG = '\U00002705 ' + 'Бот на устройстве <tg-spoiler><b><I><u>Бегемотик</u></I></b></tg-spoiler> запущен.' 
STOP_BOT_MSG = '\U0001F198 ' + 'Бот на устройстве <tg-spoiler><b><I><u>Бегемотик</u></I></b></tg-spoiler> остановлен.' 
AFTER_POWER_ON_OFF_MSG = 'Устройство запущено после <b>включения/выключения</b> питания. Возможны коллизии при работе! ' + '\U0001F198'
AUTO_SSH_FOUND_MSG = 'Процесс <b>AUTOSSH</b> найден.'
AUTO_SSH_NO_FOUND_MSG = 'Процесс <b>AUTOSSH</b> не найден.'
AUTO_SSH_START_MSG = 'Процесс <b>AUTOSSH</b> запущен/перезапущен.'
START_NETWORK_TEST_MSG = '<b>Начало тестирования доступа к Интернет-ресурсам ...</b>.'
VIEW_LOG_ERROR = 'При просмотре логов устройства <tg-spoiler><b><I><u>Бегемотик</u></I></b></tg-spoiler> прозошла ошибка!'


NO_TEMP_FOUND = "Температура: <I>нет данных</I>"
NO_INTERFACE_DATA = 'нет данных по сетевому интерфейсу'
ERROR_IP_LOG = '<b>Ошибка</b> при получении данных о значениях <b>ip</b>-адресов, выданных DHCP-сервером.'
ERROR_DEVICE_GET_DATA = 'При получении данных о параметрах устройства произошла ошибка.'

# Кнопки меню бота
STATUS_BUTTON = 'Статус устройства'
HELP_BUTTON = 'Команды бота'
CONNECT_TO_BARS = 'Подключиться к МИС "БАРС"'
DISCONNET_FROM_BARS = 'Отключиться от МИС "БАРС"'

# Команда оболочки для перезагрузки системы 
SYSTEM_REBOOT_CMD = '/sbin/shutdown -r +2'

# Команды оболочки для включения/отключения интерфейса
# ВАЖНО! Требуются изменения в файле /etc/sudoerrs (я внес такие)
# orangepi  ALL=NOPASSWD: /sbin/ip
SYSTEM_UP_NETWORK_CMD = 'sudo /sbin/ip link set eth0 up'
SYSTEM_DOWN_NETWORK_CMD = 'sudo /sbin/ip link set eth0 down'

RESTORE_ROUTE = f'sudo /sbin/ip route add {TARGET} via {GTW}'
# Команда для получения информации о процессоре(ах)
SHOW_CPU_INFO = 'lscpu'
# Команда для получения информации о дистрибутиве ОВ
OS_RELEASE_INFO = ['lsb_release', '-a']
# Команда для получения информации о версии ядра ОС
OS_RELEASE_INFO = ['lsb_release', '-a']
# Команда для получения сведений об испольщованных разделах
OS_DF_INFO = ['df', '-h']
# Команда на создание файла-маяка, сигнализирующего о первом запуске платы
OS_SEMAPHOR_CREATE = 'touch /tmp/orange.tmp'

# Команда на поиск запущенного экземпляра процесса autossh
SEARCH_AUTUSSH_CMD = 'pidof autossh'

# Команда на запуск autossh с параметрами
# параметры ssh см. в файле ~/.ssh/config
RUN_AUTUSSH_CMD = 'autossh -M 0 -f -N bars-gw &'

# Количестов записей системного журнала для просмотра
LAST_RECORD_COUNT = 20
# Команда просмотра последних записей системного журнала
VIEW_LAST_RECORDS_JOURNAL = f'journalctl -e -n {LAST_RECORD_COUNT}'


# Имена файлов из каталога /proc для получения данных о системе
# Использование памяти
MEM_INFO_FILE = '/proc/meminfo'
# Температура платы
THERMAL_FILE =  '/sys/devices/virtual/thermal/thermal_zone0/temp'
# Время непрерывной работы
UPTIME_INFO_FILE = '/proc/uptime'
# файл для получения статуса интерфейса eth0
NET_DEVICE_CARRIER_FILE =  '/sys/class/net/eth0/carrier'
# Файл с логами ip-адресов, получаемых от DHCP-сервера по
# проводному интерфейсу при вколючении устройства
IP_LOG_FILE = '/home/orangepi/ip.log'
# Файл с адресами шлюзов, полученных от DHCP по проводному 
# интерфейсу при вколючении устройства
GATEWAY_LOG_FILE = '/home/orangepi/route.log'
# файл для получения версии ядра операционной системы
KERNEL_VERSION_FILE = '/proc/version'
# файл для получения имени хоста
HOSTNAME_FILE = '/proc/sys/kernel/hostname'
# файл для получения инфорации о релизе платы
RELEASE_BOARD_FILE = '/etc/orangepi-release'

# файл-якорь первого включения
FIRST_LAUNCH_FILE = '/tmp/orange.tmp'

# URL_WEB_Server
#SOURCE_WEB_SERVER_URL = 'http://10.20.3.9'
SOURCE_WEB_SERVER_URL = "".join((WEB_PROTOCOL, TARGET, WEB_PORT))

# Узлы для проверки работоспособности сети
TEST_NETWORK_HOSTS = {
    '192.168.43.1' : "Шлюз сети Wi-Fi",
    'lombard-alania.ru' : 'SSH-сервер удаленного доступа',
    '77.88.8.8' : 'DNS-сервер Яндекса',
    #'beeline.ru' : 'Сервер провайдера',
    '8.8.4.4.': 'DNS-сервер Google',
}


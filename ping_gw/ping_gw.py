
import asyncio
import aiofiles
import math
import datetime

TARGET = "192.168.43.1"
# TARGET = "lombard-alania1.ru"
PACKET_COUNT = 10
TEMPLATE = '% packet loss'
LEVEL_ERROR = 80
TIME_KOEFF = 2 

# Файлы логов
LOG_FILE = '/tmp/ping.log'
ERROR_FILE = '/tmp/ping.err'

DEBUG_MODE = False

async def main():
    cmd_ping = f'ping -4 -c {PACKET_COUNT} {TARGET}'
    process = await asyncio.create_subprocess_shell(cmd_ping,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    # print(f'[{cmd_ping!r} exited with {process.returncode}]')
    # if stdout:
    #     result_txt = str(stdout.decode()).strip()
    #     print(f'[stdout]\n{result_txt}')
    #     pprint.pprint(result_txt.split("\n"))
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')

    try:
        if process.returncode == 0:
            result_txt = str(stdout.decode()).strip().split("\n")
            stat_str = ""
            for item in reversed(result_txt):
                if DEBUG_MODE:
                    print(item)
                if TEMPLATE in item:
                    stat_str = item
                    break
            if stat_str == "":
                raise ValueError
            total_list = stat_str.split(',')
            #['5 packets transmitted', ' 5 received', ' 0% packet loss', ' time 4008ms']
            if DEBUG_MODE:
                print(total_list)
            error_str = total_list[2]
            error = math.floor(float(error_str[:error_str.find(TEMPLATE)]))
            
            if DEBUG_MODE:
                print(f'Процент потерянных пакетов - {error}')

            if error >= LEVEL_ERROR:
                raise ValueError 

            time_str = total_list[3].split()[1]
            time_total_ms = int(time_str[:time_str.find('ms')])

            if DEBUG_MODE:
                print(f'Затраченное время (мс) - {time_total_ms}')

            if time_total_ms > PACKET_COUNT * TIME_KOEFF * 1_000:
                raise ValueError
            
            # Пишел лог удачного завершения работы
            
            async with aiofiles.open(LOG_FILE, mode='a') as log_file:
                await log_file.write(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') } : {''.join(total_list)}\n") 
            
        else:
            raise ValueError
            
    except (ValueError, IndexError):
        if DEBUG_MODE:
            print('Ошибка при проверке')
        # Пишем лог об ошибке
        async with aiofiles.open(ERROR_FILE, mode='a') as log_file:
            await log_file.write(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} \n") 



if __name__ == "__main__":
    asyncio.run(main=main())
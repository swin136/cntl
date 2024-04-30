import asyncio
import math


async def ping_host(target:str, packet_count=10): 
    TEMPLATE_1 ='min/avg/max/mdev'
    TEMPLATE_2 = '% packet loss'
    CMD_RUN = f'ping -4 -c {packet_count} {target}'
    result_ping = {}

    process = await asyncio.create_subprocess_shell(CMD_RUN,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.DEVNULL,
                                                    )
    stdout, stderr = await process.communicate()

    try:
        if process.returncode == 0:
            result_txt = str(stdout.decode()).strip().split("\n")
            stat_str1 = ""
            stat_str2 = ""
            for item in reversed(result_txt):
                if TEMPLATE_1 in item:
                    stat_str1 = item
                    continue
                if TEMPLATE_2 in item:
                    stat_str2 = item
                    continue

            if stat_str2 == "":
                raise ValueError
            total_list = stat_str2.split(',')
            # input(total_list)
            error_str = total_list[2]
            error = math.floor(float(error_str[:error_str.find(TEMPLATE_2)]))

            # rtt min/avg/max/mdev = 70.508/87.984/115.214/9.331 ms
            # print(stat_str1)
            result_ping['avarage_time'] = stat_str1.split()[3].split('/')[1]



            result_ping['return_code'] = 0
            result_ping['persent_loss'] = error
            
            return result_ping

        else:
            raise ValueError
    except (ValueError, IndexError):
        result_ping['return_code'] = -1
        return result_ping
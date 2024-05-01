from environs import Env
from dataclasses import dataclass

@dataclass
class Bots:
    bot_token: str
    user_ids: list


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str('bot_token'),
            user_ids=[int(item) for item in env.str('user_tlg_ids').split("/")]
            )
    )


bot_settings = get_settings('config.txt')

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from app_text import STATUS_BUTTON, HELP_BUTTON, CONNECT_TO_BARS, DISCONNET_FROM_BARS


kb = [
        [KeyboardButton(text= CONNECT_TO_BARS), KeyboardButton(text=STATUS_BUTTON)],
        [KeyboardButton(text=DISCONNET_FROM_BARS), KeyboardButton(text=HELP_BUTTON)],
        
    ]

keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
        input_field_placeholder="Или введите команду для бота")
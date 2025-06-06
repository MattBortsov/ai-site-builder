from typing import Dict, Tuple, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
    *,
    btns: Dict[str, str],
    sizes: Tuple[int, ...] = (1,),
) -> InlineKeyboardMarkup:
    """
    btns: {текст кнопки: callback_data или URL}
    sizes: кортеж с числом кнопок в строке, например (2,1) => 2 кнопки в первой, 1 — во второй
    """
    keyboard = InlineKeyboardBuilder()
    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
    return keyboard.adjust(*sizes).as_markup()

from typing import Tuple, Optional

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: Optional[str] = None,
    request_contact: Optional[int] = None,
    request_location: Optional[int] = None,
    sizes: Tuple[int, ...] = (2,),
) -> ReplyKeyboardMarkup:
    """
    btns: последовательность текстов кнопок
    placeholder: text, который будет в input
    request_contact: индекс кнопки, которая отправит контакт
    request_location: индекс кнопки, которая запросит локацию
    sizes: кортеж с числом кнопок в строке, например (2,1)
    """
    keyboard = ReplyKeyboardBuilder()
    for idx, text in enumerate(btns):
        if request_contact is not None and idx == request_contact:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location is not None and idx == request_location:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )
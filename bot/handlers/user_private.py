from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from keyboards.reply import get_keyboard
from keyboards.inline import get_callback_btns
from services.site_generator import generate_site_and_return  # должен возвращать (file_path, html_code)
from common.texts import (
    START_TEXT, EXAMPLE_TEXT, GENERATE_TEXT, START_GENERATE,
    SITE_READY_TEXT, USE_SITE_TEXT, PROMPT_INSTRUCTION,
    NOT_TEXT, USE_SITE_TEXT, BALANCE_TEXT, PAYMENT_TEXT, SELECT_PAYMENT_METHOD_TEXT
)

router = Router()


class GenerateSite(StatesGroup):
    wait_prompt = State()


# ——— Вспомогательные функции для меню ———

async def show_start_menu(message: types.Message, state: FSMContext):
    """Старт: кнопка Генерация"""
    await state.clear()
    kb = get_keyboard(
        '✨ Сгенерировать сайт',
        placeholder='Нажмите, чтобы начать',
        sizes=(1,)
    )
    await message.answer(START_TEXT, reply_markup=kb)


async def show_prompt_menu(message: types.Message, state: FSMContext):
    """Ожидание промпта: кнопки На главную, Отмена"""
    await state.set_state(GenerateSite.wait_prompt)
    kb = get_keyboard(
        'На главную', '❌ Отмена',
        placeholder='Введите описание сайта',
        sizes=(2,)
    )
    await message.answer("Напиши, какой сайт ты хочешь получить:", reply_markup=kb)


async def show_post_menu(callback_or_msg, file_url: str):
    """После генерации: inline-кнопки"""
    buttons = {
        'Сгенерировать новый сайт': 'regen',
        'Использовать сайт в своем проекте': 'use_site'
    }
    kb = get_callback_btns(btns=buttons, sizes=(2,))
    text = f"✅ Ваш сайт готов:\n{file_url}"
    if isinstance(callback_or_msg, types.CallbackQuery):
        await callback_or_msg.answer()
        await callback_or_msg.message.answer(text, reply_markup=kb)
    else:
        await callback_or_msg.answer(text, reply_markup=kb)


async def show_main_inline_menu(callback: types.CallbackQuery):
    """Главная после первого цикла: inline-кнопки"""
    await callback.answer()
    buttons = {
        'ℹ️ Как писать промпт':       'help_prompt',
        '✨ Сгенерировать сайт':       'generate',
        'Проверенные разработчики':   'verified_devs',
        'Баланс':                     'balance',
    }
    kb = get_callback_btns(btns=buttons, sizes=(2, 2))
    await callback.message.answer(START_TEXT, reply_markup=kb)


# ——— Хендлеры ———

@router.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await show_start_menu(msg, state)


@router.message(StateFilter(None), F.text == '✨ Сгенерировать сайт')
async def on_generate_start(msg: types.Message, state: FSMContext):
    await show_prompt_menu(msg, state)


@router.message(GenerateSite.wait_prompt, F.text == 'На главную')
async def prompt_back_to_main(msg: types.Message, state: FSMContext):
    await show_start_menu(msg, state)


@router.message(GenerateSite.wait_prompt, F.text == '❌ Отмена')
async def prompt_cancel(msg: types.Message, state: FSMContext):
    await show_start_menu(msg, state)


@router.message(GenerateSite.wait_prompt, ~F.text)
async def prompt_not_text(msg: types.Message):
    await msg.answer("Пожалуйста, отправьте текстовое описание сайта.")


@router.message(GenerateSite.wait_prompt, F.text)
async def handle_prompt(msg: types.Message, state: FSMContext):
    # генерируем сайт и получаем путь + HTML-код
    file_path, html_code = await generate_site_and_return(msg.text)
    file_url = f"https://example.com/{file_path}"  # или ваш BASE_URL

    # сохраняем в FSMContext для дальнейшего использования
    await state.update_data(last_file_path=file_path, last_html_code=html_code)

    # показ пост-меню
    await state.clear()
    await show_post_menu(msg, file_url)


@router.callback_query(F.data == 'regen')
async def on_regen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_prompt_menu(callback.message, state)


@router.callback_query(F.data == 'use_site')
async def on_use_site(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    file_path = data.get('last_file_path')
    html_code = data.get('last_html_code')

    # отправляем инструкцию
    await callback.message.answer(USE_IN_PROJECT_TEXT)

    # отправляем файл кода
    await callback.message.answer_document(
        FSInputFile(file_path),
        caption="Вот полный код вашего сайта"
    )

    # inline-кнопка На главную
    kb = get_callback_btns(btns={'На главную': 'back_main'}, sizes=(1,))
    await callback.message.answer("Вернуться в начало:", reply_markup=kb)


@router.callback_query(F.data == 'back_main')
async def on_back_main(callback: types.CallbackQuery, state: FSMContext):
    await show_main_inline_menu(callback)


@router.callback_query(F.data == 'help_prompt')
async def on_help_prompt(callback: types.CallbackQuery):
    await callback.answer()
    kb = get_callback_btns(
        btns={
            'Бесплатный туториал': 'https://example.com/prompts-tutorial',
            'Назад': 'back_main'
        },
        sizes=(2,)
    )
    await callback.message.answer(PROMPT_INSTRUCTION, reply_markup=kb)


@router.callback_query(F.data == 'verified_devs')
async def on_verified_devs(callback: types.CallbackQuery):
    await callback.answer()
    kb = get_callback_btns(
        btns={
            'Найти разработчика': 'find_dev',
            'Стать разработчиком': 'become_dev'
        },
        sizes=(2,)
    )
    await callback.message.answer(VERIFIED_DEVS_TEXT, reply_markup=kb)


@router.callback_query(F.data == 'balance')
async def on_balance(callback: types.CallbackQuery):
    await callback.answer()
    kb = get_callback_btns(
        btns={
            'Оплата': 'payment',
            'Назад':  'back_main'
        },
        sizes=(2,)
    )
    await callback.message.answer(BALANCE_TEXT, reply_markup=kb)


@router.callback_query(F.data == 'payment')
async def on_payment(callback: types.CallbackQuery):
    await callback.answer()
    kb = get_callback_btns(
        btns={
            'Купить 3 сайта':  'buy_3',
            'Купить 10 сайтов': 'buy_10',
            'Купить 30 сайтов': 'buy_30'
        },
        sizes=(3,)
    )
    await callback.message.answer("Выберите тариф:", reply_markup=kb)


@router.callback_query(F.data.in_({'buy_3','buy_10','buy_30'}))
async def on_choose_tariff(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    tariff = callback.data  # buy_3, buy_10 или buy_30
    # ссылки на оплату, можно вытянуть из конфига
    links = {
        'buy_3': {
            'По карте РФ': 'https://pay.example.com/rf/3',
            'По карте иностранного банка': 'https://pay.example.com/int/3'
        },
        'buy_10': {
            'По карте РФ': 'https://pay.example.com/rf/10',
            'По карте иностранного банка': 'https://pay.example.com/int/10'
        },
        'buy_30': {
            'По карте РФ': 'https://pay.example.com/rf/30',
            'По карте иностранного банка': 'https://pay.example.com/int/30'
        },
    }
    kb = get_callback_btns(btns=links[tariff], sizes=(2,))
    await callback.message.answer("Выберите способ оплаты:", reply_markup=kb)


# Неопознанные сообщения
@router.message()
async def fallback(msg: types.Message):
    await msg.answer("Я не понял. Попробуйте воспользоваться кнопками меню.")

@router.message(StateFilter(None), F.text == 'Примеры')
async def give_example(message: Message):
    """Показ примеров — открывает inline-кнопки"""
    await message.answer(
        EXAMPLE_TEXT,
        reply_markup=get_callback_btns(btns={
            'Смотреть примеры': 'link',
            '✨ Сгенерировать свой сайт': 'generate'
        })
    )


@router.callback_query(StateFilter(None), F.data == 'generate')
async def get_prompt_from_example(
    callback: CallbackQuery,
    state: FSMContext
):
    """При нажатии 'Сгенерировать свой сайт' на inline-кнопках"""
    assert isinstance(callback.message, Message)
    await callback.message.answer(
        GENERATE_TEXT,
        reply_markup=types.ReplyKeyboardRemove()
    )
    await callback.answer()
    await state.set_state(GenerateSite.generate)
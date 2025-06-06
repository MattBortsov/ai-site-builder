from aiogram import Dispatcher
from .user_private import router as user_private_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(user_private_router)

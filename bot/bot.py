import os

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

load_dotenv()

from handlers import register_all_handlers
from services.utils import cleanup_old_sites
# from database.engine import create_db, drop_db


token = os.getenv('BOT_TOKEN')
if not token:
    raise RuntimeError('BOT_TOKEN is missing in .env file')

bot = Bot(
    token=token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


async def on_startup():
    # await create_db()
    register_all_handlers(dp)
    # register_db_middleware(dp)


async def on_shutdown():
    print("Бот лег")
    await bot.session.close()


def setup_cleanup_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    # каждый день в 03:00 UTC
    scheduler.add_job(cleanup_old_sites, 'cron', hour=3, minute=0)
    scheduler.start()


async def main():
    await on_startup()
    await dp.start_polling(bot)
    await on_shutdown()


if __name__ == "__main__":
    setup_cleanup_scheduler()
    asyncio.run(main())

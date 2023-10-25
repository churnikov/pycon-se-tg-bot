import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from tortoise import Tortoise

from pycon_se_bot.bot import *  # noqa F401, F403
from pycon_se_bot.settings import (
    BOT_TOKEN,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    dp,
)


async def main() -> None:
    await Tortoise.init(
        db_url=f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}",
        modules={"models": ["pycon_se_bot.models"]},
    )
    # Create the database schema
    await Tortoise.generate_schemas()

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp.bot = bot
    # And the run events dispatching
    await dp.start_polling(bot)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

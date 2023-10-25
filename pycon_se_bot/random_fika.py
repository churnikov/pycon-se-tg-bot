import asyncio
import random
from typing import List

from aiogram import Bot
from aiogram.enums import ParseMode
from tortoise import Tortoise

from pycon_se_bot.bot import *  # noqa F401, F403
from pycon_se_bot.models import Matches, User
from pycon_se_bot.settings import (
    BOT_TOKEN,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    dp,
)


async def get_users_in_random_fika() -> List[User]:
    """Get all users that are in a random fika."""
    return await User.filter(fikas__isnull=False)


async def shuffle_paritcipants() -> None:
    """Shuffle the participants in the random fika."""
    users = await get_users_in_random_fika()
    random.shuffle(users)
    if len(users) % 2 == 1:
        lucky_user = users.pop()
        await Matches.create(user1=lucky_user, user2=lucky_user)
    for i in range(0, len(users), 2):
        user1 = users[i]
        user2 = users[i + 1]
        await Matches.create(user1=user1, user2=user2)


async def get_matches() -> List[Matches]:
    """Get all matches."""
    return await Matches.all().prefetch_related("user1", "user2")


async def send_notification_to_user(user: User, match: User) -> None:
    """Send notification to user."""
    await dp.bot.send_message(
        user.id,
        f"Hi {user.name}! You have been matched with {match.name} for a random fika! "
        f"Please contact each other to set up a time and place to meet. "
        f"Once you have met, please mark yourself as done with the command `/fika done`.",
    )
    await dp.bot.send_message(
        user.id,
        f"{user.name}'s contact info: {user.contact}",
    )


async def send_notifications_to_users() -> None:
    """Send notifications to users."""
    matches = await get_matches()
    for match in matches:
        user1 = match.user1
        user2 = match.user2
        if user1 == user2:
            await dp.bot.send_message(
                user1.id,
                f"Hi {user1.name}! Unfortunately, we were not able to find a match for you this time. "
                "But we want to make it up to you. Please contact us at the registration desk :) ",
            )
            continue
        await send_notification_to_user(user1, user2)
        await send_notification_to_user(user2, user1)


async def main() -> None:
    await Tortoise.init(
        db_url=f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}",
        modules={"models": ["pycon_se_bot.models"]},
    )
    # Create the database schema
    await Tortoise.generate_schemas()

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp.bot = bot

    await shuffle_paritcipants()
    await send_notifications_to_users()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

import asyncio
import json

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from pycon_se_bot.models import Room, Talk
from pycon_se_bot.settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
)

with open("talks.json") as f:
    talks_data = json.load(f).get("talks")


async def setup() -> None:
    # Connect to the database
    await Tortoise.init(
        db_url=f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}",
        modules={"models": ["__main__"]},
    )
    # Create the database schema
    await Tortoise.generate_schemas()

    # Populate the database with rooms and talks
    async with in_transaction():
        # Create rooms
        main_room, _ = await Room.get_or_create(name="Main Room")
        second_room, _ = await Room.get_or_create(name="Second Room")

        # Create talks
        for talk_data in talks_data:
            room = main_room if talk_data["room"] == "Main Room" else second_room
            date = "2023-11-09T{time}" if talk_data["day"] == 1 else "2023-11-10T{time}"

            await Talk.create(
                name=talk_data["name"],
                time_start=date.format(time=talk_data["time_start"]),
                time_end=date.format(time=talk_data["time_end"]),
                link=talk_data["link"],
                room=room,
                day=talk_data["day"],
            )


# Run the setup function
loop = asyncio.get_event_loop()
loop.run_until_complete(setup())

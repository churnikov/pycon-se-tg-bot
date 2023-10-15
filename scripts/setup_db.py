import asyncio

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from pycon_se_bot.models import Room, Talk

talks_data = [
    {
        "name": "Registration opens",
        "time_start": "07:00",
        "time_end": "08:30",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "Opening Speech",
        "time_start": "08:30",
        "time_end": "09:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "Keynote: Daniel Stenberg",
        "time_start": "09:00",
        "time_end": "10:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "coffee break",
        "time_start": "10:00",
        "time_end": "10:30",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "The Python packaging ecosystem – Simple guidelines for packaging",
        "time_start": "10:30",
        "time_end": "11:00",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#the-python-packaging-ecosystem-–-simple-guidelines-for-packaging",
    },
    {
        "name": "Python in Excel, a big step for finance",
        "time_start": "11:00",
        "time_end": "11:30",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#pythone-in-excel-a-big-step-for-finance",
    },
    {
        "name": "Kivy: Cross-platform App development for Pythonistas",
        "time_start": "11:30",
        "time_end": "12:00",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#kivy-cross-platform-app-development-for-pythonistas",
    },
    {
        "name": "Lunch",
        "time_start": "12:00",
        "time_end": "13:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "Keynote: Sebastián Ramírez",
        "time_start": "13:00",
        "time_end": "14:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "CompiledPoetry.py : teaching about diversity with Python and poetry",
        "time_start": "14:00",
        "time_end": "14:30",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#compiledpoetry-py-teaching-about-diversity-with-python-and-poetry",
    },
    {
        "name": "Harry Potter and the Elastic Python Clients",
        "time_start": "14:30",
        "time_end": "15:00",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#harry-potter-and-the-elastic-python-clients",
    },
    {
        "name": "GraphQL as an umbrella for microservices",
        "time_start": "15:00",
        "time_end": "15:30",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#graphql-as-an-umbrella-for-microservices",
    },
    {
        "name": "coffee break",
        "time_start": "15:30",
        "time_end": "16:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "Debugging Python",
        "time_start": "16:00",
        "time_end": "16:30",
        "room": "Main Room",
        "day": 1,
        "link": "https://pycon.se/#debugging-python",
    },
    {
        "name": "Closing Day 1",
        "time_start": "16:30",
        "time_end": "17:00",
        "room": "Main Room",
        "day": 1,
        "link": None,
    },
    {
        "name": "Keynote: Carol Willing",
        "time_start": "09:00",
        "time_end": "10:00",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "coffee break",
        "time_start": "10:00",
        "time_end": "10:30",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "PEP 458 a solution not only for PyPI",
        "time_start": "10:30",
        "time_end": "11:00",
        "room": "Main Room",
        "day": 2,
        "link": "https://pycon.se/#pep458-a-solution-not-only-for-pypi",
    },
    {
        "name": "Load testing with Python and Locust",
        "time_start": "11:00",
        "time_end": "11:30",
        "room": "Main Room",
        "day": 2,
        "link": "https://pycon.se/#load-testing-with-python-and-locust",
    },
    {
        "name": "Sustainable Python Performance",
        "time_start": "11:30",
        "time_end": "12:00",
        "room": "Main Room",
        "day": 2,
        "link": "https://pycon.se/#sustainable-python-performance",
    },
    {
        "name": "Lunch",
        "time_start": "12:00",
        "time_end": "13:00",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "Keynote: Deb Nicholson",
        "time_start": "13:00",
        "time_end": "14:00",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "Exploring OpenSearch, Python, and Serverless: Crafting Efficient and Modern Search Applications",
        "time_start": "14:00",
        "time_end": "14:30",
        "room": "Main Room",
        "day": 2,
        "link": (
            "https://pycon.se/#exploring-opensearch-python-and-serverless-crafting-efficient"
            "-and-modern-search-applications",
        ),
    },
    {
        "name": "CALFEM - Teaching the Finite Element method in Python",
        "time_start": "14:30",
        "time_end": "15:00",
        "room": "Main Room",
        "day": 2,
        "link": "https://pycon.se/#calfem-teaching-the-finite-element-method-in-python",
    },
    {
        "name": "Robyn: An async Python web framework with a Rust runtime",
        "time_start": "15:00",
        "time_end": "15:30",
        "room": "Main Room",
        "day": 2,
        "link": "https://pycon.se/#robyn-an-async-python-web-framework-with-a-rust-runtime",
    },
    {
        "name": "coffee break",
        "time_start": "15:30",
        "time_end": "16:00",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "Python Developer Experience with Polylith",
        "time_start": "16:00",
        "time_end": "16:30",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "Lightning talks",
        "time_start": "16:30",
        "time_end": "17:00",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
    {
        "name": "Closing speech of PyCon Sweden 2023",
        "time_start": "17:00",
        "time_end": "17:30",
        "room": "Main Room",
        "day": 2,
        "link": None,
    },
]


async def setup() -> None:
    # Connect to the database
    await Tortoise.init(db_url="postgres://nikita:@localhost/postgres", modules={"models": ["__main__"]})
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
            date = "2023-11-09 {time}" if talk_data["day"] == 1 else "2023-11-10 {time}"

            await Talk.create(
                name=talk_data["name"],
                time_start=date.format(time=talk_data["time_start"]),
                time_end=date.format(time=talk_data["time_end"]),
                link=talk_data["link"],
                room=room,
            )


# Run the setup function
loop = asyncio.get_event_loop()
loop.run_until_complete(setup())

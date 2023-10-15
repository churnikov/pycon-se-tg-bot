import asyncio

import aiohttp
from bs4 import BeautifulSoup


# Function to extract talks from a table
def extract_talks(
    table: BeautifulSoup,
) -> list[tuple[str, tuple[str | None, str | None], tuple[str | None, str | None]]]:
    talks = []
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:
            time_slot: str = cols[0].text.strip()

            # Extract main room talk and link
            main_room_talk: str | None = cols[1].text.strip() if cols[1].text.strip() != "" else None
            main_room_link: str | None = None
            main_room_anchor = cols[1].find("a")
            if main_room_anchor:
                link_id = main_room_anchor["href"].split("#")[-1]
                main_room_link = f"https://pycon.se/{link_id}"

            # Extract second room talk and link
            second_room_talk: str | None = None
            second_room_link: str | None = None
            if len(cols) > 2:
                second_room_talk = cols[2].text.strip() if cols[2].text.strip() != "" else None
                second_room_anchor = cols[2].find("a")
                if second_room_anchor:
                    link_id = second_room_anchor["href"].split("#")[-1]
                    second_room_link = f"https://pycon.se/{link_id}"

            talks.append((time_slot, (main_room_talk, main_room_link), (second_room_talk, second_room_link)))
    return talks


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pycon.se/") as resp:
            resp.raise_for_status()
            soup = BeautifulSoup(await resp.text(), "lxml")
            program = soup.find(id="program")

            # Find tables for Day 1 and Day 2
            tables = program.find_all("table", class_="tg")
            day1_table, day2_table = tables

            # Extract talks
            day1_talks = extract_talks(day1_table)
            day2_talks = extract_talks(day2_table)

            # Print talks
            print("Day 1 Talks:")
            for talk in day1_talks:
                print(talk)

            print("\nDay 2 Talks:")
            for talk in day2_talks:
                print(talk)


asyncio.run(main())

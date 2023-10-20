import asyncio

import aiohttp
from bs4 import BeautifulSoup


def get_link_to_talk(soup: BeautifulSoup) -> str | None:
    link: str | None = None
    talk_link = soup.find("a")
    like_button = soup.find("button", class_="heart-button")

    link_id = None
    if talk_link and talk_link["href"] != "#":
        link_id = talk_link["href"].split("#")[-1]
    elif like_button:
        link_id = like_button["id"]

    if link_id:
        link = f"https://pycon.se/#{link_id}"

    return link


# Function to extract talks from a table
def extract_talks(
    table: BeautifulSoup,
) -> list[dict[str, str | None]]:
    talks = []
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:
            time_slot: str = cols[0].text.strip()
            time_start, time_end = time_slot.split("-")

            # Extract main room talk and link
            main_room_talk: str | None = cols[1].text.strip() if cols[1].text.strip() != "" else None
            main_room_link = get_link_to_talk(cols[1])
            talks.append(
                {
                    "name": main_room_talk,
                    "time_start": time_start,
                    "time_end": time_end,
                    "room": "Main Room",
                    "link": main_room_link,
                }
                )

            # Extract second room talk and link
            second_room_talk: str | None = None
            second_room_link: str | None = None
            if len(cols) > 2:
                second_room_talk = cols[2].text.strip() if cols[2].text.strip() != "" else None
                second_room_link = get_link_to_talk(cols[2])
                talks.append(
                    {
                        "name": second_room_talk,
                        "time_start": time_start,
                        "time_end": time_end,
                        "room": "Second Room",
                        "link": second_room_link,
                    }
                    )

    return talks


async def main() -> None:
    talks = []
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
            for talk in day1_talks:
                talk["day"] = 1
            for talk in day2_talks:
                talk["day"] = 2

            talks = [*day1_talks, *day2_talks]
    
        async with session.get("https://www.pycon.se/speakers.json") as resp:
            resp.raise_for_status()
            speakers = await resp.json()
            for talk in talks:
                remote_talk = next((speaker for speaker in speakers if speaker["Talk/Workshop title"] == talk["name"]), None)
                if remote_talk:
                    talk["image"] = remote_talk.get("Images", None)
                    talk["speaker_biography"] = remote_talk.get("Your biography", None)
                    talk["audience_level"] = remote_talk.get("Audience knowledge level", None)
                    talk["talk_abstract"] = remote_talk.get("Abstract", None)
                    talk["proposal_type"] = remote_talk.get("Proposal type", None)

    with open("talks.json", "w") as f:
        import json
        json.dump({"talks": talks}, f, indent=4)


asyncio.run(main())

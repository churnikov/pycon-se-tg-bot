import logging
from datetime import datetime, timedelta

from aiogram import F, types
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from pycon_se_bot.models import Fika, LikedTalk, Talk, User
from pycon_se_bot.settings import ADMIN_PASSWORD, dp

# Utility functions


async def get_talks(day: int) -> list[Talk]:
    """
    Get all talks for a given day

    :param day: Day number

    :return: List of talks
    """
    talks = await (Talk.filter(day=day).all().prefetch_related("room").order_by("time_start"))
    print(talks[0].time_start)
    return talks


def split_talks_by_room(talks: list[Talk]) -> dict[str, dict[str, Talk]]:
    """
    Split talks by room and time

    :param talks: List of talks

    :return: Dict of talks
    """
    table_data = {}
    for talk in talks:
        time_key = f"{talk.time_start.strftime('%H:%M')} - {talk.time_end.strftime('%H:%M')}"
        if time_key not in table_data:
            table_data[time_key] = {"Main Room": None, "Second Room": None}
        room_name = talk.room.name if talk.room else None
        table_data[time_key][room_name] = talk
    return table_data


async def generate_keyboard_for_day(day: int) -> ReplyKeyboardMarkup:
    """
    Generate keyboard for a given day

    :param day: Day number

    :return: Telegram Keyboard
    """
    talks = await get_talks(day)
    talks = split_talks_by_room(talks)
    schedule_kbrd = [
        [
            KeyboardButton(text="Main Room"),
            KeyboardButton(text="Second Room"),
        ],
    ]
    for rooms in talks.values():
        row = []
        for room_name, talk in rooms.items():
            if talk:
                row.append(
                    KeyboardButton(
                        text=f"{talk.name} ({talk.time_start.strftime('%H:%M')} - {talk.time_end.strftime('%H:%M')})"
                    )
                )
        schedule_kbrd.append(row)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="< Schedule")],
            *schedule_kbrd,
        ],
        is_persistent=False,
    )
    return keyboard


async def generate_message_and_inline_keyboard_for_talk(
    talk: Talk, user: User
) -> tuple[str, InlineKeyboardMarkup | None]:
    """
    Generate message and inline keyboard for a given talk

    :param talk: Talk

    :return: Tuple of message and inline keyboard
    """
    message = f"{talk.name} ({talk.time_start.strftime('%H:%M')} - {talk.time_end.strftime('%H:%M')})"
    if talk.link:
        message += f"\nLink: {talk.link}"
    if talk.room:
        message += f"\nRoom: {talk.room.name}"
    if talk.speaker:
        message += f"\nSpeaker: {talk.speaker}"

    if talk.link:
        liked_talk_relation = await LikedTalk.filter(talk=talk, user=user).first()
        if liked_talk_relation:
            like_button = InlineKeyboardButton(
                text="Remove like", callback_data=SchleduleCallback(talk_id=talk.id, liked=False).pack()
            )
        else:
            like_button = InlineKeyboardButton(
                text="Like", callback_data=SchleduleCallback(talk_id=talk.id, liked=True).pack()
            )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[like_button]])
    else:
        keyboard = None

    return message, keyboard


async def generate_messages_for_day(day: int, user: User) -> list[tuple[str, InlineKeyboardMarkup | None]]:
    """
    Generate messages for a given day

    :param day: Day number

    :return: List of messages
    """
    talks = await get_talks(day)
    talks = split_talks_by_room(talks)
    messages = []
    for time_slot, rooms in talks.items():
        for room_name, talk in rooms.items():
            if talk:
                text, keyboard = await generate_message_and_inline_keyboard_for_talk(talk, user)
                messages.append((text, keyboard))
    return messages


async def answer_message_with_talks(
    message: types.Message, replies: list[tuple[str, InlineKeyboardMarkup | None]], **kwargs
) -> None:
    """
    Answer message with a list of talks

    :param message: Message to answer
    :param replies: List of replies
    """
    for text, keyboard in replies:
        if keyboard is None:
            await message.answer(text, **kwargs)
        else:
            await message.answer(text, reply_markup=keyboard, **kwargs)


# Base functionality

DEFAULT_KEYBOAD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Schedule"),
        ],
        [KeyboardButton(text="Random fika (coffee)")],
    ],
    is_persistent=False,
)


@dp.message(CommandStart())  # type: ignore
async def start(message: types.Message) -> None:
    # Sending a message with the keyboard
    await message.answer(
        "Hello! By using this bot you agree to our code of conduct " "https://www.europython-society.org/coc/"
    )
    await message.answer("Hello! I'm your bot, choose an option:", reply_markup=DEFAULT_KEYBOAD)
    user = await User.get_or_create(id=message.from_user.id, name=message.from_user.full_name)
    print("Created user", user)


# Schedule handlers

# States
class Form(StatesGroup):
    schedule = State()
    random_fika = State()


class SchleduleCallback(CallbackData, prefix="talk"):
    talk_id: int
    liked: bool = False


# Handlers


@dp.message(F.text == "Schedule")  # type: ignore
@dp.message(F.text == "< Schedule")  # type: ignore
async def handle_schedule_lookup(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.schedule)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Day 1"),
                KeyboardButton(text="Day 2"),
            ],
            [
                KeyboardButton(text="Home"),
            ],
        ],
        is_persistent=False,
    )
    await message.answer("Which day's schedule would you like to see?", reply_markup=keyboard)


@dp.message(Command("now"))  # type: ignore
async def handle_schedule_now(message: types.Message) -> None:
    # current_time = datetime(2023, 11, 9, 10, 10)
    current_time = datetime.now()
    current_time = current_time.replace(second=0, microsecond=0)
    next_detltha = current_time + timedelta(minutes=61)
    previous_thirty_minutes = current_time - timedelta(minutes=30)
    print(previous_thirty_minutes, next_detltha)
    talks = await (
        Talk.filter(time_start__gte=previous_thirty_minutes, time_end__lte=next_detltha)
        .all()
        .prefetch_related("room")
        .order_by("time_start")
    )
    print(talks)
    talks = split_talks_by_room(talks)
    user = await User.get(id=message.from_user.id)
    for time_slot, rooms in talks.items():
        await message.answer(f"{time_slot}")
        for room_name, talk in rooms.items():
            if talk:
                await answer_message_with_talks(
                    message,
                    [await generate_message_and_inline_keyboard_for_talk(talk, user)],
                    disable_web_page_preview=True,
                    disable_notification=True,
                )
    else:
        await message.answer("Get some rest, there is nothing happening right now")


@dp.message(F.text.regexp(r"Day \d+"))  # type: ignore
async def handle_schedule_for_day(message: types.Message, state: FSMContext) -> None:
    day = message.text.split(" ")
    if len(day) != 2:
        await message.answer("Please choose a day")
        return

    day = day[1]
    user = await User.get(id=message.from_user.id)
    if day == "1":
        replies = await generate_messages_for_day(1, user)
        await answer_message_with_talks(message, replies, disable_web_page_preview=True, disable_notification=True)
    elif day == "2":
        replies = await generate_messages_for_day(2, user)
        await answer_message_with_talks(message, replies, disable_web_page_preview=True, disable_notification=True)
    else:
        await message.answer("Please choose a day")
        return

    await message.answer(f"Here's the schedule for day {day}")


@dp.message(F.text == "Home")  # type: ignore
async def handle_schedule_back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer("Back to home", reply_markup=DEFAULT_KEYBOAD)


@dp.callback_query(SchleduleCallback.filter())  # type: ignore
async def handle_schedule_talk_callback(callback_query: types.CallbackQuery, callback_data: SchleduleCallback) -> None:
    talk_id = callback_data.talk_id
    liked = callback_data.liked
    user = await User.get(id=callback_query.from_user.id)
    talk = await Talk.get(id=talk_id)
    if liked:
        await LikedTalk.create(talk=talk, user=user)
        await callback_query.answer("Talk saved")
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Remove like", callback_data=SchleduleCallback(talk_id=talk.id, liked=False).pack()
                        ),
                    ],
                ]
            )
        )
    else:
        await LikedTalk.filter(talk=talk, user=user).delete()
        await callback_query.answer("Talk removed")
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Like", callback_data=SchleduleCallback(talk_id=talk.id, liked=True).pack()
                        ),
                    ],
                ]
            )
        )


@dp.message(Command("liked"))  # type: ignore
async def handle_liked_talks(message: types.Message) -> None:
    user = await User.get(id=message.from_user.id)
    liked_talks = await user.liked_talks.all()
    talks = []
    for liked_talk in liked_talks:
        talks.append(await Talk.get(id=liked_talk.talk_id).prefetch_related("room"))
    if not talks:
        await message.answer("You have no liked talks")
        return
    talks = split_talks_by_room(talks)
    for time_slot, rooms in talks.items():
        for room_name, talk in rooms.items():
            if talk:
                await answer_message_with_talks(
                    message,
                    [await generate_message_and_inline_keyboard_for_talk(talk, user)],
                    disable_web_page_preview=True,
                    disable_notification=True,
                )


# RandomFika handlers

# States
class FikaCallback(CallbackData, prefix="fika"):
    is_participating: bool


class RandomFika(StatesGroup):
    participating = State()


# Handlers
@dp.message(F.text == "Random fika (coffee)")  # type: ignore
async def handle_random_fika(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.random_fika)
    await message.answer("Do you want to participate in random fika?")
    await message.answer("You will be matched with a random person from the conference")
    await message.answer(
        "You deside how you want to do it, but we recommend having a cinamon bun and a cup of coffee "
        "or a glass of beer after the conference. We just want to help you make approching people easier and "
        "have a good time.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Yes", callback_data=FikaCallback(is_participating=True).pack()),
                    InlineKeyboardButton(text="No", callback_data=FikaCallback(is_participating=False).pack()),
                ],
            ]
        ),
    )


@dp.callback_query(FikaCallback.filter(F.is_participating == True))  # type: ignore; noqa: E712
async def handle_random_fika_yes(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    # TODO: May be times should be configurable
    user = await User.get(id=callback_query.from_user.id).prefetch_related("fikas")
    if user.fikas:
        await callback_query.answer("You have already signed up for random fika")
        return
    await state.set_state(RandomFika.participating)
    await dp.bot.send_message(
        user.id,
        "Please send us info on how you want to be contacted (email, telegram, linkedin, etc.) "
        "and we will send you a message at 11:00 with the name of the person you will have fika with",
    )


@dp.message(RandomFika.participating)  # type: ignore; noqa: F712
async def handle_random_fika_participating(message: types.Message, state: FSMContext) -> None:

    user = await User.get(id=message.from_user.id).prefetch_related("fikas")

    await Fika.create(user=user, contact=message.text)
    # TODO this not very usable, change it. Message is at the top right now
    await dp.bot.send_message(
        user.id,
        "You have been added to the list of people who want to participate in random fika. "
        "At 11:00 we will send you a message with the name of the person you will have fika with",
    )


@dp.callback_query(FikaCallback.filter(F.is_participating == False))  # type: ignore, noqa: E712
async def handle_random_fika_no(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        "You have been removed from the list of people who want to participate in random fika. "
    )
    user = await User.get(id=callback_query.from_user.id).prefetch_related("fikas")
    if not user.fikas:
        await callback_query.answer("You already not participating in random fika")
        return
    await Fika.filter(user=user).delete()
    await dp.bot.send_message(
        user.id, "You have been removed from the list of people who want to participate in random fika. "
    )


@dp.message(Command("cancel"))  # type: ignore
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=DEFAULT_KEYBOAD,
    )


# Admin commands
@dp.message(Command("admin"))  # type: ignore
async def admin(message: types.Message, command: CommandObject) -> None:
    if command.args and command.args == ADMIN_PASSWORD:
        user = User(id=message.from_user.id, is_admin=True, name=message.from_user.full_name)
        await user.save()
        await message.answer("You are now logged in as admin")

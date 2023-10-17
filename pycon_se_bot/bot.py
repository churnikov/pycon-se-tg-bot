import logging

from aiogram import F, types
from aiogram.filters import CommandStart
from aiogram.filters.command import Command, CommandObject
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from pycon_se_bot.models import Talk, User
from pycon_se_bot.settings import ADMIN_PASSWORD, dp


DEFAULT_KEYBOAD = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Schedule"),
                ],
            [
                KeyboardButton(text="Random fika (coffee)")
                ],
            ],
        is_persistent=True)


# States
class Form(StatesGroup):
    schedule = State()
    schedule_day_1 = State()
    schedule_day_2 = State()
    fandom_fika = State()


@dp.message(CommandStart())  # type: ignore
async def start(message: types.Message) -> None:
    # Sending a message with the keyboard
    await message.answer("Hello! I'm your bot, choose an option:", reply_markup=DEFAULT_KEYBOAD)


# Handler for messages (it will handle messages containing "Button 1", "Button 2", "Button 3")


@dp.message(F.text == "Schedule")  # type: ignore
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
        is_persistent=True)
    await message.answer("Which day's schedule would you like to see?", reply_markup=keyboard)


async def get_talks(day: int) -> list[Talk]:
    talks = await Talk.filter(day=day).order_by("time_start").all()
    return talks


@dp.message(F.text.regexp("Day \d+"))  # type: ignore
async def handle_schedule_for_day(message: types.Message, state: FSMContext) -> None:
    day = message.text.split(" ")
    if len(day) != 2:
        await message.answer("Please choose a day")
        return

    day = day[1]
    if day == "1":
        await state.set_state(Form.schedule_day_1)
        talks = await get_talks(1)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"{talk.name} ({talk.time_start} - {talk.time_end})",
                                         callback_data=f"talk_{talk.id}"),
                    ] for talk in talks
                ],
            )
        await message.answer("Here's the schedule for day 1", reply_markup=keyboard)
    elif day == "2":
        await state.set_state(Form.schedule_day_2)
        await message.answer("Here's the schedule for day 2")
    else:
        await message.answer("Please choose a day")


@dp.message(F.text == "Home")  # type: ignore
async def handle_schedule_back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer("Back to home", reply_markup=DEFAULT_KEYBOAD)


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

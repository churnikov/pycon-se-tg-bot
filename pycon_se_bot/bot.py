from aiogram import F, types
from aiogram.filters import CommandStart
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from pycon_se_bot.models import Talk
from pycon_se_bot.settings import dp


@dp.message(CommandStart())  # type: ignore
async def start(message: types.Message) -> None:
    # Creating buttons
    button_1 = KeyboardButton(text="See schedule")
    button_2 = KeyboardButton(text="Random fika (coffee)")
    button_3 = KeyboardButton(text="Button 3")

    # Creating a keyboard
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2, button_3]], is_persistent=True)

    # Sending a message with the keyboard
    await message.answer("Hello! I'm your bot, choose an option:", reply_markup=keyboard)


# Handler for messages (it will handle messages containing "Button 1", "Button 2", "Button 3")


@dp.message(F.text == "See schedule")  # type: ignore
async def handle_schedule_lookup(message: types.Message) -> None:
    talks = await Talk.all()
    talks = [talk.name for talk in talks]
    await message.answer(str(talks))


@dp.message(F.text.in_({"See schedule", "Button 2", "Button 3"}))  # type: ignore
async def handle_button_click(message: types.Message) -> None:
    # Respond to the user's button click
    await message.answer(f"You clicked {message.text}!")
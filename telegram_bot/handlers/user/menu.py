from aiogram.handlers.callback_query import CallbackQuery
from aiogram.types import Message, ErrorEvent
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router
from typing import Union
from aiogram import F

from telegram_bot.keyboards import menu_keyboard, return_keyboard, add_back_button

router = Router()


@router.callback_query(F.data == "menu")
async def catch_menu_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await menu(callback.message, state)


@router.message(Command(commands=["menu", "start"]))
async def catch_menu_command(message: Message, state: FSMContext):
    await message.delete()
    await menu(message, state)


async def menu(message: Message, state: FSMContext):
    keyboard = await menu_keyboard()
    if message.from_user.is_bot:
        await message.edit_text(text="Меню", reply_markup=keyboard.as_markup())
    else:
        await message.answer(text="Меню", reply_markup=keyboard.as_markup())
    await state.clear()


# @router.error()
# async def catch_error(error_event: ErrorEvent):
#     await exception_occurred(repr(error_event.exception), error_event.update.message)


async def exception_occurred(text: str = "", message: Message = None):
    if text:
        text = f"Возникло исключение:\n<code>{text}</code>"
    else:
        text = f"Возникло исключение"

    keyboard = await return_keyboard()
    if message:
        await message.answer(text=text, reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)
    else:
        pass
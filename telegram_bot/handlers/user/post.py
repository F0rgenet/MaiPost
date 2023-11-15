from typing import Union
import textwrap

from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from aiogram.handlers.callback_query import CallbackQuery

from telegram_bot.utils.states import CreatePost
from telegram_bot.utils.callbacks import TagCallback
from telegram_bot.keyboards import *

from .menu import exception_occurred

router = Router()


async def get_tags_string(post_tags: list[str]) -> str:
    tags_string = " ".join([rf"\[`{tag.replace(' ', '◾️')}`\]" for tag in post_tags])
    tags_string = textwrap.fill(tags_string, width=40).replace("◾️", " ")
    return tags_string


async def update_menu(state: FSMContext, keyboard: InlineKeyboardBuilder, message: Message = None):
    post_message = await get_state_data(state, "post_message")
    if not post_message:
        if not message:
            await exception_occurred("Сообщение не найдено")
        post_message = message
    post_title = await get_state_data(state, "post_title")
    if not post_title: post_title = "-"
    post_data = await get_state_data(state, "post_data")
    if not post_data: post_data = "-"
    post_tags = await get_state_data(state, "post_tags")
    if not post_tags: post_tags = []

    states = ["CreatePost:title", "CreatePost:data", "CreatePost:tags", "CreatePost:attachments", "CreatePost:publish"]
    state_level = states.index(await state.get_state())

    lines = [
        f"*Заголовок*: \"`{post_title}`\"\n",
        f"*Информация*:\n```txt\n{post_data}```\n",
        f"Выбранные *теги*:\n{await get_tags_string(post_tags)}",
        f"Прикреплённые *файлы*:\n",
        ""
    ]
    edit_lines = [
        "Введите *заголовок*",
        "Отправьте сообщение с *информацией*",
        "Выберите *теги*" if not post_tags else f"Выбранные *теги*:\n{await get_tags_string(post_tags)}",
        "Прикрепите *файлы*",
        "Вы действительно желаете опубликовать этот пост?"
    ]
    text = "\n".join(lines[:state_level] + [edit_lines[state_level]])
    message = await post_message.edit_text(text, reply_markup=keyboard.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)
    return message


@router.callback_query(F.data == "create_post")
async def catch_create_post(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CreatePost.title)
    await title_menu(state, callback.message)


async def title_menu(state: FSMContext, menu_message: Union[Message, None] = None):
    keyboard = await skip_keyboard("enable_data_menu")
    keyboard = await add_back_button(keyboard, "menu")

    message = await update_menu(state, keyboard, menu_message)

    await state.update_data(post_message=message)


@router.message(CreatePost.title)
async def catch_title(message: Message, state: FSMContext):
    title = message.text
    await message.delete()
    await state.update_data(post_title=title)
    await state.set_state(CreatePost.data)
    await data_menu(state)


@router.callback_query(F.data == "enable_data_menu")
async def enable_data_menu(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if "post_tags" in state_data:
        await state.update_data(post_tags=[])
    await callback.answer()
    await state.set_state(CreatePost.data)
    await data_menu(state)


async def data_menu(state: FSMContext):
    keyboard = await skip_keyboard("enable_tags_menu")
    keyboard = await add_back_button(keyboard, "create_post")

    await update_menu(state, keyboard)


@router.message(CreatePost.data)
async def catch_data(message: Message, state: FSMContext):
    data = message.text
    await message.delete()
    await state.update_data(post_data=data)
    await state.set_state(CreatePost.tags)
    await tags_menu(state)


@router.callback_query(F.data == "enable_tags_menu")
async def enable_tags_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreatePost.tags)
    await tags_menu(state)


async def tags_menu(state: FSMContext):
    post_tags = await get_state_data(state, "post_tags") or []
    tags = ["Инженерная графика", "Математический анализ",
            "Линейная алгебра", "Дискретная математика",
            "ОРГ", "Информатика", "ВвАРКТ",
            "Английский язык", "Философия"]

    tags_keyboard = await generate_tags_keyboard(tags, post_tags)
    keyboard = await add_back_button(tags_keyboard, "enable_data_menu", False, True)
    keyboard.add(InlineKeyboardButton(text="Продолжить", callback_data="enable_attachments_menu"))

    await update_menu(state, keyboard)


@router.callback_query(TagCallback.filter())
async def add_tag(callback: CallbackQuery, state: FSMContext, callback_data: TagCallback):
    state_data = await state.get_data()
    if "post_tags" in state_data:
        tags = state_data["post_tags"]
        if callback_data.enable:
            tags.append(callback_data.tag)
        else:
            tags.remove(callback_data.tag)
        await state.update_data(post_tags=tags)
    else:
        await state.update_data(post_tags=[callback_data.tag])
    await callback.answer()
    await tags_menu(state)


@router.callback_query(F.data == "enable_attachments_menu")
async def enable_attachments_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreatePost.attachments)
    await attachments_menu(state)


async def attachments_menu(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard = await add_back_button(keyboard, "enable_tags_menu")
    keyboard.add(InlineKeyboardButton(text="Продолжить", callback_data="enable_publish_menu"))

    await update_menu(state, keyboard)


@router.message(CreatePost.attachments)
async def catch_attachments(message: Message, state: FSMContext):
    photos = message.photo
    await message.delete()
    if photos:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Открепить", callback_data="post_detach_file"))
        message = await message.answer_photo(photo=photos[-1].file_id,
                                             caption="Прикреплённое", reply_markup=keyboard.as_markup())
        file_id = message.photo[-1].file_id
        post_photos = await get_state_data(state, "post_photos")
        if not post_photos: await state.update_data(post_photos=[file_id])
        else: await state.update_data(post_photos=post_photos + [file_id])


@router.callback_query(F.data == "post_detach_file")
async def catch_detachments(callback: CallbackQuery, state: FSMContext):
    photos = await get_state_data(state, "post_photos")
    photos.remove(callback.message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await callback.message.delete()
    print(await get_state_data(state, "post_photos"))


@router.callback_query(F.data == "enable_publish_menu")
async def enable_publish_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreatePost.publish)
    await publish_menu(state)


async def publish_menu(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard = await add_back_button(keyboard, "enable_attachments_menu")
    keyboard.add(InlineKeyboardButton(text="Опубликовать", callback_data="publish"))

    await update_menu(state, keyboard)


async def get_state_data(state: FSMContext, key: str):
    data = await state.get_data()
    if key in data:
        return data[key]
    else:
        return None

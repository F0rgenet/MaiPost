from typing import Union
import textwrap

from aiogram import F
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, IS_ADMIN
from aiogram.filters.chat_member_updated import ChatMemberUpdated
from aiogram import Router
from aiogram.types import Message, ForumTopic
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from aiogram.handlers.callback_query import CallbackQuery

from telegram_bot.utils.states import CreatePost
from telegram_bot.utils.callbacks import TagCallback
from telegram_bot.keyboards import *
from aiogram.methods.base import TelegramMethod
from aiogram.types import ForumTopic, Chat, User


router = Router()


class GetForumTopics(TelegramMethod[list[ForumTopic]]):
    __returning__ = list[ForumTopic]
    __api_method__ = "channels.getForumTopics"

    channel: Chat


@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    chat = event.chat

    if chat.is_forum:
        print(await event.from_user.bot(GetForumTopics(channel=chat)))
    print("join", event.chat)


@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_ADMIN))
async def on_user_join(event: ChatMemberUpdated):
    print("admin", event.chat.id)
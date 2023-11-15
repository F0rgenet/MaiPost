from aiogram.filters.callback_data import CallbackData
from typing import Callable


class TagCallback(CallbackData, prefix="tag"):
    tag: str
    enable: bool

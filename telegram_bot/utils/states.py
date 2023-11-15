from aiogram.fsm.state import StatesGroup, State


class CreatePost(StatesGroup):
	title = State()
	data = State()
	tags = State()
	attachments = State()
	publish = State()

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from telegram_bot.utils.callbacks import TagCallback


async def menu_keyboard(is_admin: bool = False) -> InlineKeyboardBuilder:
	builder = InlineKeyboardBuilder()
	builder.row(
		InlineKeyboardButton(text="Создать пост", callback_data="create_post"),
	)
	if is_admin:
		builder.add(InlineKeyboardButton(text="Админ панель", callback_data="admin_menu"))
	return builder


async def generate_tags_keyboard(tags: list, enabled_tags: list) -> InlineKeyboardBuilder:
	builder = InlineKeyboardBuilder()
	for tag in tags:
		enabled = tag in enabled_tags
		callback_data = TagCallback(tag=tag, enable=not enabled).pack()
		if enabled:
			text = f"[✅]{tag}"
		else:
			text = f"[❌]{tag}"
		builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
	builder.adjust(3)
	return builder


async def skip_keyboard(callback: str) -> InlineKeyboardBuilder:
	builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Пропустить", callback_data=callback))
	return builder


async def add_back_button(builder: InlineKeyboardBuilder, callback: str, to_start: bool = True, separate_row: bool = False) -> InlineKeyboardBuilder:
	back_button = InlineKeyboardButton(text="Назад", callback_data=callback)
	if to_start:
		new_builder = InlineKeyboardBuilder()
		if separate_row:
			new_builder.add(back_button)
			new_builder.attach(builder)
		else:
			new_builder.add(back_button)
			for button in builder.buttons:
				new_builder.add(button)
	else:
		new_builder = builder
		if separate_row:
			new_builder.row(back_button)
		else:
			new_builder.add(back_button)
	return new_builder


async def back_keyboard(callback: str) -> InlineKeyboardBuilder:
	builder = InlineKeyboardBuilder()
	return await add_back_button(builder, callback)


async def return_keyboard() -> InlineKeyboardBuilder:
	builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Вернуться", callback_data="menu"))
	return builder

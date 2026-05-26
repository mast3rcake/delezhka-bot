from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🆕 Новая делёжка"),
                KeyboardButton(text="👥 Участники"),
            ],
            [
                KeyboardButton(text="💸 Добавить расход"),
                KeyboardButton(text="📋 Расходы"),
            ],
            [
                KeyboardButton(text="🧮 Итог"),
                KeyboardButton(text="🗑 Очистить"),
            ],
        ],
        resize_keyboard=True,
    )
